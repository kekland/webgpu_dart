from enum import Enum, auto
from dataclasses import dataclass, replace
from typing import Optional

import _state as state
from utils import *


class TypeKind(Enum):
  UNKNOWN = auto()
  VOID = auto()

  VOID_DATA = auto()
  UINT8 = auto()
  UINT16 = auto()
  UINT32 = auto()
  UINT64 = auto()
  INT8 = auto()
  INT16 = auto()
  INT32 = auto()
  INT64 = auto()
  USIZE = auto()
  FLOAT32 = auto()
  FLOAT64 = auto()
  BOOL = auto()
  CHAR = auto()

  STRING = auto()
  FUTURE = auto()

  ENUM = auto()
  FLAG = auto()
  STRUCT = auto()
  OBJECT = auto()
  CALLBACK = auto()
  FUNCTION_PTR = auto()

  ARRAY = auto()


INTEGER_KINDS = (TypeKind.UINT8, TypeKind.UINT16, TypeKind.UINT32, TypeKind.UINT64, TypeKind.INT8, TypeKind.INT16, TypeKind.INT32, TypeKind.INT64, TypeKind.USIZE)
FLOAT_KINDS = (TypeKind.FLOAT32, TypeKind.FLOAT64)


def parse_primitive_type_kind(type_name: str) -> TypeKind:
  if type_name == 'void': return TypeKind.VOID
  elif type_name == 'int': return TypeKind.INT32
  elif type_name == 'uint8_t': return TypeKind.UINT8
  elif type_name == 'uint16_t': return TypeKind.UINT16
  elif type_name == 'uint32_t': return TypeKind.UINT32
  elif type_name == 'uint64_t': return TypeKind.UINT64
  elif type_name == 'int8_t': return TypeKind.INT8
  elif type_name == 'int16_t': return TypeKind.INT16
  elif type_name == 'int32_t': return TypeKind.INT32
  elif type_name == 'int64_t': return TypeKind.INT64
  elif type_name == 'size_t': return TypeKind.USIZE
  elif type_name == 'float': return TypeKind.FLOAT32
  elif type_name == 'double': return TypeKind.FLOAT64
  elif type_name == 'bool': return TypeKind.BOOL
  elif type_name == 'char': return TypeKind.CHAR
  else:
    print(f'unknown primitive type: {type_name}')
    return TypeKind.UNKNOWN


class PointerKind(Enum):
  MUTABLE = auto()
  IMMUTABLE = auto()


