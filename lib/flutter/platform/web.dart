import 'package:flutter/widgets.dart';
import 'package:web/web.dart' as web;
import 'package:webgpu/flutter/webgpu_widget.dart';
import 'package:webgpu/web/webgpu.g.dart' as web;
import 'package:webgpu/flutter/renderable.dart';
import 'package:webgpu/webgpu.dart' as webgpu;
import 'package:webgpu/web.dart' as webgpu_web;

import '../webgpu_render_object.dart';

WebGpuWidgetState createWebGpuWidgetState() => WebWebGpuWidgetState();

final class WebWebGpuWidgetState extends WebGpuWidgetState {
  web.HTMLCanvasElement? _canvas;

  @override
  void dispose() {
    _canvas = null;
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return _WebWebGpuRenderObjectWidget(
      renderable: widget.renderable,
      canvas: _canvas,
      child: HtmlElementView.fromTagName(
        tagName: 'canvas',
        onElementCreated: (element) {
          _canvas = element as web.HTMLCanvasElement;
          _canvas!.style.width = '100%';
          _canvas!.style.height = '100%';
          _canvas!.style.display = 'block';
          _canvas!.style.pointerEvents = 'none';

          setState(() {});
        },
      ),
    );
  }
}

final class const _WebWebGpuRenderObjectWidget({
  super.key,
  final Renderable? renderable,
  final web.HTMLCanvasElement? canvas,
  super.child,
}) extends SingleChildRenderObjectWidget {
  @override
  WebWebGpuRenderObject createRenderObject(BuildContext context) {
    return WebWebGpuRenderObject(
      renderable: renderable,
      canvas: canvas,
      devicePixelRatio: MediaQuery.devicePixelRatioOf(context),
    );
  }

  @override
  void updateRenderObject(BuildContext context, WebWebGpuRenderObject renderObject) {
    renderObject
      ..renderable = renderable
      ..canvas = canvas
      ..devicePixelRatio = MediaQuery.devicePixelRatioOf(context);
  }
}

final class WebWebGpuRenderObject extends WebGpuRenderObject {
  WebWebGpuRenderObject({
    this._canvas,
    super.renderable,
    super.devicePixelRatio,
  });

  web.HTMLCanvasElement? _canvas;
  web.HTMLCanvasElement? get canvas => _canvas;
  set canvas(web.HTMLCanvasElement? value) {
    if (_canvas == value) return;
    _canvas = value;
    markNeedsSetup();
  }

  @override
  void performSetup() {
    if (_canvas == null) return;
    if (device == null) return;

    final canvasContext = _canvas!.getContext('webgpu') as web.GPUCanvasContext?;
    if (canvasContext == null) {
      debugPrint('warning: Failed to get WebGPU context from canvas');
      return;
    }

    final preferredFormat = webgpu_web.Instance.instance.toJS.getPreferredCanvasFormat();

    canvasContext.configure(
      .new(
        device: device!.toJS,
        format: preferredFormat,
        usage: webgpu.TextureUsage.renderAttachment.value,
        alphaMode: 'premultiplied',
      ),
    );
  }

  @override
  void performRender(Renderable renderable, int width, int height) {
    final canvas = _canvas;
    if (canvas == null) return;

    canvas.width = width;
    canvas.height = height;

    final canvasContext = canvas.getContext('webgpu') as web.GPUCanvasContext?;
    if (canvasContext == null) {
      debugPrint('warning: Failed to get WebGPU context from canvas');
      return;
    }

    final texture = webgpu_web.Texture.from(canvasContext.getCurrentTexture());
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
  }

  @override
  void dispose() {
    _canvas = null;
    super.dispose();
  }
}
