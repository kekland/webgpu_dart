part of 'dawn.g.dart';

final class Instance extends _InstanceBase implements webgpu.Instance {
  Instance._(super.ptr) : super._() {
    webgpu.Instance.ensureInitialized();
    _EventLoop._registerInstance(this);
  }

  Instance._borrowed(super.ptr) : super._borrowed();
  factory Instance.create([InstanceDescriptor? descriptor]) => _createInstance(descriptor);

  void processEvents() => _processEvents();

  @override
  Future<Adapter> requestAdapter([RequestAdapterOptions? options]) async {
    final result = await _requestAdapter(options);
    if (result == null) throw StateError('failed to request adapter');
    return result;
  }

  Surface createSurface(SurfaceDescriptor descriptor) => _createSurface(descriptor);

  @override
  void dispose() {
    _EventLoop._removeInstance(this);
    super.dispose();
  }
}

final class Adapter extends _AdapterBase implements webgpu.Adapter {
  Adapter._(super.ptr) : super._();
  Adapter._borrowed(super.ptr) : super._borrowed();

  @override
  Future<Device> requestDevice(DeviceDescriptor? descriptor) async {
    final result = await _requestDevice(descriptor);
    if (result == null) throw StateError('failed to request device');
    return result;
  }

  @override
  Future<Device> requestDefaultDevice() {
    return requestDevice(platformDeviceDescriptor);
  }
}

final class BindGroupLayout extends _BindGroupLayoutBase implements webgpu.BindGroupLayout {
  BindGroupLayout._(super.ptr) : super._();
  BindGroupLayout._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);
}

final class BindGroup extends _BindGroupBase implements webgpu.BindGroup {
  BindGroup._(super.ptr) : super._();
  BindGroup._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);
}

final class Buffer extends _BufferBase implements webgpu.Buffer {
  Buffer._(super.ptr) : super._();
  Buffer._borrowed(super.ptr) : super._borrowed();

  late final _impl = webgpu.BufferImpl(this);

  @override
  BufferMapState get mapState => _getMapState();

  @override
  int get size => _getSize();

  @override
  BufferUsage get usage => _getUsage();

  @override
  set label(String label) => _setLabel(label);

  // ----
  // Mapping
  // ----

  @override
  Future<void> mapAsync({int offset = 0, int? size, MapMode mode = .read}) {
    return _impl.mapAsync(offset: offset, size: size, mode: mode);
  }

  @override
  void mapSync({int offset = 0, int? size, MapMode mode = .read}) {
    return _impl.mapSync(offset: offset, size: size, mode: mode);
  }

  @override
  TypedData getMappedRange(int offset, int size, {bool readOnly = false}) {
    return _impl.getMappedRange(offset, size, readOnly: readOnly);
  }

  @override
  void writeMappedRange(TypedData data, {int offset = 0}) {
    return _impl.writeMappedRange(data, offset: offset);
  }

  @override
  void unmap() {
    return _impl.unmap();
  }

  @override
  Future<void> internalMapAsync(MapMode mode, int offset, int size) {
    return _mapAsync(mode, offset, size);
  }

  @override
  void internalMapSync(MapMode mode, int offset, int size) {
    return _mapSync(mode, offset, size);
  }

  @override
  TypedData internalGetMappedRange(int offset, int size, {bool readOnly = false}) {
    final ptr = readOnly ? _getConstMappedRange(offset, size) : _getMappedRange(offset, size);
    if (ptr == ffi.nullptr) {
      throw StateError('wgpuBufferGetMappedRange validation failed for range ($offset, ${offset + size}).');
    }

    final view = ptr.cast<ffi.Uint8>().asTypedList(size);
    return view;
  }

  @override
  void internalWriteMappedRange(TypedData data, {int offset = 0}) {
    final status = _writeMappedRange(offset, data);
    if (status != .success) throw StateError('wgpuBufferWriteMappedRange failed: $status');
    return;
  }

  @override
  void internalUnmap() {
    _unmap();
  }

  @override
  void destroy() {
    _destroy();
  }
}

final class CommandBuffer extends _CommandBufferBase implements webgpu.CommandBuffer {
  CommandBuffer._(super.ptr) : super._();
  CommandBuffer._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);
}

