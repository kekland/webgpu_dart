from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto

import _state as state
from types_gen import *
from utils import *


class StructMemberKind(Enum):
  REQUIRED = auto()
  NULLABLE = auto()
  DEFAULTED = auto()
  SENTINEL = auto()


@dataclass
class StructMemberDecl:
  name: str
  type: Type
  tags: set[str]
  array_length_of: Optional[str] = None
  struct: 'StructDecl' = None

  def resolve_kind(self) -> tuple[StructMemberKind, Optional[str]]:
    type = self.type
    default = self.type.default

    if type.is_callback: return StructMemberKind.NULLABLE, None
    if type.is_nullable: return StructMemberKind.NULLABLE, None
    if default is None:
      if type.is_array:
        if type.is_typed_data_array:
          return StructMemberKind.SENTINEL, '.new(0)'
        else:
          return StructMemberKind.DEFAULTED, 'const []'

      if type.is_struct and type.struct_decl.has_zero: return StructMemberKind.DEFAULTED, 'const .new()'
      if type.is_enum or type.is_flag:
        decl = type.enum_or_flag_decl
        zero_entry = decl.zero_entry
        if zero_entry is None: return StructMemberKind.REQUIRED, None
        if zero_entry.js_name == 'undefined': return StructMemberKind.DEFAULTED, f'.{zero_entry.dart_name}'
        return StructMemberKind.DEFAULTED, f'.{zero_entry.dart_name}'

      return StructMemberKind.REQUIRED, None

    if is_numeric(default) or default in ('true', 'false'):
      return StructMemberKind.DEFAULTED, type.resolve_dart_default()

    if type.is_enum or type.is_flag:
      return StructMemberKind.DEFAULTED, type.resolve_dart_default()

    if type.is_struct and default == 'zero':
      return StructMemberKind.SENTINEL, f'zero'

    if type.is_array and default == 'nullptr':
      return StructMemberKind.SENTINEL, f'ffi.nullptr'

    if default in state.CONSTANTS:
      return StructMemberKind.SENTINEL, state.get_constant(default).dart_name

    raise ValueError(f'unknown default value: {default} on {self.struct.name}.{self.name}')

  @property
  def is_nullable(self) -> bool:
    kind, _ = self.resolve_kind()
    return kind in (StructMemberKind.NULLABLE, StructMemberKind.SENTINEL)

  @property
  def dart_name(self) -> str: 
    if self.type.is_callback and self.name.endswith('info'): return to_dart_member_name(self.name[:-5])
    return to_dart_member_name(self.name)

  @property
  def c_name(self) -> str: return to_c_member_name(self.name)

  @property
  def dart_type(self) -> str: return self.type.resolve_dart_type(nullable=self.is_nullable)

  @property
  def zero_value(self) -> str: return self.type.resolve_zero_value()


class Extensible(Enum):
  NO = auto()
  IN = auto()
  OUT = auto()


class Chained(Enum):
  NO = auto()
  IN = auto()
  OUT = auto()


@dataclass
class StructDecl:
  name: str
  members: list[StructMemberDecl]
  tags: set[str]
  extensible: Extensible
  chained: Chained
  chain_roots: list[str]
  free_members: bool
  out_name: Optional[str] = None
  is_derived: bool = False

  def __post_init__(self):
    for member in self.members: member.struct = self

  @property
  def dart_name(self) -> str: 
    if self.name == 'future': return 'WGPUFuture'
    return to_dart_top_level_name(self.name)

  @property
  def c_name(self) -> str: return f'bindings.WGPU{to_dart_top_level_name(self.name)}'

  @property
  def has_zero(self) -> bool:
    return all(m.resolve_kind()[0] != StructMemberKind.REQUIRED for m in self.members)

  @property
  def needs_free_members(self) -> bool:
    return any(m.type.is_array or m.type.is_string or m.type.is_pointer for m in self.members)

  def member(self, name: str) -> StructMemberDecl:
    for m in self.members:
      if m.name == name: return m
    raise ValueError(f'unknown member: {name} in struct {self.name}')


def parse_struct_member(decl: dict) -> StructMemberDecl:
  name = decl['name']
  type = parse_type(decl)
  tags = set(decl.get('tags', []))
  return StructMemberDecl(name=name, type=type, tags=tags)


def parse_struct_members(decl: dict) -> list[StructMemberDecl]:
  members = [parse_struct_member(m) for m in decl.get('members', [])]
  members_by_name = {m.name: m for m in members}

  for m in members:
    if m.type.is_array and m.type.array_length_has_field:
      members_by_name[m.type.array_length].array_length_of = m.name

  return members


