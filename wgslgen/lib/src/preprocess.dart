import 'dart:io';

final _includeRegex = RegExp(r'#import\s+"([^"]+)"');
final _defineImportPathRegex = RegExp(r'#define_import_path\s+(\w+)');
final _defineRegex = RegExp(r'^\s*#define\s+(\w+)(?:\s+(.+))?$');
final _undefRegex = RegExp(r'#undef\s+(\w+)');
final _ifdefRegex = RegExp(r'#ifdef\s+(\w+)');
final _ifndefRegex = RegExp(r'#ifndef\s+(\w+)');
final _endifRegex = RegExp(r'#endif');

/// Preprocesses directives in WGSL.
String preprocessWgsl(File file, String content, {Set<Uri>? includedFiles, Map<String, String>? defines}) {
  final _includedFiles = includedFiles ?? {};
  final _defines = defines ?? {};

  final baseDirUri = file.parent.uri;

  final lines = content.split('\n');
  final processedLines = <String>[];

  final skipStack = <bool>[];
  for (var rawLine in lines) {
    final line = rawLine.trim();

    final ifdefMatch = _ifdefRegex.firstMatch(line);
    final ifndefMatch = _ifndefRegex.firstMatch(line);
    final endifMatch = _endifRegex.firstMatch(line);

    if (ifdefMatch != null) {
      final name = ifdefMatch.group(1)!;
      final active = skipStack.every((e) => e);
      skipStack.add(active && _defines.containsKey(name));
      continue;
    }

    if (ifndefMatch != null) {
      final name = ifndefMatch.group(1)!;
      final active = skipStack.every((e) => e);
      skipStack.add(active && !_defines.containsKey(name));
      continue;
    }

    if (endifMatch != null) {
      if (skipStack.isNotEmpty) skipStack.removeLast();
      continue;
    }

    if (skipStack.any((e) => !e)) continue;

    final includeMatch = _includeRegex.firstMatch(line);
    final defineImportPathMatch = _defineImportPathRegex.firstMatch(line);
    final defineMatch = _defineRegex.firstMatch(line);
    final undefMatch = _undefRegex.firstMatch(line);

    if (includeMatch != null) {
      final includePath = includeMatch.group(1)!;
      final includeUri = baseDirUri.resolve(includePath);
      if (_includedFiles.contains(includeUri)) continue;
      _includedFiles.add(includeUri);

      final includeFile = File.fromUri(includeUri);
      if (!includeFile.existsSync()) throw Exception('Included file "${includeFile.path}" does not exist.');

      final includeContent = includeFile.readAsStringSync();
      var processedInclude = preprocessWgsl(
        includeFile,
        includeContent,
        includedFiles: _includedFiles,
        defines: _defines,
      ).split('\n');

      while (processedInclude.isNotEmpty && processedInclude.first.trim().isEmpty) processedInclude.removeAt(0);
      while (processedInclude.isNotEmpty && processedInclude.last.trim().isEmpty) processedInclude.removeLast();

      processedLines.add('// import "$includePath"');
      processedLines.addAll(processedInclude);
      processedLines.add('// end import "$includePath"');
      processedLines.add('');
    } else if (defineImportPathMatch != null) {
      // Ignore the line
    } else if (defineMatch != null) {
      final name = defineMatch.group(1)!;
      final value = defineMatch.group(2) ?? '';
      _defines[name] = value;
    } else if (undefMatch != null) {
      final name = undefMatch.group(1)!;
      _defines.remove(name);
    } else {
      processedLines.add(line);
    }
  }

  return processedLines.join('\n');
}
