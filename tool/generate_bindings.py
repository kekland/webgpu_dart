#!/usr/bin/env python3

from _common import ROOT, exec_cmd
from pathlib import Path

import json

DAWN_JSON = ROOT / 'build' / 'dawn.json'
OUT_IMPL_PATH = ROOT / 'lib' / 'native' / 'dawn.g.dart'
OUT_SHARED_PATH = ROOT / 'lib' / 'shared' / 'webgpu.g.dart'


if __name__ == '__main__':
  FFIGEN_PATH = ROOT / 'tool' / 'generator' / '_ffigen.dart'
  GENERATOR_PATH = ROOT / 'tool' / 'generator' / '_generator.py'

  exec_cmd(f'{FFIGEN_PATH}')
  exec_cmd(f'{GENERATOR_PATH} --spec-path {DAWN_JSON} --out-impl {OUT_IMPL_PATH} --out-shared {OUT_SHARED_PATH}', cwd=GENERATOR_PATH.parent)