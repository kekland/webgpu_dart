from dataclasses import dataclass
from typing import Optional

import _state as state
from utils import *


@dataclass
class EnumDeclEntry:
  name: str
  value: int
  valid: bool
  tags: set[str]
  enum: 'EnumDecl' = None
  js_name: Optional[str] = None

  @property
  def dart_name(self) -> str:
    if self.js_name == 'undefined': return to_dart_member_name(self.name)
    webidl_name = self.webidl_name_raw
    return to_dart_member_name(' '.join(webidl_name[1:-1].split('-')))

  @property
  def effective_value(self) -> str:
    effective_value = self.value
    if 'compat' in self.tags: effective_value = 0x0002_0000 + self.value
    elif 'dawn' in self.tags: effective_value = 0x0005_0000 + self.value
    elif 'emscripten' in self.tags: effective_value = 0x0004_0000 + self.value
    elif 'native' in self.tags: effective_value = 0x0001_0000 + self.value
    return f'0x{effective_value:08X}'

  @property
  def webidl_name_raw(self) -> str:
    if self.js_name == 'undefined': return 'null'
    if self.js_name is not None: return self.js_name
    return f'\'{enum_to_webidl_name(self.name)}\''

  @property
  def webidl_name(self) -> str: return self.webidl_name_raw.lower()


@dataclass
class EnumDecl:
  name: str
  entries: list[EnumDeclEntry]
  tags: set[str]

  def __post_init__(self):
    for entry in self.entries: entry.enum = self

  @property
  def dart_name(self) -> str: return to_dart_top_level_name(self.name)

  @property
  def c_name(self) -> str: return f'WGPU{to_dart_top_level_name(self.name)}'

  def entry(self, name: str) -> EnumDeclEntry:
    for e in self.entries:
      if e.name == name: return e
    raise ValueError(f'entry not found: {name} ({self.name})')

  @property
  def zero_entry(self) -> Optional[EnumDeclEntry]:
    for e in self.entries:
      if e.value == 0: return e
    return None


def parse_enum_entry_decl(decl: dict) -> EnumDeclEntry:
  name = decl['name']
  value = decl['value']
  valid = decl.get('valid', True)
  tags = set(decl.get('tags', []))
  js_name = decl.get('jsrepr')
  return EnumDeclEntry(name=name, value=value, valid=valid, tags=tags, js_name=js_name)


def parse_enum_decl(name: str) -> EnumDecl:
  decl = state.spec[name]
  entries: list[EnumDeclEntry] = []

  for entry_decl in decl['values']:
    entry = parse_enum_entry_decl(entry_decl)
    entries.append(entry)

  tags = set(decl.get('tags', []))
  return EnumDecl(name=name, entries=entries, tags=tags)

  
def get_effective_enum_value(value: int, tags: set[str]) -> int:
  if 'compat' in tags: return 0x0002_0000 + value
  if 'dawn' in tags: return 0x0005_0000 + value
  if 'emscripten' in tags: return 0x0004_0000 + value
  if 'native' in tags: return 0x0001_0000 + value
  return value

def generate_enum_code(enum: EnumDecl) -> tuple[list[str], list[str]]:
  code: list[str] = []
  impl_code: list[str] = []

  code.append(f'extension type const {enum.dart_name}._(int value) {{')

  # entries
  for entry in enum.entries:
    code.append(f'  static const {entry.dart_name} = {enum.dart_name}._({entry.effective_value});')
  code.append('')

  # values
  code.append(f'  static const List<{enum.dart_name}> values = [')
  for entry in enum.entries:
    code.append(f'    .{entry.dart_name},')
  code.append(f'  ];')
  code.append('')

  # name
  last_value = None
  code.append(f'  String? get name => switch (this) {{')
  for entry in enum.entries:
    if not entry.valid: continue
    if entry.effective_value == last_value: code.append(f'    // ignore: unreachable_switch_case')
    code.append(f'    .{entry.dart_name} => {entry.webidl_name},')
    last_value = entry.effective_value

  code.append(f'    _ => throw ArgumentError.value(this, \'this\', \'invalid enum entry\'),')
  code.append('  };')
  code.append('')

  # fromName
  code.append(f'  static {enum.dart_name} fromName(String name) => switch (name) {{')
  for entry in enum.entries:
    if not entry.valid: continue
    webidl_name = entry.webidl_name
    if webidl_name == 'null': continue
    code.append(f'    {webidl_name} => .{entry.dart_name},')
  code.append(f'    _ => throw ArgumentError.value(name, \'name\', \'invalid enum name\'),')
  code.append('  };')
  code.append('')
  
  # fromValue
  impl_code.append(f'{enum.dart_name} _{enum.dart_name}$FromValue(int value) => switch (value) {{')

  last_value = None
  for entry in enum.entries:
    if entry.effective_value == last_value: impl_code.append(f'  // ignore: unreachable_switch_case')
    impl_code.append(f'  {entry.effective_value} => .{entry.dart_name},')
    last_value = entry.effective_value

  impl_code.append(f'  _ => throw ArgumentError.value(value, \'value\', \'unknown value for {enum.dart_name}\'),')
  impl_code.append('};')


  code.append(f'}}')


  return code, impl_code