@dataclass
class Type:
  kind: TypeKind
  ref_name: Optional[str] = None
  array_inner: Optional["Type"] = None
  array_length: Optional[str | int] = None
  is_nullable: bool = False
  default: Optional[str] = None
  pointer: int = 0
  pointer_kind: Optional[PointerKind] = None
  callback_info_name: Optional[str] = None

  @property
  def is_primitive(self) -> bool: return self.is_numeric or self.is_bool or self.is_string or self.is_char

  @property
  def is_void(self) -> bool: return self.kind == TypeKind.VOID
  
  @property
  def is_pure_void(self) -> bool: return self.is_void and not self.is_pointer

  @property
  def is_void_data(self) -> bool: return self.kind == TypeKind.VOID_DATA

  @property
  def is_integer(self) -> bool: return self.kind in INTEGER_KINDS

  @property
  def is_float(self) -> bool: return self.kind in FLOAT_KINDS

  @property
  def is_numeric(self) -> bool: return self.is_integer or self.is_float

  @property
  def is_bool(self) -> bool: return self.kind == TypeKind.BOOL

  @property
  def is_string(self) -> bool: return self.kind == TypeKind.STRING

  @property
  def is_char(self) -> bool: return self.kind == TypeKind.CHAR

  @property
  def is_enum(self) -> bool: return self.kind == TypeKind.ENUM

  @property
  def is_flag(self) -> bool: return self.kind == TypeKind.FLAG

  @property
  def is_struct(self) -> bool: return self.kind == TypeKind.STRUCT

  @property
  def is_future(self) -> bool: return self.kind == TypeKind.FUTURE

  @property
  def is_object(self) -> bool: return self.kind == TypeKind.OBJECT

  @property
  def is_callback(self) -> bool: return self.kind == TypeKind.CALLBACK

  @property
  def is_function_ptr(self) -> bool: return self.kind == TypeKind.FUNCTION_PTR

  @property
  def is_array(self) -> bool: return self.kind == TypeKind.ARRAY

  @property
  def is_pointer(self) -> bool: return self.pointer > 0

  @property
  def is_typed_data_array(self) -> bool: return self.is_array and (self.array_inner.is_numeric or self.array_inner.is_void_data)

  @property
  def enum_decl(self) -> 'EnumDecl': return state.get_enum(self.ref_name)

  @property
  def flag_decl(self) -> 'FlagDecl': return state.get_flag(self.ref_name)

  @property
  def object_decl(self) -> 'ObjectDecl': return state.get_object(self.ref_name)

  @property
  def callback_decl(self) -> 'CallbackDecl': return state.get_callback(self.ref_name)

  @property
  def array_length_is_fixed(self) -> bool: return self.is_array and isinstance(self.array_length, int)

  @property
  def array_length_has_field(self) -> bool: return self.is_array and isinstance(self.array_length, str)

  @property
  def array_length_field(self) -> str:
    if not self.array_length_has_field: raise ValueError(f'array does not have a count field: {self.ref_name}')
    return to_c_member_name(self.array_length)

  @property
  def enum_or_flag_decl(self) -> 'EnumDecl | FlagDecl':
    if self.is_enum: return self.enum_decl
    if self.is_flag: return self.flag_decl
    raise ValueError(f'not an enum or flag: {self.ref_name}')

  @property
  def struct_decl(self) -> 'StructDecl': return state.get_struct(self.ref_name)

  @property
  def dart_name(self):
    if self.is_struct: return self.struct_decl.dart_name
    if self.is_enum: return self.enum_decl.dart_name
    if self.is_flag: return self.flag_decl.dart_name
    if self.is_object: return self.object_decl.dart_name
    if self.is_callback: return self.callback_decl.dart_name
    return self.ref_name

  @property
  def c_name(self):
    if self.is_struct: return self.struct_decl.c_name
    if self.is_enum: return self.enum_decl.c_name
    if self.is_flag: return self.flag_decl.c_name
    if self.is_object: return self.object_decl.c_name
    if self.is_callback: return self.callback_decl.c_name
    return self.ref_name

  def resolve_dart_type(self, nullable: Optional[bool] = None) -> str: return type_to_dart(self, nullable=nullable)
  def resolve_c_type(self) -> str: return type_to_c(self)
  def resolve_fn_c_type(self) -> str: return type_fn_c_type(self)

  def resolve_dart_default(self) -> Optional[str]: return type_dart_default(self)
  def resolve_zero_value(self) -> str: return type_zero_value(self)

  def resolve_from_native(self, expr: str, borrowed: bool = False) -> str: return type_from_native(self, expr, borrowed_field='true' if borrowed else None)
  def resolve_to_native(self, expr: str) -> str: return type_to_native(self, expr)

  def resolve_set_native(self, dest: str, expr: str, default: Optional[str] = None, array_count_field: Optional[str] = None) -> list[str]:
    return type_set_native(self, dest, expr, default=default, array_count_field=array_count_field)

  def resolve_set_dart(self, dest: str, expr: str, borrowed_field: Optional[str] = None) -> list[str]:
    return type_set_dart(self, dest, expr, borrowed_field=borrowed_field)

  def resolve_allocator_type(self) -> str: return type_allocator_type(self)


