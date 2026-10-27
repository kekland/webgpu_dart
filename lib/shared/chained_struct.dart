import 'webgpu.g.dart';

abstract class ExtensibleStruct {
  const ExtensibleStruct({this.next});
  final ChainedStruct? next;

  T resolveNext<T extends ChainedStruct>() => next as T;
}

abstract class ChainedStruct {
  const ChainedStruct({this.next});
  final ChainedStruct? next;

  SType get sType;

  T resolveNext<T extends ChainedStruct>() => next as T;
}
