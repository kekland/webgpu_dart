import 'package:webgpu/webgpu.dart' as webgpu;

import 'dawn.g.dart';
export 'dawn.g.dart';

import 'platform.dart';

// import 'dawn_bindings.g.dart' as bindings;

void initializeWebGpu() {
  initializePlatform();
}

Instance? _defaultInstance;
webgpu.Instance get platformDefaultInstance {
  _defaultInstance ??= .create();
  return _defaultInstance!;
}
