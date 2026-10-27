# webgpu

WebGPU bindings for Dart and platform interop for Flutter (currently iOS, macOS, and web).

Uses Dawn with a codegen script for native platforms:
- `tool/build_dawn.py`: build script
- `tool/generate_bindings.py`: generates high-level Dart bindings

and partially hand-rolled JS bindings for web:
- `tool/generate_webgpu_bindings.dart`: generates `package:web`-compatible bindings for WebGPU using the IDL definitions

with a shared common interface under `lib/shared`.

Additional platform support can be added by creating the texture interop and render object implementations.