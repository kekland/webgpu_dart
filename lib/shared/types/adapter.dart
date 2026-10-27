part of 'types.dart';

abstract class Adapter {
  Future<Device> requestDevice(DeviceDescriptor? descriptor);
  Future<Device> requestDefaultDevice([DeviceDescriptor? descriptor]);

  void dispose();
}
