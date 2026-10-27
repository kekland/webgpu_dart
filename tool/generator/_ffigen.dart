#!/usr/bin/env -S fvm dart run

import 'dart:io';

// ignore: depend_on_referenced_packages
import 'package:ffigen/ffigen.dart' as ffigen;

void main() {
  final root = Platform.script.resolve('../../');

  final visitor = ffigen.Visitor(
    func: (node) {
      node.isIncluded = true;
      node.exposeSymbolAddress = node.originalName.endsWith('Release') || node.originalName.endsWith('destroy');
    },
    macroConstant: (n) => n.isIncluded = true,
    typealias: (n) => n.isIncluded = .always,
    global: (n) => n.isIncluded = true,
    enumClass: (n) {
      n.isIncluded = true;
      n.style = .intConstants;
    },
    struct: (n) => n.isIncluded = true,
    union: (n) => n.isIncluded = true,
  );

  // webgpu.h
  ffigen.FfiGenerator(
    input: .new(
      entryPoints: [root.resolve('build/include/webgpu.h')],
      appendCompilerOptions: true,
    ),
    output: .new(
      dart: .new(path: root.resolve('lib/native/dawn_bindings.g.dart')),
      style: ffigen.NativeExternalBindings(assetId: 'package:webgpu/src/asset.dart'),
      preamble: '// ignore_for_file: camel_case_types, non_constant_identifier_names, unused_element, unused_field, return_of_invalid_type, void_checks, annotate_overrides, no_leading_underscores_for_local_identifiers, library_private_types_in_public_api, todo',
    ),
    visitors: [visitor],
  ).generate();

  // darwin
  ffigen.FfiGenerator(
    input: .new(
      entryPoints: [root.resolve('src/platform/darwin.h')],
      compilerOptions: ['-Ibuild/include', '-Isrc'],
      appendCompilerOptions: true,
    ),
    output: .new(
      dart: .new(path: root.resolve('lib/native/darwin/darwin_bindings.g.dart')),
      style: ffigen.NativeExternalBindings(assetId: 'package:webgpu/src/asset.dart'),
      preamble: '// ignore_for_file: camel_case_types, non_constant_identifier_names, unused_element, unused_field, return_of_invalid_type, void_checks, annotate_overrides, no_leading_underscores_for_local_identifiers, library_private_types_in_public_api, todo',
    ),
    visitors: [visitor],
  ).generate();
}
