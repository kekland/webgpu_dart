import 'package:flutter/rendering.dart';
import 'package:flutter/widgets.dart' hide Texture;
import 'package:webgpu/flutter/renderable.dart';
import 'package:webgpu/flutter/webgpu_widget.dart';
import 'package:webgpu/native.dart';
import 'package:webgpu/native/darwin/darwin.dart' as darwin;

import '../webgpu_render_object.dart';

WebGpuWidgetState createWebGpuWidgetState() => DarwinWebGpuWidgetState();

final class DarwinWebGpuWidgetState extends WebGpuWidgetState {
  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(child: _DarwinWebGpuRenderObjectWidget(renderable: widget.renderable));
  }
}

final class const _DarwinWebGpuRenderObjectWidget({
  super.key,
  final Renderable? renderable,
}) extends LeafRenderObjectWidget {
  @override
  DarwinWebGpuRenderObject createRenderObject(BuildContext context) {
    return DarwinWebGpuRenderObject(
      renderable: renderable,
      devicePixelRatio: MediaQuery.devicePixelRatioOf(context),
    );
  }

  @override
  void updateRenderObject(BuildContext context, DarwinWebGpuRenderObject renderObject) {
    renderObject
      ..renderable = renderable
      ..devicePixelRatio = MediaQuery.devicePixelRatioOf(context);
  }
}

final class DarwinWebGpuRenderObject extends WebGpuRenderObject {
  DarwinWebGpuRenderObject({
    super.renderable,
    super.devicePixelRatio,
  });

  darwin.MetalFlutterTexture? _texture;
  final _cachedMemory = <int, (SharedTextureMemory, Texture)>{};

  @override
  void performSetup() {
    _texture ??= .new();
    _cachedMemory.clear();
  }

  @override
  void performRender(Renderable renderable, int width, int height) {
    final surface = _texture!.acquire(width: width, height: height);
    if (surface == null) return;

    final (SharedTextureMemory, Texture) sharedMemoryValue;
    if (_cachedMemory.containsKey(surface.address)) {
      sharedMemoryValue = _cachedMemory[surface.address]!;
    } else {
      final textureMemory = device!.importSharedTextureMemory(
        .new(next: SharedTextureMemoryIOSurfaceDescriptor(ioSurface: surface.cast())),
      );

      final texture = textureMemory.createTexture(
        .new(
          size: .new(width: width, height: height),
          format: .bgra8unorm,
          usage: .renderAttachment,
        ),
      );

      sharedMemoryValue = (textureMemory, texture);
      _cachedMemory[surface.address] = sharedMemoryValue;
    }

    final (memory, texture) = sharedMemoryValue;

    final status = memory.beginAccess(
      texture,
      .new(
        initialized: false,
        concurrentRead: false,
      ),
    );
    if (status != .success) {
      debugPrint('warning: failed to begin access with status $status');
      return;
    }

    final view = texture.createView();

    final renderContext = RenderContext(
      textureView: view,
      textureFormat: texture.format,
      textureWidth: width,
      textureHeight: height,
      devicePixelRatio: devicePixelRatio,
      size: size,
    );

    renderable.performRender(renderContext);

    final endAccessState = memory.endAccess(texture);
    _texture!.present(endAccessState);
  }

  @override
  void performPaint(PaintingContext context, Offset offset) {
    context.addLayer(
      TextureLayer(
        rect: Rect.fromLTWH(offset.dx, offset.dy, size.width, size.height),
        textureId: _texture!.id!,
        filterQuality: .low,
      ),
    );
  }

  @override
  void dispose() {
    _texture?.dispose();
    _texture = null;
    _cachedMemory.clear();
    super.dispose();
  }
}
