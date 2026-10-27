#!/usr/bin/env python3
from _common import ROOT, exec_cmd
import argparse
import shutil

DAWN_URL = 'https://dawn.googlesource.com/dawn'
DAWN_TAG = 'chromium/8120'
BUILD_DIR = ROOT / 'build'
DAWN_DIR = BUILD_DIR / 'dawn'


def download_dawn():
  print(f'Downloading Dawn ({DAWN_TAG})...')
  if not DAWN_DIR.exists():
    exec_cmd(f'git clone --branch {DAWN_TAG} --depth 1 {DAWN_URL} {DAWN_DIR}')
  else:
    exec_cmd(f'git fetch --depth 1 origin {DAWN_TAG}', cwd=str(DAWN_DIR))
    exec_cmd(f'git checkout --detach FETCH_HEAD', cwd=str(DAWN_DIR))


def create_cmake_args(platform_arch: str, build_type: str):
  base = [
    f'-DCMAKE_BUILD_TYPE={build_type}',
    '-DDAWN_FETCH_DEPENDENCIES=ON',
    '-DDAWN_BUILD_MONOLITHIC_LIBRARY=STATIC',
    '-DDAWN_ENABLE_INSTALL=ON',
    '-DDAWN_BUILD_SAMPLES=OFF',
    '-DDAWN_BUILD_TESTS=OFF',
    '-DTINT_BUILD_TESTS=OFF',
    '-DTINT_BUILD_CMD_TOOLS=OFF',
    '-DDAWN_USE_GLFW=OFF',
    '-DDAWN_BUILD_PROTOBUF=OFF',
    '-DDAWN_ENABLE_NULL=OFF',
    '-DDAWN_ENABLE_DESKTOP_GL=OFF',
    '-DDAWN_ENABLE_OPENGLES=OFF',
    '-DDAWN_ENABLE_D3D11=OFF',
  ]

  platform_args = {
    'macos-arm64': [
      '-DCMAKE_OSX_ARCHITECTURES=arm64',
      '-DCMAKE_OSX_DEPLOYMENT_TARGET=12.0',
    ],
    'ios-arm64': [
      '-DCMAKE_SYSTEM_NAME=iOS',
      '-DCMAKE_OSX_SYSROOT=iphoneos',
      '-DCMAKE_OSX_ARCHITECTURES=arm64',
      '-DCMAKE_OSX_DEPLOYMENT_TARGET=15.0',
    ],
    'ios-simulator-arm64': [
      '-DCMAKE_SYSTEM_NAME=iOS',
      '-DCMAKE_OSX_SYSROOT=iphonesimulator',
      '-DCMAKE_OSX_ARCHITECTURES=arm64',
      '-DCMAKE_OSX_DEPLOYMENT_TARGET=15.0',
    ],
  }

  if platform_arch not in platform_args: raise ValueError(f'Unsupported platform: {platform_arch}')
  return base + platform_args[platform_arch]


def build_dawn(platform_arch, build_type: str = 'Release'):
  target = f'{platform_arch}-{build_type}'
  out = BUILD_DIR / 'out' / target
  install = BUILD_DIR / 'install' / target
  args = ' '.join([
    *create_cmake_args(platform_arch, build_type),
    f'-DCMAKE_INSTALL_PREFIX={install}',
  ])

  if not out.exists(): out.mkdir(parents=True)
  if not install.exists(): install.mkdir(parents=True)
  exec_cmd(f'cmake -S {DAWN_DIR} -B {out} -G Ninja {args}')
  exec_cmd(f'cmake --build {out} --parallel')
  exec_cmd(f'cmake --install {out}')


def copy_dawn_json():
  DAWN_JSON = DAWN_DIR / 'src' / 'dawn' / 'dawn.json'
  DAWN_JSON_OUT = BUILD_DIR / 'dawn.json'
  shutil.copy(DAWN_JSON, DAWN_JSON_OUT)


def copy_dawn_header(target: str):
  DAWN_HEADER = BUILD_DIR / 'install' / target / 'include' / 'dawn' / 'webgpu.h'
  DAWN_HEADER_OUT = BUILD_DIR / 'include' / 'webgpu.h'

  # remove '#include "dawn/dawn_version.h"'
  content = DAWN_HEADER.read_text()
  content = content.replace('#include "dawn/dawn_version.h"\n', '')
  DAWN_HEADER_OUT.write_text(content)


PLATFORMS = [
  'macos-arm64',
  'ios-arm64',
  'ios-simulator-arm64',
]

BUILD_TYPES = [
  'Debug',
  'Release',
]


def build(platform: str, build_type: str):
  print(f'Building Dawn for {platform}-{build_type}')
  if not BUILD_DIR.exists(): BUILD_DIR.mkdir(parents=True)
  target = f'{platform}-{build_type}'
  download_dawn()
  copy_dawn_json()
  build_dawn(platform, build_type)
  copy_dawn_header(target)


def clean():
  # keep {DAWN_DIR}, remove everything else
  for item in BUILD_DIR.iterdir():
    if item == DAWN_DIR: continue
    if item.is_dir(): shutil.rmtree(item)
    else: item.unlink()


if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('--platform', choices=PLATFORMS)
  ap.add_argument('--build-type', choices=BUILD_TYPES, default='Release')
  ap.add_argument('--clean', action='store_true')
  args = ap.parse_args()

  if args.clean:
    clean()
  else:
    if not args.platform: raise ValueError(f'--platform must be specified: {PLATFORMS}')
    build(args.platform, args.build_type)
