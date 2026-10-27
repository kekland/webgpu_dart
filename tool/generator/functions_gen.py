from dataclasses import dataclass, replace
from typing import Optional
from enum import Enum, auto

import _state as state
from structs_gen import *
from types_gen import *
from utils import *


@dataclass
class FunctionArgDecl:
  name: str
  type: Type
  tags: set[str]
  array_length_of: Optional[str] = None

  @property
  def dart_name(self): return to_dart_member_name(self.name)

  @property
  def c_name(self): return f'_{self.dart_name}'

  @property
  def dart_type(self): return self.type.resolve_dart_type()

  @property
  def c_type(self): return self.type.resolve_c_type()

  @property
  def fn_c_type(self): return self.type.resolve_fn_c_type()


@dataclass
class FunctionDecl:
  name: str
  returns: Type
  args: list[FunctionArgDecl]
  tags: set[str]
  owner: Optional[str] = None
  _dart_name_override: Optional[str] = None
  _c_name_override: Optional[str] = None
  _injected_first_arg: Optional[str] = None

  @property
  def dart_name(self): return self._dart_name_override or to_dart_member_name(self.name)

  @property
  def c_name(self): return self._c_name_override or f'bindings.wgpu{to_dart_top_level_name(self.name)}'

  @property
  def callback(self) -> Optional[FunctionArgDecl]:
    for arg in self.args:
      if arg.type.is_callback: return arg
    return None


def parse_function_arg_decl(decl: dict) -> FunctionArgDecl:
  name = decl['name']
  type = parse_type(decl)
  tags = set(decl.get('tags', []))
  return FunctionArgDecl(name=name, type=type, tags=tags)


def parse_function_args(decl: dict) -> list[FunctionArgDecl]:
  args = [parse_function_arg_decl(arg) for arg in decl.get('args', [])]
  args_by_name = {arg.name: arg for arg in args}

  for arg in args:
    if arg.type.is_array and arg.type.array_length_has_field:
      print(arg.type.array_length)
      args_by_name[arg.type.array_length].array_length_of = arg.name

  return args


def parse_function_returns(decl: dict) -> Type:
  if 'returns' in decl:
    if isinstance(decl['returns'], dict): return parse_type(decl['returns'])
    return parse_type({'type': decl['returns']})
  return Type(kind=TypeKind.VOID)


def parse_function_decl(decl: dict, name: Optional[str] = None, owner: Optional[str] = None):
  _name = decl['name'] if name is None else name
  args = parse_function_args(decl)
  returns = parse_function_returns(decl)
  tags = set(decl.get('tags', []))
  return FunctionDecl(name=_name, returns=returns, args=args, tags=tags, owner=owner)


@dataclass
class GeneratedFuncOverrides:
  dart_name_override: Optional[str] = None
  c_name_override: Optional[str] = None
  injected_first_arg: Optional[str] = None


class FunctionShape(Enum):
  ASYNC = auto() # takes a callback
  STATUS_OUT_PARAM = auto() # returns a status and has an out param
  VOID_OUT_PARAM = auto() # has an out param
  SIZE_OUT_PARAM = auto() # returns a size and has an array out param
  SYNC = auto() # default


def classify_function_shape(func: FunctionDecl) -> FunctionShape:
  if func.callback: return FunctionShape.ASYNC

  last_arg = func.args[-1] if func.args else None
  if not last_arg: return FunctionShape.SYNC

  has_outparam = (
    last_arg.type.is_struct and
    last_arg.type.is_pointer and
    last_arg.type.pointer_kind == PointerKind.MUTABLE
  )

  if has_outparam:
    if func.returns.is_void: return FunctionShape.VOID_OUT_PARAM
    if func.returns.is_enum and func.returns.enum_decl.name.endswith('status'): return FunctionShape.STATUS_OUT_PARAM

  if last_arg.type.is_array and func.returns.kind == TypeKind.USIZE: return FunctionShape.SIZE_OUT_PARAM
  return FunctionShape.SYNC


def generate_function_arg_list(args: list[Union[str, FunctionArgDecl]]) -> str:
  out: list[str] = []
  for arg in args:
    if isinstance(arg, str):
      out.append(arg)
      continue

    if arg.array_length_of: continue
    out.append(f'{arg.dart_type} {arg.dart_name}')
  return ', '.join(out)


def generate_function_c_arg_list(args: list[FunctionArgDecl]) -> str:
  out: list[str] = []
  for arg in args:
    out.append(f'{arg.fn_c_type} {arg.dart_name}')
  return ', '.join(out)


def generate_function_arg_marshalling(args: list[FunctionArgDecl]) -> list[str]:
  impl: list[str] = []

  for arg in args:
    if arg.array_length_of: continue

    length_field = None
    if arg.type.is_array and arg.type.array_length_has_field:
      array_length_field_arg = next(a for a in args if a.array_length_of == arg.name)
      length_field = array_length_field_arg.c_name
      impl.append(f'final int {length_field};')

    setter = arg.type.resolve_set_native(arg.c_name, arg.dart_name, array_count_field=length_field)
    if len(setter) == 1: impl.append(f'final {setter[0]}')
    else:
      impl.append(f'final {arg.type.resolve_c_type()} {arg.c_name};')
      impl.extend(setter)

  return impl