def parse_type(member: dict) -> Type:
  type_name = member['type']
  entry = state.spec[type_name]
  category = entry['category']

  result: Type = Type(kind=TypeKind.UNKNOWN)

  if category == 'native':
    if type_name == 'void *':
      result.kind = TypeKind.VOID
      result.pointer = 1
      result.pointer_kind = PointerKind.MUTABLE
    elif type_name == 'void const *':
      result.kind = TypeKind.VOID
      result.pointer = 1
      result.pointer_kind = PointerKind.IMMUTABLE
    else:
      result.kind = parse_primitive_type_kind(type_name)
  elif category == 'enum':
    result.kind = TypeKind.ENUM
    result.ref_name = type_name
  elif category == 'bitmask':
    result.kind = TypeKind.FLAG
    result.ref_name = type_name
  elif category == 'structure':
    if type_name == 'string view':
      result.kind = TypeKind.STRING
    elif type_name == 'future':
      result.kind = TypeKind.FUTURE
    else:
      result.kind = TypeKind.STRUCT
    result.ref_name = type_name
  elif category == 'object':
    result.kind = TypeKind.OBJECT
    result.ref_name = type_name
  elif category == 'callback info':
    fn_member = next(m for m in entry['members'] if state.spec[m['type']]['category'] == 'callback function')
    result.kind = TypeKind.CALLBACK
    result.ref_name = fn_member['type']
    result.callback_info_name = type_name
  elif category == 'callback function':
    result.kind = TypeKind.CALLBACK
    result.ref_name = type_name
  elif category == 'function pointer':
    result.kind = TypeKind.FUNCTION_PTR
    result.ref_name = type_name

  annotation = member.get('annotation')
  if annotation:
    result.pointer = annotation.count('*')
    result.pointer_kind = PointerKind.IMMUTABLE if 'const' in annotation else PointerKind.MUTABLE

  if result.kind == TypeKind.UNKNOWN:
    print(f'warning(type): unknown type {type_name}')

  if result.kind == TypeKind.VOID and result.pointer == 0:
    print(f'warning(type): void type without pointer {type_name}')

  if member.get('length') is not None:
    if isinstance(member['length'], str) or member['length'] > 1:
      inner = result
      inner.pointer -= 1
      if inner.is_void: inner.kind = TypeKind.VOID_DATA
      result = Type(kind=TypeKind.ARRAY, array_inner=inner, array_length=member['length'], pointer=1, pointer_kind=inner.pointer_kind)

  if member.get('optional') == True: result.is_nullable = True
  if member.get('default') == 'NAN': result.is_nullable = True
  if member.get('default') == 'nullptr': result.is_nullable = True

  result.default = member.get('default')
  return result


########################################################################################################################
# Dart conversions
########################################################################################################################

def type_dart_default(type: Type) -> Optional[str]:
  d = type.default
  if type.is_bool: return 'true' if d in (True, 'true', 1) else 'false'
  if type.is_string: return "''" if d == '' else repr(str(d)).replace('"', "'")
  if type.is_float:
    value = str(d)
    if value.endswith('f'): value = value[:-1]
    if value.endswith('.'): value += '0'
    return value
  if type.is_integer: return d
  if type.is_flag: return f'.{type.flag_decl.entry(d).dart_name}'
  if type.is_enum: return f'.{type.enum_decl.entry(d).dart_name}'
  if type.is_struct and d == 'zero': return '.zero'
  if d == 'nullptr': return 'ffi.nullptr'
  if d in state.CONSTANTS: return state.get_constant(d).dart_name

  print(f'warning(type): unknown default value {d}')
  return None


def type_to_dart(type: Type, nullable: Optional[bool] = None) -> str:
  kind = type.kind
  nullable = nullable if nullable is not None else type.is_nullable
  _type: str = 'dynamic'

  if type.is_pointer:
    if kind == TypeKind.VOID: _type = 'ffi.Pointer<ffi.Void>'
    if kind == TypeKind.VOID_DATA: _type = 'TypedData'
    if kind == TypeKind.INT8: _type = 'Int8List'
    if kind == TypeKind.UINT8: _type = 'Uint8List'
    if kind == TypeKind.INT16: _type = 'Int16List'
    if kind == TypeKind.UINT16: _type = 'Uint16List'
    if kind == TypeKind.INT32: _type = 'Int32List'
    if kind == TypeKind.UINT32: _type = 'Uint32List'
    if kind == TypeKind.INT64: _type = 'Int64List'
    if kind == TypeKind.UINT64: _type = 'Uint64List'
    if kind == TypeKind.USIZE: _type = 'Uint64List'
    if kind == TypeKind.FLOAT32: _type = 'Float32List'
    if kind == TypeKind.FLOAT64: _type = 'Float64List'
    if kind == TypeKind.CHAR: _type = 'String'
  else:
    if type.is_void: _type = 'void'
    if type.is_bool: _type = 'bool'
    if type.is_string: _type = 'String'
    if type.is_float: _type = 'double'
    if type.is_integer: _type = 'int'

  if type.is_enum: _type = type.dart_name
  if type.is_flag: _type = type.dart_name
  if type.is_struct: _type = type.dart_name
  if type.is_object: _type = type.dart_name
  if type.is_callback: _type = type.dart_name
  if type.is_future: _type = f'WGPUFuture'

  if type.is_array:
    inner_type = type.array_inner
    if inner_type.is_void_data or inner_type.is_numeric:
      inner_type_ptr = replace(inner_type)
      inner_type_ptr.pointer = 1
      _type = type_to_dart(inner_type_ptr)
    else: 
      inner_dart_type = type_to_dart(type.array_inner)
      _type = f'List<{inner_dart_type}>'

  if type.is_function_ptr:
    c_name = f'bindings.WGPU{to_dart_top_level_name(type.ref_name)}'
    _type = f'{c_name}'

  if _type == 'dynamic': print(f'warning(type): cannot resolve dart type for {type.kind} ({type.pointer})')

  if nullable: _type += '?'
  return _type


