import 'package:flutter/foundation.dart';
import 'package:webgpu/webgpu.dart' as webgpu;

mixin Renderable on ChangeNotifier {
  webgpu.Instance? get instance;
  webgpu.Device? get device;

  void render(webgpu.TextureView renderTextureView, webgpu.TextureFormat renderTextureFormat, int width, int height);
}