def parse_extensible(value: str) -> Extensible:
  if value == 'in': return Extensible.IN
  elif value == 'out': return Extensible.OUT
  return Extensible.NO


def parse_chained(value: str) -> Chained:
  if value == 'in': return Chained.IN
  elif value == 'out': return Chained.OUT
  return Chained.NO


def needs_free_members(extensible: Extensible, members: list[StructMemberDecl]) -> bool:
  if extensible != Extensible.OUT: return False
  return any(m.type.is_array or m.type.is_string or m.type.is_pointer for m in members)


def parse_struct_decl(name: str) -> StructDecl:
  decl = state.spec[name]
  members = parse_struct_members(decl)
  tags = set(decl.get('tags', []))
  extensible = parse_extensible(decl.get('extensible', 'NO'))
  chained = parse_chained(decl.get('chained', 'NO'))
  chain_roots = decl.get('chain roots', [])
  free_members = needs_free_members(extensible, members)

  return StructDecl(name=name, members=members, tags=tags, extensible=extensible, chained=chained, chain_roots=chain_roots, free_members=free_members)


def generate_struct_code(struct: StructDecl) -> tuple[list[str], list[str]]:
  code: list[str] = []
  impl_code: list[str] = []

  is_chained = struct.chained != Chained.NO
  is_chain_root = struct.extensible != Extensible.NO
  class_extends = ''
  if is_chained: class_extends = ' extends ChainedStruct'
  elif is_chain_root: class_extends = ' extends ExtensibleStruct'

  # Constructor
  ctor: list[str] = []
  for member in struct.members:
    if member.array_length_of: continue
    kind, default = member.resolve_kind()
    dart_type = member.dart_type

    if kind == StructMemberKind.DEFAULTED:
      ctor.append(f'final {dart_type} {member.dart_name} = {default},')
    elif member.is_nullable:
      ctor.append(f'final {dart_type} {member.dart_name},')
    else:
      ctor.append(f'required final {dart_type} {member.dart_name},')

  if is_chained:
    ctor.append(f'super.next,')
  elif is_chain_root:
    ctor.append(f'super.next,')

  # Declaration body
  body: list[str] = []
  if is_chained:
    body.append(f'@override')
    body.append(f'SType get sType => .{uncapitalize(struct.dart_name)};')

  # Full declaration
  decl: list[str] = []
  if ctor:
    decl.append(f'final class const {struct.dart_name}({{')
    decl.extend(indent(ctor))
    decl.append(f'}}){class_extends}')
  else:
    decl.append(f'final class const {struct.dart_name}(){class_extends}')

  if body:
    decl[-1] += f' {{'
    decl.extend(indent(body))
    decl.append(f'}}')
  else:
    decl[-1] += f';'

  is_native = 'native' in struct.tags or 'dawn' in struct.tags
  if is_native: impl_code = decl
  else: code = decl

  impl_code.append(f'')

  # Impl: to native
  if not struct.is_derived:
    impl_code.append(f'ffi.Pointer<{struct.c_name}> _{struct.dart_name}$ToNative(ffi.Allocator allocator, {struct.dart_name} value) {{')
    impl_code.append(f'  final ptr = allocator<{struct.c_name}>();')

    if is_chained:
      impl_code.append(f'  ptr.ref.chain.sType = value.sType.value;')
      impl_code.append(f'  ptr.ref.chain.next = _ChainedStruct$ToNative(allocator, value.next).cast();')
    elif is_chain_root:
      impl_code.append(f'  ptr.ref.nextInChain = _ChainedStruct$ToNative(allocator, value.next).cast();')

    for m in struct.members:
      kind, default = m.resolve_kind()
      if kind != StructMemberKind.SENTINEL: default = None

      if m.array_length_of:
        array_member = struct.member(m.array_length_of)
        if array_member.is_nullable:
          impl_code.append(f'  ptr.ref.{m.c_name} = value.{array_member.dart_name}?.length ?? 0;')
        else:
          impl_code.append(f'  ptr.ref.{m.c_name} = value.{array_member.dart_name}.length;')

        continue

      impl_code.extend(indent(m.type.resolve_set_native(f'ptr.ref.{m.c_name}', f'value.{m.dart_name}', default=default)))

    impl_code.append(f'  return ptr;')
    impl_code.append(f'}}')
    impl_code.append(f'')
  
  # Impl: from native
  if not struct.is_derived:
    impl_code.append(f'{struct.dart_name} _{struct.dart_name}$FromNative({struct.c_name} str, {{bool borrowed = false}}) {{')

    for m in struct.members:
      dart_name = m.dart_name
      c_name = m.c_name
      impl_code.extend(indent(m.type.resolve_set_dart(dart_name, f'str.{c_name}', borrowed_field='borrowed')))

    impl_code.append(f'  return .new(')
    for m in struct.members:
      if m.array_length_of: continue
      impl_code.append(f'    {m.dart_name}: {m.dart_name},')

    if is_chained: impl_code.append(f'    next: _ChainedStruct$FromNative(str.chain.next, borrowed: borrowed),')
    elif is_chain_root: impl_code.append(f'    next: _ChainedStruct$FromNative(str.nextInChain, borrowed: borrowed),')
    impl_code.append(f'  );')

    impl_code.append(f'}}')


  return code, impl_code


