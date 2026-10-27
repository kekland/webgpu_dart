import 'dart:ui';

import 'package:flutter/foundation.dart';
import 'package:webgpu/webgpu.dart' as webgpu;

mixin Renderable on ChangeNotifier {
  webgpu.Device? get device;
  void performRender(RenderContext context);
}

final class RenderContext({
  required final webgpu.TextureView textureView,
  required final webgpu.TextureFormat textureFormat,
  required final int textureWidth,
  required final int textureHeight,
  required final double devicePixelRatio,
  required final Size size,
});