final class CommandEncoder extends _CommandEncoderBase implements webgpu.CommandEncoder {
  CommandEncoder._(super.ptr) : super._();
  CommandEncoder._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);

  @override
  ComputePassEncoder beginComputePass([ComputePassDescriptor? descriptor]) {
    return _beginComputePass(descriptor);
  }

  @override
  RenderPassEncoder beginRenderPass(RenderPassDescriptor descriptor) {
    return _beginRenderPass(descriptor);
  }

  @override
  void copyTextureToBuffer(
    webgpu.TexelCopyTextureInfo source,
    webgpu.TexelCopyBufferInfo destination,
    webgpu.Extent3D copySize,
  ) {
    _copyTextureToBuffer(source, destination, copySize);
  }

  @override
  CommandBuffer finish([CommandBufferDescriptor? descriptor]) {
    return _finish(descriptor);
  }

  @override
  void clearBuffer(Buffer buffer, {int offset = 0, int? size}) {
    _clearBuffer(buffer, offset, size ?? (buffer.size - offset));
  }

  @override
  void copyBufferToBuffer(
    Buffer source,
    Buffer destination, {
    int sourceOffset = 0,
    int destinationOffset = 0,
    required int size,
  }) {
    _copyBufferToBuffer(source, sourceOffset, destination, destinationOffset, size);
  }

  @override
  void copyBufferToTexture(
    webgpu.TexelCopyBufferInfo source,
    webgpu.TexelCopyTextureInfo destination,
    webgpu.Extent3D copySize,
  ) {
    _copyBufferToTexture(source, destination, copySize);
  }

  @override
  void insertDebugMarker(String markerLabel) {
    _insertDebugMarker(markerLabel);
  }

  @override
  void pushDebugGroup(String groupLabel) {
    _pushDebugGroup(groupLabel);
  }

  @override
  void popDebugGroup() {
    _popDebugGroup();
  }

  @override
  void resolveQuerySet(
    QuerySet querySet,
    Buffer destination, {
    required int firstQuery,
    required int queryCount,
    required int destinationOffset,
  }) {
    _resolveQuerySet(querySet, firstQuery, queryCount, destination, destinationOffset);
  }

  void writeTimestamp(QuerySet querySet, int queryIndex) {
    _writeTimestamp(querySet, queryIndex);
  }
}

final class ComputePassEncoder extends _ComputePassEncoderBase implements webgpu.ComputePassEncoder {
  ComputePassEncoder._(super.ptr) : super._();
  ComputePassEncoder._borrowed(super.ptr) : super._borrowed();

  @override
  void dispatchWorkgroups(int x, [int? y, int? z]) {
    _dispatchWorkgroups(x, y ?? 1, z ?? 1);
  }

  @override
  void dispatchWorkgroupsIndirect(Buffer indirectBuffer, {int indirectOffset = 0}) {
    _dispatchWorkgroupsIndirect(indirectBuffer, indirectOffset);
  }

  @override
  void end() {
    _end();
  }

  @override
  void insertDebugMarker(String markerLabel) {
    _insertDebugMarker(markerLabel);
  }

  @override
  set label(String value) {
    _setLabel(value);
  }

  @override
  void popDebugGroup() {
    _popDebugGroup();
  }

  @override
  void pushDebugGroup(String groupLabel) {
    _pushDebugGroup(groupLabel);
  }

  @override
  void setBindGroup(int index, BindGroup? bindGroup, {Uint32List? dynamicOffsets}) {
    _setBindGroup(index, bindGroup, dynamicOffsets);
  }

  @override
  void setImmediates(int offset, TypedData data) {
    _setImmediates(offset, data);
  }

  @override
  void setPipeline(ComputePipeline pipeline) {
    _setPipeline(pipeline);
  }
}

final class ComputePipeline extends _ComputePipelineBase implements webgpu.ComputePipeline {
  ComputePipeline._(super.ptr) : super._();
  ComputePipeline._borrowed(super.ptr) : super._borrowed();

  @override
  BindGroupLayout getBindGroupLayout(int index) => _getBindGroupLayout(index);

  @override
  set label(String value) => _setLabel(value);
}

