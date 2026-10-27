#!/usr/bin/env python3

import sys
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).parent.parent
subprocess.run(['fvm', 'dart', 'compile', 'exe', 'bin/wgslgen.dart', '-o', 'build/wgslgen'], cwd=ROOT)