def generate_function_inverse_arg_marshalling(args: list[FunctionArgDecl]) -> list[str]:
  impl: list[str] = []

  for arg in args:
    if arg.array_length_of: continue

    getter = arg.type.resolve_set_dart(arg.c_name, arg.dart_name)
    impl.extend(getter)

  return impl


def generate_function_call_args(args: list[FunctionArgDecl], injected_first_arg: Optional[str] = None, injected_last_arg: Optional[str] = None) -> str:
  call_args: list[str] = []
  if injected_first_arg: call_args.append(injected_first_arg)

  for arg in args:
    if arg.type.is_pointer:
      call_args.append(f'{arg.c_name}.cast()')
    else:
      call_args.append(arg.c_name)

  if injected_last_arg: call_args.append(injected_last_arg)
  return ', '.join(call_args)


def generate_inverse_function_call_args(args: list[FunctionArgDecl]) -> str:
  call_args: list[str] = []
  for arg in args:
    if arg.array_length_of: continue
    call_args.append(arg.c_name)
  return ', '.join(call_args)


def generate_function_signature(func: FunctionDecl, returns: Optional[Union[str, Type]] = None, args: Optional[list[Union[str, FunctionArgDecl]]] = None, name: Optional[str] = None) -> str:
  _returns = func.returns.resolve_dart_type()
  if returns:
    if isinstance(returns, str): _returns = returns
    else: _returns = returns.resolve_dart_type()

  _args = func.args
  if args is not None: _args = args

  return f'{_returns} {name or func.dart_name}({generate_function_arg_list(_args)})'


def _generate_sync_function_code(func: FunctionDecl) -> list[str]:
  impl: list[str] = []
  func_signature = generate_function_signature(func)

  impl.append(f'{func_signature} => _using((allocator) {{')
  impl.extend(indent(generate_function_arg_marshalling(func.args)))

  call_args = generate_function_call_args(func.args, func._injected_first_arg)
  if not func.returns.is_pure_void:
    impl.append(f'  final result = {func.c_name}({call_args});')
    impl.append(f'  return {func.returns.resolve_from_native("result")};')
  else:
    impl.append(f'  {func.c_name}({call_args});')
  impl.append(f'}});')
  return impl


def _generate_out_param_function_code(func: FunctionDecl) -> list[str]:
  shape = classify_function_shape(func)

  impl: list[str] = []
  func_out = func.args[-1]
  in_args = func.args[:-1]
  returns = func_out.type

  is_return_struct = func_out.type.is_struct
  is_return_struct_extensible = func_out.type.is_struct and func_out.type.struct_decl.extensible == Extensible.OUT
  is_return_struct_free_members = func_out.type.is_struct and func_out.type.struct_decl.needs_free_members

  func_signature = generate_function_signature(func, returns=returns, args=in_args)
  if is_return_struct_extensible:
    func_signature = func_signature[:-1]
    if func_signature.endswith('('): func_signature += '{List<SType> extensions = const []})'
    else: func_signature += ', {List<SType> extensions = const []})'

  impl.append(f'{func_signature} => _using((allocator) {{')
  impl.append(f'  final outPtr = allocator<{func_out.type.resolve_allocator_type()}>();')

  if is_return_struct_extensible:
    impl.append(f'  outPtr.ref.nextInChain = _ChainedStruct$FromExtensionList(allocator, extensions).cast();')

  impl.extend(indent(generate_function_arg_marshalling(in_args)))
  call_args = generate_function_call_args(in_args, injected_first_arg=func._injected_first_arg, injected_last_arg='outPtr')
  call_expr = f'{func.c_name}({call_args})'

  if shape == FunctionShape.STATUS_OUT_PARAM:
    impl.append(f'  final statusValue = {call_expr};')
    impl.append(f'  final status = {func.returns.resolve_from_native("statusValue")};')
    impl.append(f'  if (statusValue != 1) throw Exception("{func.c_name.split("bindings.")[1]} failed: ${{status.name}}");')

  elif shape == FunctionShape.SIZE_OUT_PARAM:
    impl.append(f'  // todo: handle SIZE_OUT_PARAM')
    impl.append(f'  final sizeValue = {call_expr};')
  else:
    impl.append(f'  {call_expr};')

  impl.append(f'  final result = {func_out.type.resolve_from_native("outPtr", borrowed=is_return_struct_free_members)};')

  if is_return_struct_free_members:
    impl.append(f'  bindings.wgpu{func_out.type.dart_name}FreeMembers(outPtr.ref);')

  impl.append(f'  return result;')

  impl.append(f'}});')

  return impl


