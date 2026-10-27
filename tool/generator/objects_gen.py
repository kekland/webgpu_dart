from dataclasses import dataclass
from typing import Optional

import _state as state
from types_gen import *
from functions_gen import *
from utils import *


@dataclass
class ObjectDecl:
  name: str
  methods: list[FunctionDecl]
  tags: set[str]

  @property
  def dart_name(self) -> str: return to_dart_top_level_name(self.name)

  @property
  def c_name(self) -> str: return f'bindings.WGPU{to_dart_top_level_name(self.name)}'

  @property
  def c_release_raw_name(self) -> str: return f'wgpu{self.dart_name}Release'


def parse_object_methods(name: str, decl: dict) -> list[FunctionDecl]:
  if 'methods' not in decl: return []
  methods = [parse_function_decl(m) for m in decl['methods']]

  obj_ptr = Type(kind=TypeKind.OBJECT, ref_name=name)
  for m in methods:
    m.args.insert(0, FunctionArgDecl(name=name, type=obj_ptr, tags=set()))

  return methods


def parse_object_decl(name: str) -> ObjectDecl:
  decl = state.spec[name]
  methods = parse_object_methods(name, decl)
  tags = set(decl.get('tags', []))

  return ObjectDecl(name=name, methods=methods, tags=tags)


def generate_object_code(obj: ObjectDecl, skip_methods: list[str]) -> tuple[list[str], list[str]]:
  impl_code: list[str] = []

  base_name = f'_{obj.dart_name}Base'

  impl_code.append(f'class {base_name} extends _Opaque<{obj.c_name}Impl> {{')
  impl_code.append(f'  {base_name}._(super.ptr): super._();')
  impl_code.append(f'  {base_name}._borrowed(super.ptr): super._borrowed();')
  impl_code.append(f'')
  impl_code.append(f'  @override')
  impl_code.append(f'  ffi.NativeFinalizer get _finalizer => __finalizer;')
  impl_code.append(f'  static final __finalizer = ffi.NativeFinalizer(bindings.addresses.{obj.c_release_raw_name}.cast());')
  impl_code.append(f'')
  impl_code.append(f'  @override')
  impl_code.append(f'  void dispose() => _dispose(bindings.{obj.c_release_raw_name});')

  # private methods for internal use
  impl_code.append(f'')

  for m in obj.methods:
    if m.name in skip_methods: continue
    method_c_name = f'bindings.wgpu{obj.dart_name}{to_dart_top_level_name(m.name)}'
    method_dart_name = f'_{m.dart_name}'

    obj_method = replace(m)
    obj_method.args.pop(0)

    overrides = GeneratedFuncOverrides(c_name_override=method_c_name, dart_name_override=method_dart_name, injected_first_arg='_ptr')
    impl_code.extend(indent(generate_function_code(obj_method, overrides)))
    impl_code.append(f'')

  if impl_code[-1] == '': impl_code.pop()
  impl_code.append(f'}}')
  impl_code.append(f'')

  is_native_only = 'dawn' in obj.tags or 'native' in obj.tags

  if is_native_only:
    impl_code.append(f'ffi.Pointer<{obj.c_name}Impl> _{obj.dart_name}$ToPointer({obj.dart_name} obj) => obj._ptr;')
  else:
    impl_code.append(f'ffi.Pointer<{obj.c_name}Impl> _{obj.dart_name}$ToPointer(webgpu.{obj.dart_name} obj) => (obj as {obj.dart_name})._ptr;')
  impl_code.append(f'{obj.dart_name} _{obj.dart_name}$FromPointer(ffi.Pointer<{obj.c_name}Impl> ptr, {{bool borrowed = false}}) => borrowed? ._borrowed(ptr) : ._(ptr);')
  impl_code.append(f'')

  return [], impl_code
