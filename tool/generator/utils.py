PREFER_INLINE = '@pragma(\'vm:prefer-inline\')'


def indent(lines: Union[str, list[str]], level: int = 1, indent_str: str = '  ') -> Union[str, list[str]]:
  indent_prefix = indent_str * level
  if isinstance(lines, str): return indent_prefix + lines
  return [indent_prefix + line if line else '' for line in lines]


def _clean_dart_name(name: str):
  if name in ('null', 'true', 'false'): return f'{name}_'

  DIGITS = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'}
  if name[0].isdigit(): return DIGITS[name[0]] + ' ' + name[1:]

  return name


def to_dart_top_level_name(name: str) -> str:
  cleaned = _clean_dart_name(name)
  return _to_pascal_case(cleaned)


def to_dart_member_name(name: str) -> str:
  cleaned = _clean_dart_name(name)
  return _to_camel_case(cleaned)


def to_c_member_name(name: str) -> str:
  if len(name) == 1: return name
  return to_dart_member_name(name)


def _capitalize_segment(seg: str) -> str:
  if not seg: return '_'
  if seg[0].isupper() or seg[0].isdigit(): return seg
  return seg[0].upper() + seg[1:]


def _to_camel_case(name: str) -> str:
  parts = name.split(' ')
  if not parts: return name
  first = uncapitalize(parts[0])
  rest = ''.join(_capitalize_segment(seg) for seg in parts[1:])
  return first + rest


def _to_pascal_case(name: str) -> str:
  return ''.join(_capitalize_segment(seg) for seg in name.split(' '))


def to_c_name(name: str) -> str:
  return '_'.join(name.split(' '))


def capitalize(name: str) -> str:
  if not name: return name
  if name[0].isupper() or name[0].isdigit(): return name
  return name[0].upper() + name[1:]


def uncapitalize(name: str) -> str:
  if not name: return name
  if name[0].islower() or name[0].isdigit(): return name
  return name[0].lower() + name[1:]


def is_numeric(value: Any) -> bool:
  result = isinstance(value, int) or isinstance(value, float)
  if isinstance(value, str):
    result = value.isnumeric() or value.startswith('0x') or value.endswith('f')
  return result


def wrap_in_block(lines: Union[str, list[str]]) -> list[str]:
  if isinstance(lines, str): lines = [lines]
  return ['{'] + indent(lines) + ['}']


force_split_tokens = ['D3D11', 'D3D12']
force_lowercase_tokens = [
  'RGB9', 'E5', 'RGBA16', 'A2', 'RG16', 'R32', 
  'ASTC', 'RG8', 'R10X6', 'BGRA8', 'B10', 'RGB10', 
  'RG11B10', 'RG32', 'RG11', 'ETC2', 'R16', 'RGBA32', 'BT_1886', 
  'A8', 'BG8', 'RGBA8', 'BG10X6', 'R8'
]

def enum_to_webidl_name(enum: str) -> str:
  out = ''
  prev_token = None
  for word in enum.split():
    if out and not out[-1].isdigit():
      out += '-'
    elif prev_token in force_split_tokens:
      out += '-'

    if word in force_lowercase_tokens:
      out += word.lower()
    else:
      out += word
  
    prev_token = word

  return out


# {'RGB9', '1D', 'E5', 'RGBA16', 'A2', 'GL', 'MSAA', 'LUID', 'XCB', 'CPU', 'WGSL', 'RG16', 'SPIRV', 'ASTC', 'R32', 'RG8', 'IO', 'R10X6', 'BC', 'UWP', 'HLG', '3D', 'CW', '2D', 'FD', 'GPU', 'D3D', 'BGRA8', 'D3D11', 'B10', 'RGB10', 'RG11B10', 'MTL', 'WGPU', 'RG32', 'RG11', 'DXGI', 'ETC2', 'EGL', 'R16', 'ANGLE', 'OOM', 'RGBA32', 'BT_1886', 'HTML', 'HWND', 'CCW', 'A8', 'BG8', 'RGBA8', 'D3D12', 'BG10X6', 'PQ', 'R8', 'SMPTE_170M'}