def type_fn_c_type(type: Type) -> str:
  if not type.is_pointer:
    if type.is_integer: return 'int'
    if type.is_float: return 'double'
  
  return type_to_c(type)

def type_to_c(type: Type, pointer_offset: int = 0) -> str:
  kind = type.kind
  _type = None

  if kind == TypeKind.VOID: _type = 'ffi.Void'
  if kind == TypeKind.VOID_DATA: _type = 'ffi.Uint8'
  if kind == TypeKind.INT8: _type = 'ffi.Int8'
  if kind == TypeKind.UINT8: _type = 'ffi.Uint8'
  if kind == TypeKind.INT16: _type = 'ffi.Int16'
  if kind == TypeKind.UINT16: _type = 'ffi.Uint16'
  if kind == TypeKind.INT32: _type = 'ffi.Int32'
  if kind == TypeKind.UINT32: _type = 'ffi.Uint32'
  if kind == TypeKind.INT64: _type = 'ffi.Int64'
  if kind == TypeKind.UINT64: _type = 'ffi.Uint64'
  if kind == TypeKind.USIZE: _type = 'ffi.Uint64'
  if kind == TypeKind.FLOAT32: _type = 'ffi.Float'
  if kind == TypeKind.FLOAT64: _type = 'ffi.Double'
  if kind == TypeKind.BOOL: _type = 'ffi.Bool'
  if kind == TypeKind.STRING: _type = 'bindings.WGPUStringView'
  if kind == TypeKind.CHAR: _type = 'ffi.Uint8'

  if type.is_enum: _type = 'int'
  if type.is_flag: _type = type.flag_decl.c_name
  if type.is_struct: _type = type.struct_decl.c_name
  if type.is_object: _type = f'ffi.Pointer<{type.c_name}Impl>'

  if type.is_array:
    inner_c_type = type_to_c(type.array_inner)
    _type = f'ffi.Pointer<{inner_c_type}>'
  elif type.is_pointer:
    for _ in range(type.pointer + pointer_offset): _type = f'ffi.Pointer<{_type}>'
  # elif type.is_nullable: _type = f'ffi.Pointer<{_type}>'

  if _type is None:
    _type = 'ffi.Void'
    print(f'warning(type): cannot resolve C type for {type.kind}')


  return _type


def type_zero_value(type: Type) -> str:
  if type.is_nullable: return 'null'

  if type.is_pointer: return 'null'
  if type.is_array: return 'const []'
  if type.is_integer: return '0'
  if type.is_float: return '0.0'
  if type.is_bool: return 'false'
  if type.is_string: return "''"

  if type.is_enum or type.is_flag:
    decl = type.enum_or_flag_decl
    zero_entry = decl.zero_entry
    if zero_entry is None: raise ValueError(f'no zero entry for {decl.name}')
    return f'.{zero_entry.dart_name}'

  if type.is_struct: return f'_${type.dart_name}$Zero'
  if type.is_callback: return 'null'

  raise ValueError(f'cannot resolve zero value for {type.kind}')


def _array_count_field(type: Type, dest: str) -> str:
  field_name = type.array_length_field
  return '.'.join(dest.split('.')[:-1] + [field_name])