final class Device extends _DeviceBase implements webgpu.Device {
  Device._(super.ptr) : super._();
  Device._borrowed(super.ptr) : super._borrowed();

  @override
  Buffer createBuffer(webgpu.BufferDescriptor descriptor) {
    final result = _createBuffer(descriptor);
    if (result == null) throw StateError('failed to create buffer');
    return result;
  }

  @override
  Texture createTexture(webgpu.TextureDescriptor descriptor) => _createTexture(descriptor);

  @override
  late final Queue queue = _getQueue();

  @override
  CommandEncoder createCommandEncoder([webgpu.CommandEncoderDescriptor? descriptor]) =>
      _createCommandEncoder(descriptor);

  @override
  RenderPipeline createRenderPipeline(webgpu.RenderPipelineDescriptor descriptor) => _createRenderPipeline(descriptor);

  @override
  ShaderModule createShaderModule(webgpu.ShaderModuleDescriptor descriptor) => _createShaderModule(descriptor);

  @override
  BindGroupLayout createBindGroupLayout(webgpu.BindGroupLayoutDescriptor descriptor) =>
      _createBindGroupLayout(descriptor);

  @override
  BindGroup createBindGroup(webgpu.BindGroupDescriptor descriptor) => _createBindGroup(descriptor);

  @override
  AdapterInfo get adapterInfo => _getAdapterInfo();

  @override
  ComputePipeline createComputePipeline(webgpu.ComputePipelineDescriptor descriptor) {
    return _createComputePipeline(descriptor);
  }

  @override
  Future<ComputePipeline?> createComputePipelineAsync(webgpu.ComputePipelineDescriptor descriptor) {
    return _createComputePipelineAsync(descriptor);
  }

  @override
  PipelineLayout createPipelineLayout(webgpu.PipelineLayoutDescriptor descriptor) {
    return _createPipelineLayout(descriptor);
  }

  @override
  QuerySet createQuerySet(webgpu.QuerySetDescriptor descriptor) {
    return _createQuerySet(descriptor);
  }

  @override
  RenderBundleEncoder createRenderBundleEncoder(webgpu.RenderBundleEncoderDescriptor descriptor) {
    return _createRenderBundleEncoder(descriptor);
  }

  @override
  Future<RenderPipeline?> createRenderPipelineAsync(webgpu.RenderPipelineDescriptor descriptor) {
    return _createRenderPipelineAsync(descriptor);
  }

  @override
  Sampler createSampler(webgpu.SamplerDescriptor descriptor) {
    return _createSampler(descriptor);
  }

  @override
  webgpu.SupportedFeatures get features => _getFeatures();

  bool hasFeature(webgpu.FeatureName feature) {
    return _hasFeature(feature);
  }

  @override
  set label(String value) => _setLabel(value);

  @override
  webgpu.SupportedLimits get limits => _getLimits().asSupportedLimits;

  @override
  Future<webgpu.ErrorType> popErrorScope() {
    return _popErrorScope();
  }

  @override
  void pushErrorScope(webgpu.ErrorFilter filter) {
    _pushErrorScope(filter);
  }

  ResourceTable createResourceTable(ResourceTableDescriptor descriptor) {
    return _createResourceTable(descriptor);
  }

  SharedBufferMemory importSharedBufferMemory(SharedBufferMemoryDescriptor descriptor) {
    return _importSharedBufferMemory(descriptor);
  }

  SharedTextureMemory importSharedTextureMemory(SharedTextureMemoryDescriptor descriptor) {
    return _importSharedTextureMemory(descriptor);
  }

  SharedFence importSharedFence(SharedFenceDescriptor descriptor) {
    return _importSharedFence(descriptor);
  }

  @override
  void setLogCallback(webgpu.LogCallback callback) {
    _using((allocator) {
      final info = _LoggingCallback$ToInfoRepeating(allocator, callback);
      bindings.wgpuDeviceSetLoggingCallback(_ptr, info.ref);
    });
  }

  @override
  void destroy() {
    _destroy();
  }
}

extension DeviceDawnExtension on webgpu.Device {
  ResourceTable createResourceTable(ResourceTableDescriptor descriptor) {
    return (this as Device).createResourceTable(descriptor);
  }

