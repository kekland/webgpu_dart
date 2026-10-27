import 'webgpu.g.dart';
import 'types/types.dart';

export 'types/types.dart';
export 'chained_struct.dart';
export 'webgpu.g.dart';

typedef LogCallback = void Function(LoggingType type, String message);

extension OptionalBoolExt on OptionalBool {
  bool? get asBoolean => switch (this) {
    .true_ => true,
    .false_ => false,
    .undefined => null,
    _ => throw ArgumentError('invalid OptionalBool value'),
  };
}

extension LimitsToSupportedLimits on Limits {
  SupportedLimits get asSupportedLimits => SupportedLimits(
    maxTextureDimension1D: maxTextureDimension1D!,
    maxTextureDimension2D: maxTextureDimension2D!,
    maxTextureDimension3D: maxTextureDimension3D!,
    maxTextureArrayLayers: maxTextureArrayLayers!,
    maxBindGroups: maxBindGroups!,
    maxBindGroupsPlusVertexBuffers: maxBindGroupsPlusVertexBuffers!,
    maxBindingsPerBindGroup: maxBindingsPerBindGroup!,
    maxDynamicUniformBuffersPerPipelineLayout: maxDynamicUniformBuffersPerPipelineLayout!,
    maxDynamicStorageBuffersPerPipelineLayout: maxDynamicStorageBuffersPerPipelineLayout!,
    maxSampledTexturesPerShaderStage: maxSampledTexturesPerShaderStage!,
    maxSamplersPerShaderStage: maxSamplersPerShaderStage!,
    maxStorageBuffersPerShaderStage: maxStorageBuffersPerShaderStage!,
    maxStorageTexturesPerShaderStage: maxStorageTexturesPerShaderStage!,
    maxUniformBuffersPerShaderStage: maxUniformBuffersPerShaderStage!,
    maxUniformBufferBindingSize: maxUniformBufferBindingSize!,
    maxStorageBufferBindingSize: maxStorageBufferBindingSize!,
    minUniformBufferOffsetAlignment: minUniformBufferOffsetAlignment!,
    minStorageBufferOffsetAlignment: minStorageBufferOffsetAlignment!,
    maxVertexBuffers: maxVertexBuffers!,
    maxBufferSize: maxBufferSize!,
    maxVertexAttributes: maxVertexAttributes!,
    maxVertexBufferArrayStride: maxVertexBufferArrayStride!,
    maxInterStageShaderVariables: maxInterStageShaderVariables!,
    maxColorAttachments: maxColorAttachments!,
    maxColorAttachmentBytesPerSample: maxColorAttachmentBytesPerSample!,
    maxComputeWorkgroupStorageSize: maxComputeWorkgroupStorageSize!,
    maxComputeInvocationsPerWorkgroup: maxComputeInvocationsPerWorkgroup!,
    maxComputeWorkgroupSizeX: maxComputeWorkgroupSizeX!,
    maxComputeWorkgroupSizeY: maxComputeWorkgroupSizeY!,
    maxComputeWorkgroupSizeZ: maxComputeWorkgroupSizeZ!,
    maxComputeWorkgroupsPerDimension: maxComputeWorkgroupsPerDimension!,
    maxImmediateSize: maxImmediateSize!,
  );
}

/// A utility class that represents a view into a [Buffer].
extension type BufferView._((Buffer buffer, int offset, int size) _) {
  BufferView(Buffer buffer, {int offset = 0, int? size}) : this._((buffer, offset, size ?? buffer.size));

  Buffer get buffer => _.$1;
  int get offset => _.$2;
  int get size => _.$3;
}
