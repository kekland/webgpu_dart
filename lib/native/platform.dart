import 'dart:io';

import 'package:webgpu/shared/webgpu.g.dart' as webgpu;

import 'darwin/darwin.dart' as darwin;

void initializePlatform() {
  if (Platform.isMacOS || Platform.isIOS) {
    darwin.initializePlatform();
  } else {
    throw UnsupportedError('platform not supported');
  }
}

webgpu.DeviceDescriptor get platformDeviceDescriptor {
  if (Platform.isMacOS || Platform.isIOS) {
    return darwin.platformDeviceDescriptor;
  }

  throw UnsupportedError('platform not supported');
}