def generate_async_function_code(func: FunctionDecl) -> list[str]:
  impl: list[str] = []
  callback_arg = func.args[-1]
  func_args = func.args[:-1]

  if not callback_arg.type.is_callback: raise Exception(f'functions(async): last argument is not a callback: {func.name}')
  callback = callback_arg.type.callback_decl

  cb_status_arg: Optional[FunctionArgDecl] = None
  cb_result_arg: Optional[FunctionArgDecl] = None
  cb_message_arg: Optional[FunctionArgDecl] = None

  for arg in callback.args:
    type = arg.type
    if type.is_enum and type.ref_name.endswith('status'): cb_status_arg = arg
    elif type.is_string and arg.name == 'message': cb_message_arg = arg
    elif type.is_object or type.is_struct or type.is_enum or type.is_flag: cb_result_arg = arg

  returns = cb_result_arg.type if cb_result_arg else Type(TypeKind.VOID)
  signature = generate_function_signature(func, returns=f'Future<{returns.resolve_dart_type()}>', args=func_args)

  impl.append(f'{signature} {{')

  callback_code: list[str] =[]
  callback_code.append(f'final handle = {callback.registry_name}.instance.register(({generate_function_arg_list(callback.args)}) {{')

  success_handler: str
  if cb_result_arg: success_handler = f'completer.complete({cb_result_arg.dart_name});'
  else: success_handler = f'completer.complete(null);'

  error_handler: str
  if cb_message_arg and cb_status_arg: error_handler = f'completer.completeError(StateError(\'{func.c_name} failed (${{{cb_status_arg.dart_name}.name}}): ${cb_message_arg.dart_name})\'), StackTrace.current);'
  elif cb_message_arg: error_handler = f'completer.completeError(StateError(\'{func.c_name} failed: ${cb_message_arg.dart_name})\'), StackTrace.current);'
  elif cb_status_arg: error_handler = f'completer.completeError(StateError(\'{func.c_name} failed (${{{cb_status_arg.dart_name}.name}})\'), StackTrace.current);'

  if cb_status_arg:
    callback_code.append(f'  if ({cb_status_arg.dart_name} == .success) {{')
    callback_code.append(f'    {success_handler}')
    callback_code.append(f'  }} else {{')
    callback_code.append(f'    {error_handler}')
    callback_code.append(f'  }}')
  else:
    callback_code.append(f'  {success_handler}')

  callback_code.append(f'}}, false);')

  impl.append(f'  final completer = Completer<{returns.resolve_dart_type()}>();')
  impl.extend(indent(callback_code))
  impl.append(f'')

  body: list[str] = []

  body.append(f'_using((allocator) {{')
  body.append(f'  final callbackInfo = _{callback.dart_name}$ToInfo(allocator, handle, mode: .allowProcessEvents);')
  body.extend(indent(generate_function_arg_marshalling(func_args)))
  body.append(f'  return {func.c_name}({generate_function_call_args(func_args, injected_first_arg=func._injected_first_arg, injected_last_arg="callbackInfo.ref")});')
  body.append(f'}});')

  impl.extend(indent(body))
  impl.append(f'  return _EventLoop.waitForAsync(completer);')
  impl.append(f'}}')

  # sync variant
  impl.append(f'')

  sync_name = func.dart_name
  if sync_name.endswith('Async'): sync_name = sync_name[:-5]
  sync_name = f'{sync_name}Sync'

  sync_signature = generate_function_signature(func, returns=f'{returns.resolve_dart_type()}', args=func_args, name=sync_name)
  impl.append(f'{sync_signature} {{')
  impl.append(f'  final completer = _SyncCompleter<{returns.resolve_dart_type()}>();')
  impl.extend(indent(callback_code))
  impl.append(f'')
  impl.extend(indent(body))
  impl.append(f'')
  impl.append(f'  return _EventLoop.waitForSync(completer);')
  impl.append(f'}}')

  return impl


def generate_function_code(func: FunctionDecl, overrides: Optional[GeneratedFuncOverrides] = None) -> list[str]:
  _func = replace(func)
  if overrides:
    _func._dart_name_override = overrides.dart_name_override
    _func._c_name_override = overrides.c_name_override
    _func._injected_first_arg = overrides.injected_first_arg

  shape = classify_function_shape(_func)
  if shape == FunctionShape.SYNC: return _generate_sync_function_code(_func)
  if shape == FunctionShape.SIZE_OUT_PARAM or shape == FunctionShape.STATUS_OUT_PARAM or shape == FunctionShape.VOID_OUT_PARAM: return _generate_out_param_function_code(_func)
  if shape == FunctionShape.ASYNC: return generate_async_function_code(_func)
  else:
    print(f'unsupported function shape: {shape}: {func.name}')
    return []


def generate_global_function_code(func: FunctionDecl) -> tuple[list[str], list[str]]:
  overrides = GeneratedFuncOverrides(dart_name_override=f'_{func.dart_name}')
  return [], generate_function_code(func, overrides)