def type_to_native(type: Type, expr: str, nullable: bool = False) -> str:
  kind = type.kind
  _expr = expr
  promoted_expr = f'{expr}!' if '.' in expr else expr
  if nullable or type.is_nullable: _expr += '?'
  else: promoted_expr = expr

  if not type.is_pointer:
    if type.is_numeric: return expr
    if type.is_bool: return f'{expr} ? 1 : 0'

  if type.is_string:
    if nullable: return f'{expr}?.toStringView(allocator)'
    return f'{promoted_expr}.toStringView(allocator)'

  if type.is_pointer:
    if type.is_primitive and type.is_nullable: return f'{expr} ?? ffi.nullptr'
    if type.is_char: return f'{expr}.toNativeUtf8(allocator: allocator).cast()'
    if type.is_void: return f'{expr}'

  if type.is_enum: return f'{_expr}.value'
  if type.is_flag: return f'{_expr}.value'
  if type.is_struct:
    _expr = expr
    inner_expr = f'{promoted_expr}' if type.is_nullable else _expr
    _expr = f'_{type.dart_name}$ToNative(allocator, {inner_expr})'
    if not type.is_pointer: _expr += '.ref'
    if type.is_nullable: _expr = f'{expr} != null? {_expr} : ffi.nullptr'
    return _expr

  if type.is_object:
    if type.is_nullable: return f'{expr} != null? _{type.dart_name}$ToPointer({promoted_expr}) : ffi.nullptr'
    return f'_{type.dart_name}$ToPointer({expr})'

  if type.is_function_ptr: return f'{expr}'

  if type.is_callback: return f'_{type.dart_name}$Register(allocator, {promoted_expr}).ref'
  if type.is_future: return f'.$allocate(allocator, id: {promoted_expr}.id).ref'

  print(f'warning(type_to_native): cannot resolve native conversion for {type.kind}')
  return f'{expr} as dynamic'


def type_allocator_type(type: Type) -> str:
  if type.is_array:
    inner_type = type.array_inner
    c_arr_type = inner_type.resolve_c_type()
    if inner_type.is_enum or inner_type.is_flag: c_arr_type = 'ffi.UnsignedInt'
    if inner_type.is_void: c_arr_type = 'ffi.Uint8'
    return c_arr_type
  
  if type.is_pointer:
    inner_type = replace(type)
    inner_type.pointer -= 1
    return inner_type.resolve_c_type()

  return type.resolve_c_type()


def type_set_native(type: Type, dest: str, expr: str, default: Optional[str] = None, array_count_field: Optional[str] = None) -> list[str]:
  kind = type.kind
  d = type.default
  if not type.is_nullable: d = None
  if default is not None: d = default

  is_nullable = type.is_nullable or default is not None
  promoted_expr = f'{expr}!' if '.' in expr else expr
  if not is_nullable: promoted_expr = expr

  if type.is_array:
    inner_type = type.array_inner
    c_arr_type = type_allocator_type(type)

    is_not_empty_getter = f'{promoted_expr}.isNotEmpty'
    length_getter = f'{promoted_expr}.length'
    array_setter_impl: list[str] = []

    if inner_type.is_void_data:
      length_getter = f'{promoted_expr}.lengthInBytes'
      is_not_empty_getter = f'{promoted_expr}.lengthInBytes > 0'
      array_setter_impl = [
        f'final dataList = {promoted_expr}.buffer.asUint8List({promoted_expr}.offsetInBytes, {promoted_expr}.lengthInBytes);',
        f'arrayPtr.asTypedList(arrayLength).setAll(0, dataList);'
      ]

    elif type.is_typed_data_array:
      array_setter_impl = [f'arrayPtr.asTypedList(arrayLength).setAll(0, {promoted_expr});']
    else:
      array_setter_impl = [
        f'for (var i = 0; i < arrayLength; i++) {{',
        f'  arrayPtr[i] = {type_to_native(inner_type, f"{promoted_expr}[i]")};',
        f'}}',
      ]

    impl: list[str] = []
    if is_nullable: impl.append(f'if ({expr} != null && {is_not_empty_getter}) {{')
    else: impl.append(f'if ({is_not_empty_getter}) {{')
    impl.append(f'  final arrayLength = {length_getter};')
    impl.append(f'  final arrayPtr = allocator<{c_arr_type}>(arrayLength);')
    impl.extend(indent(array_setter_impl))

    if inner_type.is_char: impl.append(f'  {dest} = arrayPtr.cast();')
    else: impl.append(f'  {dest} = arrayPtr;')

    array_count_field_setter = array_count_field
    if not array_count_field_setter and type.array_length_has_field:
      array_count_field_setter = _array_count_field(type, dest)

    if array_count_field_setter: impl.append(f'  {array_count_field_setter} = arrayLength;')
    impl.append(f'}}')
    impl.append(f'else {{')
    impl.append(f'  {dest} = ffi.nullptr;')
    if array_count_field_setter: impl.append(f'  {array_count_field_setter} = 0;')
    impl.append(f'}}')
    return wrap_in_block(impl)

  if type.is_pointer and type.is_char:
    if is_nullable:
      return [f'{dest} = {expr}?.toNativeUtf8(allocator: allocator).cast() ?? ffi.nullptr;']
    else:
      return [f'{dest} = {expr}.toNativeUtf8(allocator: allocator).cast();']

  if type.is_pointer and type.is_void:
    if is_nullable:
      return [f'{dest} = {expr} ?? ffi.nullptr;']
    else:
      return [f'{dest} = {expr};']

  if type.is_string and type.is_nullable:
    inner = type_to_native(type, expr, nullable=False)
    return [f'if ({expr} != null) {dest} = {inner};']

  if d is not None:
    if d == 'nullptr': return [f'{dest} = {type_to_native(type, expr)};']
    if d == 'zero' and type.is_struct:
      return [f'if ({expr} != null) {dest} = {type_to_native(type, promoted_expr)};']

    _expr = f'({expr} ?? {d})'
    return [f'{dest} = {type_to_native(type, _expr)};']

  return [f'{dest} = {type_to_native(type, expr)};']


