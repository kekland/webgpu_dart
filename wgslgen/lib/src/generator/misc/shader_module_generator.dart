part of '../../generator.dart';

List<String> generateShaderModule(String name, String source) {
  final lines = <String>[];

  lines.add(_metaShaderSource(name));
  lines.add('const String _shaderSource = r\'\'\'');
  lines.add(source);
  lines.add('\'\'\';');
  lines.add('');

  lines.add(_metaShaderModule(name));
  lines.add('webgpu.ShaderModule createShaderModule(webgpu.Device device) => device.createShaderModule(.new(');
  lines.add('  label: \'($name) module\',');
  lines.add('  next: const webgpu.ShaderSourceWGSL(code: _shaderSource),');
  lines.add('));');

  return lines;
}
