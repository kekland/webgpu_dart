from dataclasses import dataclass
from typing import Optional

import _state as state
from types_gen import *
from utils import *


@dataclass
class ConstantDecl:
  name: str
  kind: TypeKind
  value: str
  tags: set[str]

  @property
  def dart_name(self) -> str: return to_c_name(self.name).upper()

  @property
  def c_name(self) -> str: return f'bindings.WGPU_{to_c_name(self.name).upper()}'


def parse_constant_decl(name) -> ConstantDecl:
  decl = state.spec[name]
  kind = parse_primitive_type_kind(decl['type'])
  value = decl['value']
  tags = set(decl.get('tags', []))
  return ConstantDecl(name=name, kind=kind, value=value, tags=tags)


def generate_constant_code(constant: ConstantDecl) -> tuple[list[str], list[str]]:
  code: list[str] = []
  code.append(f'const {constant.dart_name} = {constant.c_name};')
  return [], code