  SharedBufferMemory importSharedBufferMemory(SharedBufferMemoryDescriptor descriptor) {
    return (this as Device).importSharedBufferMemory(descriptor);
  }

  SharedTextureMemory importSharedTextureMemory(SharedTextureMemoryDescriptor descriptor) {
    return (this as Device).importSharedTextureMemory(descriptor);
  }

  SharedFence importSharedFence(SharedFenceDescriptor descriptor) {
    return (this as Device).importSharedFence(descriptor);
  }
}

final class ExternalTexture extends _ExternalTextureBase implements webgpu.ExternalTexture {
  ExternalTexture._(super.ptr) : super._();
  ExternalTexture._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);
}

final class PipelineLayout extends _PipelineLayoutBase implements webgpu.PipelineLayout {
  PipelineLayout._(super.ptr) : super._();
  PipelineLayout._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);
}

final class QuerySet extends _QuerySetBase implements webgpu.QuerySet {
  QuerySet._(super.ptr) : super._();
  QuerySet._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);

  @override
  int get count => _getCount();

  @override
  webgpu.QueryType get type => _getType();

  @override
  void destroy() => _destroy();
}

final class Queue extends _QueueBase implements webgpu.Queue {
  Queue._(super.ptr) : super._();
  Queue._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String label) => _setLabel(label);

  @override
  Future<void> onSubmittedWorkDone() => _onSubmittedWorkDone();

  @override
  void submit(List<webgpu.CommandBuffer> commandBuffers) => _submit(commandBuffers.cast());

  @override
  void writeBuffer(covariant Buffer buffer, int bufferOffset, TypedData data) {
    _writeBuffer(buffer, bufferOffset, data);
  }

  @override
  void writeTexture(
    webgpu.TexelCopyTextureInfo destination,
    TypedData data,
    webgpu.TexelCopyBufferLayout layout,
    webgpu.Extent3D writeSize,
  ) {
    _writeTexture(destination, data, layout, writeSize);
  }
}

final class RenderBundleEncoder extends _RenderBundleEncoderBase implements webgpu.RenderBundleEncoder {
  RenderBundleEncoder._(super.ptr) : super._();
  RenderBundleEncoder._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);

  @override
  void draw(int vertexCount, {int instanceCount = 1, int firstVertex = 0, int firstInstance = 0}) {
    _draw(vertexCount, instanceCount, firstVertex, firstInstance);
  }

  @override
  void drawIndexed(
    int indexCount, {
    int instanceCount = 1,
    int firstIndex = 0,
    int baseVertex = 0,
    int firstInstance = 0,
  }) {
    _drawIndexed(indexCount, instanceCount, firstIndex, baseVertex, firstInstance);
  }

  @override
  void drawIndexedIndirect(Buffer indirectBuffer, {int offset = 0}) {
    _drawIndexedIndirect(indirectBuffer, offset);
  }

  @override
  void drawIndirect(Buffer indirectBuffer, {int offset = 0}) {
    _drawIndirect(indirectBuffer, offset);
  }

  @override
  RenderBundle finish([RenderBundleDescriptor? descriptor]) {
    return _finish(descriptor);
  }

  @override
  void insertDebugMarker(String markerLabel) {
    _insertDebugMarker(markerLabel);
  }

  @override
  void popDebugGroup() {
    _popDebugGroup();
  }

  @override
  void pushDebugGroup(String groupLabel) {
    _pushDebugGroup(groupLabel);
  }

  @override
  void setBindGroup(int index, BindGroup? bindGroup, {Uint32List? dynamicOffsets}) {
    _setBindGroup(index, bindGroup, dynamicOffsets);
  }

  @override
  void setImmediates(int offset, TypedData data) {
    _setImmediates(offset, data);
  }

  @override
  void setIndexBuffer(Buffer buffer, webgpu.IndexFormat format, {int offset = 0, int? size}) {
    return _setIndexBuffer(buffer, format, offset, size ?? (buffer.size - offset));
  }

  @override
  void setPipeline(RenderPipeline pipeline) {
    return _setPipeline(pipeline);
  }

  @override
  void setVertexBuffer(int slot, Buffer? buffer, {int offset = 0, int? size}) {
    if (buffer == null) return _setVertexBuffer(slot, buffer, offset, 0);
    return _setVertexBuffer(slot, buffer, offset, size ?? (buffer.size - offset));
  }
}

