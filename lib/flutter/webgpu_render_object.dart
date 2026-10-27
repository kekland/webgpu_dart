import 'dart:math';

import 'package:flutter/rendering.dart';
import 'package:webgpu/webgpu.dart' as webgpu;

import 'renderable.dart';

abstract class WebGpuRenderObject extends RenderProxyBox {
  WebGpuRenderObject({
    this._renderable,
    this._devicePixelRatio = 1.0,
  }) {
    _renderable?.addListener(onRenderableUpdated);
  }

  Renderable? _renderable;
  Renderable? get renderable => _renderable;
  set renderable(Renderable? value) {
    if (_renderable == value) return;
    _renderable?.removeListener(onRenderableUpdated);
    _renderable = value;
    _renderable?.addListener(onRenderableUpdated);
    onRenderableUpdated();
  }

  webgpu.Device? _device;
  webgpu.Device? get device => _device;

  double _devicePixelRatio;
  double get devicePixelRatio => _devicePixelRatio;
  set devicePixelRatio(double value) {
    if (_devicePixelRatio == value) return;
    _devicePixelRatio = value;
    markNeedsSetup();
  }

  var _isSetupDirty = true;
  void markNeedsSetup() {
    _isSetupDirty = true;
    markNeedsPaint();
  }

  void onRenderableUpdated() {
    if (_device != _renderable?.device) {
      _device = _renderable?.device;
      markNeedsSetup();
    }

    markNeedsPaint();
  }

  Size? _lastSize;

  @override
  void performLayout() {
    super.performLayout();
    size = constraints.biggest;
    if (_lastSize != size) {
      _lastSize = size;
      markNeedsSetup();
    }
  }

  void performSetup();

  @override
  void paint(PaintingContext context, Offset offset) {
    if (_isSetupDirty) {
      performSetup();
      _isSetupDirty = false;
    }

    if (_device != null && _renderable != null) {
      final width = max(1, (size.width * _devicePixelRatio).toInt());
      final height = max(1, (size.height * _devicePixelRatio).toInt());
      performRender(_renderable!, width, height);
    }

    performPaint(context, offset);
    super.paint(context, offset);
  }

  void performRender(Renderable renderable, int width, int height);
  void performPaint(PaintingContext context, Offset offset) {}
}