def generate_chained_struct_transformer() -> list[str]:
  structs = state.STRUCTS.values()
  chain_extensions = [s for s in structs if s.chained != Chained.NO]

  lines = [
    f'ChainedStruct? _ChainedStruct$FromNative(ffi.Pointer<bindings.WGPUChainedStruct> ptr, {{bool borrowed = false}}) {{',
    f'  if (ptr == ffi.nullptr) return null;',
    f'  final stype = ptr.ref.sType;',
    f'  return switch (stype) {{',
  ]

  stype_enum = state.ENUMS['s type']

  val_from_native: dict[int, str] = {}
  val_to_native: dict[int, str] = {}
  val_type: dict[int, StructDecl] = {}

  for s in chain_extensions:
    stype = stype_enum.entry(s.name)
    dart_name = s.dart_name

    val_from_native[stype.effective_value] = f'_{dart_name}$FromNative(ptr.cast<{s.c_name}>().ref, borrowed: borrowed)'
    val_to_native[stype.effective_value] = f'_{dart_name}$ToNative(allocator, value as {dart_name})'
    val_type[stype.effective_value] = s

  vals_sorted = sorted(val_from_native.keys())
  for val in vals_sorted:
    result = val_from_native[val]
    lines.append(f'    {val} => {result},')

  lines.append(f'    _ => throw ArgumentError(\'Unknown chained struct type: $stype\'),')
  lines.append(f'  }};')
  lines.append(f'}}')

  lines.append(f'ffi.Pointer _ChainedStruct$ToNative(ffi.Allocator allocator, ChainedStruct? value) {{')
  lines.append(f'if (value == null) return ffi.nullptr;')
  lines.append(f'  final stype = value.sType;')
  lines.append(f'  return switch(stype) {{')

  for val in vals_sorted:
    result = val_to_native[val]
    lines.append(f'    {val} => {result},')

  lines.append(f'    _ => throw ArgumentError(\'Unknown chained struct type: $stype\'),')

  lines.append(f'  }};')
  lines.append(f'}}')
  lines.append(f'')
  lines.append(f'ffi.Pointer<bindings.WGPUChainedStruct> _ChainedStruct$Allocate(ffi.Allocator allocator, SType stype) {{')
  lines.append(f'  final result = switch(stype.value) {{')
  for val in vals_sorted:
    result = val_to_native[val]
    lines.append(f'    {val} => allocator<{val_type[val].c_name}>(),')
  lines.append(f'    _ => throw ArgumentError(\'Unknown chained struct type: $stype\'),')
  lines.append(f'  }}.cast<bindings.WGPUChainedStruct>();')
  lines.append(f'')
  lines.append(f'  result.ref.sType = stype.value;')
  lines.append(f'  return result;')
  lines.append(f'}}')
  lines.append(f'')
  lines.append(f'ffi.Pointer<bindings.WGPUChainedStruct> _ChainedStruct$FromExtensionList(ffi.Allocator allocator, List<SType> extensions) {{')
  lines.append(f'  ffi.Pointer<bindings.WGPUChainedStruct> head = ffi.nullptr;')
  lines.append(f'  for (final stype in extensions.reversed) {{')
  lines.append(f'    final ptr = _ChainedStruct$Allocate(allocator, stype);')
  lines.append(f'    ptr.ref.next = head;')
  lines.append(f'    head = ptr;')
  lines.append(f'  }}')
  lines.append(f'  return head;')
  lines.append(f'}}')

  return lines
