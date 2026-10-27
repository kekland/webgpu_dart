part of '../../generator.dart';

List<String> generateRenderPipeline(
  FunctionInfo vertexFunc,
  FunctionInfo fragmentFunc,
  Map<int, Map<int, VariableInfo>> groups,
  bool isOnlyPipeline,
) {
  final lines = <String>[];

  final capVertexFuncName = vertexFunc.capDartName;
  final capFragmentFuncName = fragmentFunc.capDartName;

  final _groups = <int, Map<int, VariableInfo>>{};
  for (final resource in vertexFunc.resources) {
    _groups[resource.group] ??= {};
    _groups[resource.group]![resource.binding] = groups[resource.group]![resource.binding]!;
  }
  for (final resource in fragmentFunc.resources) {
    _groups[resource.group] ??= {};
    _groups[resource.group]![resource.binding] = groups[resource.group]![resource.binding]!;
  }

  lines.addAll(generatePipelineLayout([capVertexFuncName, capFragmentFuncName], _groups));
  lines.add('');

  final createPipelineLayoutFn = 'create$capVertexFuncName${capFragmentFuncName}PipelineLayout';

  final fnName = isOnlyPipeline
      ? 'createRenderPipeline'
      : 'create$capVertexFuncName${capFragmentFuncName}RenderPipeline';

  lines.addAll(generatePipelineBindings([fnName], _groups, isOnlyPipeline, passType: 'RenderPass'));
  lines.add('');

  lines.add(_metaRenderPipeline(vertexFunc.name, fragmentFunc.name));
  lines.add('webgpu.RenderPipeline $fnName(');
  lines.add('  webgpu.Device device,');
  lines.add('  List<webgpu.ColorTargetState> targets, {');
  lines.add('  webgpu.ShaderModule? module,');
  lines.add('  webgpu.PipelineLayout? layout,');
  lines.add('  Overrides? overrides,');
  lines.add('  webgpu.PrimitiveState primitive = const webgpu.PrimitiveState(),');
  lines.add('  webgpu.MultisampleState multisample = const webgpu.MultisampleState(),');
  lines.add('  webgpu.DepthStencilState? depthStencil,');
  lines.add('  List<webgpu.VertexBufferLayout>? vertexBuffers,');
  lines.add('}) {');
  lines.add('  final _module = module ?? createShaderModule(device);');
  lines.add('  return device.createRenderPipeline(.new(');
  lines.add('   label: ${_wgpuLabel('${vertexFunc.name}-${fragmentFunc.name} render pipeline')},');
  lines.add('   layout: layout ?? $createPipelineLayoutFn(device),');
  lines.add('   vertex: ${vertexFunc.createStateFn}(_module, overrides: overrides, vertexBuffers: vertexBuffers),');
  lines.add('   fragment: ${fragmentFunc.createStateFn}(_module, targets, overrides: overrides),');
  lines.add('   primitive: primitive,');
  lines.add('   multisample: multisample,');
  lines.add('   depthStencil: depthStencil,');
  lines.add(' ));');
  lines.add('}');

  return lines;
}
