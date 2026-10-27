part of 'types.dart';

abstract class ComputePassEncoder {
  set label(String value);

  void insertDebugMarker(String markerLabel);
  void pushDebugGroup(String groupLabel);
  void popDebugGroup();

  void setPipeline(covariant ComputePipeline pipeline);
  void setBindGroup(int index, covariant BindGroup? bindGroup, {Uint32List? dynamicOffsets});
  void setImmediates(int offset, TypedData data);
  void dispatchWorkgroups(int x, [int? y, int? z]);
  void dispatchWorkgroupsIndirect(covariant Buffer indirectBuffer, {int indirectOffset = 0});
  void end();

  void dispose();
}
