from dataclasses import dataclass
from typing import Optional

import _state as state
from types_gen import *
from functions_gen import *
from structs_gen import *
from utils import *


@dataclass
class CallbackDecl:
  name: str
  args: list[FunctionArgDecl]
  returns: Type
  tags: set[str]

  @property
  def dart_name(self): return f'{to_dart_top_level_name(self.name)}'

  @property
  def c_name(self): return f'bindings.WGPU{to_dart_top_level_name(self.name)}'

  @property
  def trampoline_name(self): return f'_{self.dart_name}$Trampoline'

  @property
  def registry_name(self): return f'_{self.dart_name}$Registry'


def parse_callback_decl(name: str) -> CallbackDecl:
  decl = state.spec[name]
  args = parse_function_args(decl)
  returns = parse_function_returns(decl)
  tags = set(decl.get('tags', []))
  return CallbackDecl(name=name, args=args, returns=returns, tags=tags)


def generate_callback_code(callback: CallbackDecl) -> tuple[list[str], list[str]]:
  code = []
  impl = []

  # resolve dart typedef
  dart_args = generate_function_arg_list(callback.args)
  dart_returns = callback.returns.resolve_dart_type()
  code.append(f'typedef {callback.dart_name} = {dart_returns} Function({dart_args});')
  impl.append(f'typedef _{callback.dart_name} = {dart_returns} Function({dart_args});')

  # resolve c typedef
  userdata1 = FunctionArgDecl(name='userdata1', type=Type(TypeKind.VOID, pointer=1), tags=set())
  userdata2 = FunctionArgDecl(name='userdata2', type=Type(TypeKind.VOID, pointer=1), tags=set())
  c_args = generate_function_c_arg_list(callback.args + [userdata1, userdata2])
  impl.append(f'')

  # trampoline
  impl.append(f'{dart_returns} {callback.trampoline_name}({c_args}) {{')
  impl.extend(indent(generate_function_inverse_arg_marshalling(callback.args)))
  impl.append(f'  final handle = {callback.registry_name}.instance.take(userdata1);')

  if callback.returns.is_void:
    impl.append(f'  if (handle == null) return;')
    impl.append(f'  handle({generate_inverse_function_call_args(callback.args)});')
  else:
    impl.append(f'  if (handle == null) throw Exception("handle is null");')
    impl.append(f'  return handle({generate_inverse_function_call_args(callback.args)});')
  impl.append(f'}}')
  impl.append(f'')

  # registry
  bindings_name = f'bindings.WGPU{callback.dart_name}Function'
  native_fn = f'ffi.NativeFunction<{bindings_name}>'
  native_callable = f'ffi.NativeCallable<{bindings_name}>'
  impl.append(f'final class {callback.registry_name} extends _CallbackRegistry<_{callback.dart_name}, {native_fn}> {{')
  impl.append(f'  static final instance = {callback.registry_name}();')
  impl.append(f'')
  impl.append(f'  @override')
  impl.append(f'  ffi.Pointer<{native_fn}> get nativeFunction => _callable.nativeFunction;')

  if callback.returns.is_void:
    impl.append(f'  final {native_callable} _callable = .isolateLocal({callback.trampoline_name});')
  else:
    impl.append(f'  final {native_callable} _callable = .isolateLocal({callback.trampoline_name}, exceptionalReturn: {callback.returns.resolve_zero_value()});')

  impl.append(f'}}')
  impl.append(f'')

  # callback info to native
  cb_info_name = f'{callback.name} info'
  cb_info_decl = state.spec[cb_info_name]
  cb_info_members = parse_struct_members(cb_info_decl)
  has_mode = any(member.name == 'mode' for member in cb_info_members)
  cb_info_c_name = f'WGPU{to_dart_top_level_name(cb_info_name)}'

  impl.append(f'ffi.Pointer<bindings.{cb_info_c_name}> _{callback.dart_name}$Register(ffi.Allocator allocator, {callback.dart_name}? callback) {{')
  if has_mode:
    impl.append(f'  final info = allocator<bindings.{cb_info_c_name}>();')
    impl.append(f'  if (callback == null) return info;')
    impl.append(f'  final handle = {callback.registry_name}.instance.register(callback, false);')
    impl.append(f'  return _{callback.dart_name}$ToInfo(allocator, handle);')
  else:
    impl.append(f'  return _{callback.dart_name}$ToInfoRepeating(allocator, callback);')
  impl.append(f'}}')
  impl.append(f'')

  # if has mode, then the callback is a one-off (e.g. a future)
  if has_mode: 
    impl.append(f'ffi.Pointer<bindings.{cb_info_c_name}> _{callback.dart_name}$ToInfo(ffi.Allocator allocator, _CallbackHandle handle, {{CallbackMode mode = .allowProcessEvents}}) {{')
    impl.append(f'  final info = allocator<bindings.{cb_info_c_name}>();')
    impl.append(f'  info.ref.mode = mode.value;')
    impl.append(f'  info.ref.callback = {callback.registry_name}.instance.nativeFunction;')
    impl.append(f'  info.ref.userdata1 = .fromAddress(handle.id);')
    impl.append(f'  info.ref.userdata2 = ffi.nullptr;')
    impl.append(f'  info.ref.nextInChain = ffi.nullptr;')
    impl.append(f'  return info;')
    impl.append(f'}}')

  # otherwise, it's a repeating callback. create handle manually for tracking
  else:
    impl.append(f'ffi.Pointer<bindings.{cb_info_c_name}> _{callback.dart_name}$ToInfoRepeating(ffi.Allocator allocator, {callback.dart_name}? callback) {{')
    impl.append(f'  final info = allocator<bindings.{cb_info_c_name}>();')
    impl.append(f'  if (callback == null) return info;')
    impl.append(f'  final handle = {callback.registry_name}.instance.register(callback, true);')
    impl.append(f'  _usingCallbackHandles.add(handle);')
    impl.append(f'  info.ref.callback = {callback.registry_name}.instance.nativeFunction;')
    impl.append(f'  info.ref.userdata1 = .fromAddress(handle.id);')
    impl.append(f'  info.ref.userdata2 = ffi.nullptr;')
    impl.append(f'  info.ref.nextInChain = ffi.nullptr;')
    impl.append(f'  return info;')
    impl.append(f'}}')


  is_native = 'native' in callback.tags or 'dawn' in callback.tags
  if is_native:
    impl = code + impl
    code = []

  return code, impl
