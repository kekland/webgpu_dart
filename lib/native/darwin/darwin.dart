import 'dart:ffi' as ffi;

import 'package:webgpu/webgpu.dart' as webgpu;
import 'package:webgpu/native.dart';

import 'darwin_bindings.g.dart' as bindings;

void initializePlatform() => bindings.darwin_ffi_init();

webgpu.DeviceDescriptor get platformDeviceDescriptor => .new(
  requiredFeatures: [.sharedTextureMemoryIOSurface, .sharedFenceMTLSharedEvent],
);

abstract class FlutterTexture<T extends ffi.NativeType> implements ffi.Finalizable {
  FlutterTexture._(this.__ptr) {
    if (__ptr.address != 0) {
      _finalizer.attach(this, __ptr.cast(), detach: this);
    }

    register();
  }

  ffi.Pointer<T> __ptr;
  ffi.Pointer<T> get _ptr {
    if (__ptr == ffi.nullptr) throw StateError('pointer is null');
    return __ptr;
  }

  int? _id;
  int? get id => _id;

  void register() {
    if (_id != null) throw StateError('texture is already registered');
    _id = FlutterTextureRegistry.instance.register(_ptr.cast());
  }

  void frameAvailable() {
    if (_id == null) throw StateError('texture is not registered');
    FlutterTextureRegistry.instance.frameAvailable(_id!);
  }

  void unregister() {
    if (_id == null) throw StateError('texture is not registered');
    FlutterTextureRegistry.instance.unregister(_id!);
    _id = null;
  }

  ffi.NativeFinalizer get _finalizer;

  void _dispose(void Function(ffi.Pointer<T>) deleter) {
    if (__ptr.address != 0) {
      if (_id != null) unregister();
      _finalizer.detach(this);
      deleter(__ptr);
      __ptr = ffi.nullptr;
    }
  }

  void dispose();
}

final class FlutterTextureRegistry {
  FlutterTextureRegistry(this._ptr);
  final bindings.flutter_texture_registry_t _ptr;

  static FlutterTextureRegistry? _instance;
  static FlutterTextureRegistry get instance {
    _instance ??= .new(bindings.flutter_texture_registry_get());
    return _instance!;
  }

  int register(bindings.flutter_texture_t texture) => bindings.flutter_texture_registry_register(_ptr, texture);
  void frameAvailable(int id) => bindings.flutter_texture_registry_texture_frame_available(_ptr, id);
  void unregister(int id) => bindings.flutter_texture_registry_unregister_texture(_ptr, id);
}

final class MetalFlutterTexture extends FlutterTexture<bindings.mtl_flutter_texture> {
  MetalFlutterTexture() : super._(bindings.mtl_flutter_texture_create());

  bindings.io_surface_ref_t? acquire({required int width, required int height}) {
    final result = bindings.mtl_flutter_texture_acquire(_ptr, width, height);
    if (result == ffi.nullptr) return null;
    return result;
  }

  void present(SharedTextureMemoryEndAccessState end) {
    final fence = end.fences.single;
    final value = end.signaledValues!.single;
    final fenceExport = fence.exportInfo(extensions: [.sharedFenceMTLSharedEventExportInfo]);
    final metalFenceExport = fenceExport.resolveNext<SharedFenceMTLSharedEventExportInfo>();
    bindings.mtl_flutter_texture_present(_ptr, metalFenceExport.sharedEvent.cast(), value);
    frameAvailable();
  }

  @override
  void dispose() => _dispose(bindings.mtl_flutter_texture_destroy);

  @override
  ffi.NativeFinalizer get _finalizer => __finalizer;
  static final __finalizer = ffi.NativeFinalizer(bindings.addresses.mtl_flutter_texture_destroy.cast());
}
