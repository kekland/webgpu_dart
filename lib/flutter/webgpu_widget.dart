import 'package:flutter/material.dart';
import 'package:webgpu/flutter/renderable.dart';

import 'platform/darwin.dart' if (dart.library.js_interop) 'platform/web.dart';

class WebGpuWidget extends StatefulWidget {
  const new({super.key, this.renderable});

  final Renderable? renderable;

  @override
  // ignore: no_logic_in_create_state
  State<WebGpuWidget> createState() => createWebGpuWidgetState();
}

abstract class WebGpuWidgetState extends State<WebGpuWidget>;
