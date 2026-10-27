part of '../../generator.dart';

List<String> generateComputeState(FunctionInfo funcInfo) {
  final lines = <String>[];

  lines.add(_metaComputeState(funcInfo.name));
  lines.add('webgpu.ComputeState ${funcInfo.createStateFn}(');
  lines.add('  webgpu.ShaderModule module, {');
  lines.add('  Overrides? overrides,');
  lines.add('}) => webgpu.ComputeState(');
  lines.add('  module: module,');
  lines.add('  entryPoint: \'${funcInfo.name}\',');
  lines.add('  constants: overrides?.entries ?? const [],');
  lines.add(');');

  return lines;
}
