#!/usr/bin/env -S fvm dart run

import 'dart:io';

import 'package:js_interop_gen/src/cli.dart' as cli;

void main() async {
  final rootDir = Platform.script.resolve('../');

  // Download js_interop_gen from github
  final jsInteropGenUrl = 'https://github.com/dart-lang/web';
  final jsInteropGenDir = rootDir.resolve('build/web').toFilePath();
  if (!Directory(jsInteropGenDir).existsSync()) {
    await cli.runProc('git', ['clone', jsInteropGenUrl, jsInteropGenDir], workingDirectory: rootDir.toFilePath());
  } else {
    await cli.runProc('git', ['pull'], workingDirectory: jsInteropGenDir);
  }

  final jsInteropGenPath = rootDir.resolve('build/web/js_interop_gen/lib/src').toFilePath();
  final webGeneratorPath = rootDir.resolve('build/web/web_generator').toFilePath();
  final bcdPath = rootDir
      .resolve('build/web/web_generator/node_modules/@mdn/browser-compat-data/data.json')
      .toFilePath();
  
  final shimIdl = rootDir.resolve('tool/idl/webgpu_shim.idl').toFilePath();
  final webgpuIdl = rootDir.resolve('tool/idl/webgpu.idl').toFilePath();

  await cli.runProc('npm', ['install'], workingDirectory: jsInteropGenPath);
  await cli.runProc('npm', ['install'], workingDirectory: webGeneratorPath);
  await cli.compileDartMain(langVersion: '3.13.0', dir: jsInteropGenPath);
  await cli.runNode([
    'main.mjs',
    '--idl',
    '--generate-all',
    '--bcd-json=$bcdPath',
    '--input=$shimIdl',
    '--input=$webgpuIdl',
    '--output=.',
  ], workingDirectory: jsInteropGenPath);

  final out = rootDir.resolve('lib/web/webgpu.g.dart').toFilePath();
  await File('$jsInteropGenPath/webgpu.dart').copy(out);

  // fix import
  var content = await File(out).readAsString();
  content = content.replaceAll(
    "import 'webgpu_shim.dart';",
    "import 'package:web/web.dart';",
  );

  content = content.replaceAll(
    'extension type GPU._',
    'extension type GPU',
  );

  await File(out).writeAsString(content);
}
