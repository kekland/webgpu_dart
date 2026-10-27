from dataclasses import dataclass
from typing import Optional

import _state as state
from utils import *


@dataclass
class FlagDeclEntry:
  name: str
  value: int
  tags: set[str]

  @property
  def dart_name(self) -> str: return to_dart_member_name(self.name)

  @property
  def js_name(self): return None

@dataclass
class FlagDecl:
  name: str
  entries: list[FlagDeclEntry]
  tags: set[str]

  @property
  def dart_name(self) -> str: return to_dart_top_level_name(self.name)

  @property
  def c_name(self) -> str: return f'WGPU{to_dart_top_level_name(self.name)}'

  def entry(self, name: str) -> FlagDeclEntry:
    for e in self.entries:
      if e.name == name: return e
    raise ValueError(f'entry not found: {name}')

  @property
  def zero_entry(self) -> Optional[FlagDeclEntry]:
    for e in self.entries:
      if e.value == 0: return e
    return None


def parse_flag_entry_decl(decl: dict) -> FlagDeclEntry:
  name = decl['name']
  value = decl['value']
  tags = set(decl.get('tags', []))
  return FlagDeclEntry(name=name, value=value, tags=tags)


def parse_flag_decl(name: str) -> FlagDecl:
  decl = state.spec[name]
  entries: list[FlagDeclEntry] = []

  for i, entry_decl in enumerate(decl['values']):
    entry = parse_flag_entry_decl(entry_decl)
    entries.append(entry)

  tags = set(decl.get('tags', []))
  return FlagDecl(name=name, entries=entries, tags=tags)

def generate_flag_code(flag: FlagDecl) -> tuple[list[str], list[str]]:
  dart_name = flag.dart_name
  code: list[str] = []
  
  code.append(f'extension type const {dart_name}(int value) {{')

  for entry in flag.entries:
    code.append(f'  static const {entry.dart_name} = {dart_name}({entry.value});')

  code.append('')
  code.append(f'  {PREFER_INLINE}')
  code.append(f'  static {dart_name} of(List<{dart_name}> flags) => {dart_name}(flags.fold(0, (v, f) => v | f.value));')
  code.append('')
  code.append(f'  {PREFER_INLINE}')
  code.append(f'  bool contains({dart_name} flag) => (value & flag.value) == flag.value;')
  for entry in flag.entries:
    cap = capitalize(entry.dart_name)
    code.append(f'  bool get has{cap} => contains(.{entry.dart_name});')

  code.append('')
  code.append(f'  {dart_name} operator |({dart_name} other) => {dart_name}(value | other.value);')
  code.append(f'  {dart_name} operator &({dart_name} other) => {dart_name}(value & other.value);')
  code.append(f'  {dart_name} operator ^({dart_name} other) => {dart_name}(value ^ other.value);')
  code.append(f'  {dart_name} operator ~() => {dart_name}(~value);')
  code.append(f'}}')

  return code, []