def type_from_native(type: Type, expr: str, borrowed_field: Optional[str] = None) -> str:
  if type.is_bool: return f'{expr} == 1'
  if not type.is_pointer and type.is_numeric: return expr
  if type.is_nullable and type.is_float: return f'{expr} != .nan ? {expr} : null'

  if type.is_pointer:
    if type.is_void: return expr
    if type.kind == TypeKind.UINT32: return f'{expr}.toUnsigned(32)'
    if type.is_char: return f'{expr}.cast<Utf8>().toDartString()'

  if type.is_struct:
    _ref = f'{expr}.ref' if type.is_pointer else expr
    ctor = f'_{type.dart_name}$FromNative({_ref}'
    if borrowed_field is not None: ctor += f', borrowed: {borrowed_field}'
    ctor += ')'

    if type.is_nullable: return f'{expr} != ffi.nullptr? {ctor} : null'
    return f'{ctor}'

  if type.is_enum: return f'_{type.dart_name}$FromValue({expr})'
  if type.is_flag: return f'{type.dart_name}({expr})'
  if type.is_string: return f'{expr}.toDartString()'
  if type.is_callback: return 'null'
  if type.is_future: return f'WGPUFuture(id: {expr}.id)'

  if type.is_object:
    _expr = expr
    if type.is_pointer:
      _expr = f'{expr}.value'

    ctor = f'_{type.dart_name}$FromPointer({_expr}'
    if borrowed_field is not None: ctor += f', borrowed: {borrowed_field}'
    elif type.is_pointer and type.pointer_kind == PointerKind.IMMUTABLE: ctor += f', borrowed: true'
    ctor += ')'

    if type.is_nullable: return f'{expr} != ffi.nullptr ? {ctor} : null'
    return f'{ctor}'

  if type.is_function_ptr: return expr

  print(f'warning(type_from_native): no conversion implemented for {type.kind}')
  return expr


def type_set_dart(type: Type, dest: str, expr: str, borrowed_field: Optional[str] = None) -> list[str]:
  if type.is_array:
    inner_type = type.array_inner

    has_count_field = type.array_length_has_field
    count = _array_count_field(type, dest) if has_count_field else type.array_length

    impl: list[str] = []
    if type.is_typed_data_array:
      impl.append(f'final {type.resolve_dart_type()} {dest};')
      impl.append(f'if ({expr} != ffi.nullptr) {{')
      impl.append(f'  {dest} = .fromList({expr}.asTypedList({count}));')
      impl.append(f'}}')
      impl.append(f'else {{')
      if type.is_nullable:
        impl.append(f'  {dest} = null;')
      else:
        impl.append(f'  if ({count} > 0) {{')
        impl.append(f'    throw Exception("{dest} has a null pointer for a required array");')
        impl.append(f'  }}')
        impl.append(f'  {dest} = .new(0);')
      impl.append(f'}}')
    else:
      impl.append(f'final {dest} = <{inner_type.resolve_dart_type()}>[];')
      impl.append(f'if ({expr} != ffi.nullptr && {count} > 0) {{')
      impl.append(f'  for (var i = 0; i < {count}; i++) {{')
      impl.append(f'    {dest}.add({type_from_native(inner_type, f"{expr}[i]", borrowed_field=borrowed_field)});')
      impl.append(f'  }}')
      impl.append(f'}}')

    return impl


    return impl

  return [
    f'final {dest} = {type_from_native(type, expr, borrowed_field=borrowed_field)};'
  ]