final class RenderBundle extends _RenderBundleBase implements webgpu.RenderBundle {
  RenderBundle._(super.ptr) : super._();
  RenderBundle._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);
}

final class RenderPassEncoder extends _RenderPassEncoderBase implements webgpu.RenderPassEncoder {
  RenderPassEncoder._(super.ptr) : super._();
  RenderPassEncoder._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);

  @override
  void end() => _end();

  @override
  void setPipeline(RenderPipeline pipeline) => _setPipeline(pipeline);

  @override
  void setBindGroup(int index, BindGroup? bindGroup, {Uint32List? dynamicOffsets}) {
    _setBindGroup(index, bindGroup, dynamicOffsets);
  }

  @override
  void beginOcclusionQuery(int queryIndex) {
    _beginOcclusionQuery(queryIndex);
  }

  @override
  void draw(int vertexCount, {int instanceCount = 1, int firstVertex = 0, int firstInstance = 0}) {
    _draw(vertexCount, instanceCount, firstVertex, firstInstance);
  }

  @override
  void drawIndexed(
    int indexCount, {
    int instanceCount = 1,
    int firstIndex = 0,
    int baseVertex = 0,
    int firstInstance = 0,
  }) {
    _drawIndexed(indexCount, instanceCount, firstIndex, baseVertex, firstInstance);
  }

  @override
  void drawIndexedIndirect(Buffer indirectBuffer, {int offset = 0}) {
    _drawIndexedIndirect(indirectBuffer, offset);
  }

  @override
  void drawIndirect(Buffer indirectBuffer, {int offset = 0}) {
    _drawIndirect(indirectBuffer, offset);
  }

  @override
  void endOcclusionQuery() {
    _endOcclusionQuery();
  }

  @override
  void executeBundles(List<webgpu.RenderBundle> bundles) {
    _executeBundles(bundles.cast());
  }

  @override
  void insertDebugMarker(String markerLabel) {
    _insertDebugMarker(markerLabel);
  }

  @override
  void popDebugGroup() {
    _popDebugGroup();
  }

  @override
  void pushDebugGroup(String groupLabel) {
    _pushDebugGroup(groupLabel);
  }

  @override
  void setBlendConstant(webgpu.Color color) {
    _setBlendConstant(color);
  }

  @override
  void setImmediates(int offset, TypedData data) {
    _setImmediates(offset, data);
  }

  @override
  void setIndexBuffer(Buffer buffer, webgpu.IndexFormat format, {int offset = 0, int? size}) {
    _setIndexBuffer(buffer, format, offset, size ?? (buffer.size - offset));
  }

  @override
  void setScissorRect({int x = 0, int y = 0, int width = 0, int height = 0}) {
    _setScissorRect(x, y, width, height);
  }

  @override
  void setStencilReference(int reference) {
    _setStencilReference(reference);
  }

  @override
  void setVertexBuffer(int slot, Buffer? buffer, {int offset = 0, int? size}) {
    if (buffer == null) return _setVertexBuffer(slot, buffer, offset, 0);
    _setVertexBuffer(slot, buffer, offset, size ?? (buffer.size - offset));
  }

  @override
  void setViewport({
    double x = 0,
    double y = 0,
    double width = 0,
    double height = 0,
    double minDepth = 0,
    double maxDepth = 1,
  }) {
    _setViewport(x, y, width, height, minDepth, maxDepth);
  }
}

final class RenderPipeline extends _RenderPipelineBase implements webgpu.RenderPipeline {
  RenderPipeline._(super.ptr) : super._();
  RenderPipeline._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);

  @override
  BindGroupLayout getBindGroupLayout(int index) => _getBindGroupLayout(index);
}

final class Sampler extends _SamplerBase implements webgpu.Sampler {
  Sampler._(super.ptr) : super._();
  Sampler._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);
}

final class ShaderModule extends _ShaderModuleBase implements webgpu.ShaderModule {
  ShaderModule._(super.ptr) : super._();
  ShaderModule._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);

  @override
  Future<webgpu.CompilationInfo> get compilationInfo => _getCompilationInfo();
}

