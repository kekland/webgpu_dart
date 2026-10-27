part of '../../generator.dart';

List<String> generateVertexState(FunctionInfo funcInfo) {
  final lines = <String>[];
  final vertexBufferLayoutFn = funcInfo.vertexBuffer != null ? funcInfo.vertexBufferLayoutFn : null;

  lines.add(_metaVertexState(funcInfo.name));
  lines.add('webgpu.VertexState ${funcInfo.createStateFn}(');
  lines.add('  webgpu.ShaderModule module, {');
  lines.add('  Overrides? overrides,');
  lines.add('  List<webgpu.VertexBufferLayout>? vertexBuffers,');
  lines.add('}) => webgpu.VertexState(');
  lines.add('  module: module,');
  lines.add('  entryPoint: \'${funcInfo.name}\',');
  lines.add('  constants: overrides?.entries ?? const [],');
  if (vertexBufferLayoutFn != null) {
    lines.add('  buffers: vertexBuffers ?? [$vertexBufferLayoutFn()],');
  } else {
    lines.add('  buffers: vertexBuffers ?? const [],');
  }
  lines.add(');');

  return lines;
}
