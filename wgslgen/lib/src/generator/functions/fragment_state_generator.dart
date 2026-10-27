part of '../../generator.dart';

List<String> generateFragmentState(FunctionInfo funcInfo) {
  final lines = <String>[];

  lines.add(_metaFragmentState(funcInfo.name));
  lines.add('webgpu.FragmentState ${funcInfo.createStateFn}(');
  lines.add('  webgpu.ShaderModule module,');
  lines.add('  List<webgpu.ColorTargetState> targets, {');
  lines.add('  Overrides? overrides,');
  lines.add('}) => webgpu.FragmentState(');
  lines.add('  module: module,');
  lines.add('  entryPoint: \'${funcInfo.name}\',');
  lines.add('  constants: overrides?.entries ?? const [],');
  lines.add('  targets: targets,');
  lines.add(');');

  return lines;
}