final class Surface extends _SurfaceBase implements webgpu.Surface {
  Surface._(super.ptr) : super._();
  Surface._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);

  @override
  webgpu.SurfaceTexture get currentTexture => _getCurrentTexture();

  @override
  webgpu.SurfaceCapabilities getCapabilities(Adapter adapter) => _getCapabilities(adapter);

  @override
  void configure(webgpu.SurfaceConfiguration configuration) {
    _configure(configuration);
  }

  @override
  webgpu.Status present() {
    return _present();
  }

  @override
  void unconfigure() {
    _unconfigure();
  }
}

final class TextureView extends _TextureViewBase implements webgpu.TextureView {
  TextureView._(super.ptr) : super._();
  TextureView._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);
}

final class Texture extends _TextureBase implements webgpu.Texture {
  Texture._(super.ptr) : super._();
  Texture._borrowed(super.ptr) : super._borrowed();

  @override
  set label(String value) => _setLabel(value);

  @override
  TextureView createView([TextureViewDescriptor? descriptor]) => _createView(descriptor);

  @override
  int get depthOrArrayLayers => _getDepthOrArrayLayers();

  @override
  webgpu.TextureDimension get dimension => _getDimension();

  @override
  webgpu.TextureFormat get format => _getFormat();

  @override
  int get height => _getHeight();

  @override
  int get mipLevelCount => _getMipLevelCount();

  @override
  int get sampleCount => _getSampleCount();

  @override
  webgpu.TextureViewDimension get textureBindingViewDimension => _getTextureBindingViewDimension();

  @override
  webgpu.TextureUsage get usage => _getUsage();

  @override
  int get width => _getWidth();

  @override
  void destroy() => _destroy();
}

final class TexelBufferView extends _TexelBufferViewBase {
  TexelBufferView._(super.ptr) : super._();
  TexelBufferView._borrowed(super.ptr) : super._borrowed();

  set label(String value) => _setLabel(value);
}

final class ResourceTable extends _ResourceTableBase {
  ResourceTable._(super.ptr) : super._();
  ResourceTable._borrowed(super.ptr) : super._borrowed();

  set label(String value) => _setLabel(value);

  int get size => _getSize();
  Status update(int slot, BindingResource resource) => _update(slot, resource);
  int insert(BindingResource resource) => _insert(resource);
  Status remove(int slot) => _remove(slot);

  void destroy() => _destroy();
}

final class SharedFence extends _SharedFenceBase {
  SharedFence._(super.ptr) : super._();
  SharedFence._borrowed(super.ptr) : super._borrowed();

  set label(String value) => _setLabel(value);

  SharedFenceExportInfo exportInfo({List<SType> extensions = const []}) => _exportInfo(extensions: extensions);
}

final class SharedTextureMemory extends _SharedTextureMemoryBase {
  SharedTextureMemory._(super.ptr) : super._();
  SharedTextureMemory._borrowed(super.ptr) : super._borrowed();

  set label(String value) => _setLabel(value);
  SharedTextureMemoryProperties get properties => _getProperties();
  Texture createTexture(TextureDescriptor? descriptor) => _createTexture(descriptor);
  Status beginAccess(Texture texture, SharedTextureMemoryBeginAccessDescriptor descriptor) =>
      _beginAccess(texture, descriptor);
  SharedTextureMemoryEndAccessState endAccess(Texture texture) => _endAccess(texture);
  bool isDeviceLost() => _isDeviceLost();
}

final class SharedBufferMemory extends _SharedBufferMemoryBase {
  SharedBufferMemory._(super.ptr) : super._();
  SharedBufferMemory._borrowed(super.ptr) : super._borrowed();

  set label(String value) => _setLabel(value);

  SharedBufferMemoryProperties get properties => _getProperties();
  Buffer createBuffer(BufferDescriptor? descriptor) => _createBuffer(descriptor);
  Status beginAccess(Buffer buffer, SharedBufferMemoryBeginAccessDescriptor descriptor) =>
      _beginAccess(buffer, descriptor);
  SharedBufferMemoryEndAccessState endAccess(Buffer buffer) => _endAccess(buffer);
  bool isDeviceLost() => _isDeviceLost();
}
