// ignore_for_file: non_constant_identifier_names

part of 'dawn.g.dart';

extension _StringExt on String {
  bindings.WGPUStringView toStringView(ffi.Allocator allocator) {
    final ptr = allocator<bindings.WGPUStringView>();
    final data = toNativeUtf8(allocator: allocator);
    ptr.ref.data = data.cast();
    ptr.ref.length = length;
    return ptr.ref;
  }
}

extension _StringViewExt on bindings.WGPUStringView {
  String toDartString() {
    if (data == ffi.nullptr) return '';
    if (length == bindings.WGPU_STRLEN) return data.cast<Utf8>().toDartString();
    if (length == 0) return '';
    return data.cast<Utf8>().toDartString(length: length);
  }
}

abstract class _Opaque<T extends ffi.NativeType> implements ffi.Finalizable {
  _Opaque._(this.__ptr) : _borrowed = false {
    if (__ptr.address != 0) _finalizer.attach(this, __ptr.cast(), detach: this);
  }

  _Opaque._borrowed(this.__ptr) : _borrowed = true;

  ffi.Pointer<T> __ptr;
  final bool _borrowed;

  ffi.Pointer<T> get _ptr {
    if (__ptr.address == 0) throw StateError('pointer is null');
    _usingKeepScope?._refs.add(this);
    return __ptr;
  }

  ffi.NativeFinalizer get _finalizer;

  void _dispose(void Function(ffi.Pointer<T>) deleter) {
    if (_borrowed) throw StateError('cannot release a borrowed pointer');
    if (__ptr.address != 0) {
      _finalizer.detach(this);
      deleter(__ptr);
      __ptr = ffi.nullptr;
    }
  }

  void dispose();
}

final class _FinalizableKeepAlive implements ffi.Finalizable {
  final _refs = <Object>[];
}

_FinalizableKeepAlive? _usingKeepScope;
final _usingCallbackHandles = <_CallbackHandle>[];
var _usingDepth = 0;

R _using<R>(R Function(ffi.Allocator) fn) {
  if (_usingDepth == 0) _usingCallbackHandles.clear();
  _usingDepth++;

  final scope = _FinalizableKeepAlive();
  final prev = _usingKeepScope;
  _usingKeepScope = scope;
  try {
    return using(fn);
  } finally {
    _usingKeepScope = prev;
    _usingDepth--;
  }
}

final class _CallbackHandle<F extends Function>(final int id, final bool repeating, final F handler);

abstract class _CallbackRegistry<F extends Function, FN extends ffi.NativeFunction> {
  final _handles = <int, _CallbackHandle<F>>{};
  int _nextId = 1;

  CallbackMode get callbackMode => .waitAnyOnly;

  _CallbackHandle register(F handler, bool repeating) {
    final id = _nextId++;
    final handle = _CallbackHandle(id, repeating, handler);
    _handles[id] = handle;

    if (!repeating) {
      _EventLoop._pending++;
      _EventLoop._ensureTicking();
    }

    return handle;
  }

  F? take(ffi.Pointer<ffi.Void> userdata) {
    final id = userdata.address;
    final handle = _handles[id];
    if (handle == null) return null;
    if (!handle.repeating) {
      _EventLoop._pending--;
      _handles.remove(id);
    }

    return handle.handler;
  }

  ffi.Pointer<FN> get nativeFunction;
}

final class _SyncCompleter<T> {
  bool isCompleted = false;
  T? _value;
  Object? _error;
  StackTrace? _stackTrace;

  void complete(T v) {
    _value = v;
    isCompleted = true;
  }

  void completeError(Object e, [StackTrace? s]) {
    _error = e;
    _stackTrace = s;
    isCompleted = true;
  }

  T get value {
    if (_error != null) Error.throwWithStackTrace(_error!, _stackTrace ?? .current);
    return _value as T;
  }
}

final class _EventLoop {
  static final _instances = <Instance>{};
  static int _pending = 0;
  static Timer? _timer;

  static void _registerInstance(Instance instance) => _instances.add(instance);
  static void _removeInstance(Instance instance) => _instances.remove(instance);

  static void _ensureTicking() {
    _timer ??= .periodic(Duration.zero, (_) => processEvents());
  }

  static const _syncPollSleep = Duration(microseconds: 200);

  static void processEvents() {
    for (final i in _instances) i._processEvents();
    if (_pending == 0) {
      _timer?.cancel();
      _timer = null;
    }
  }

  static Future<T> waitForAsync<T>(Completer<T> c) {
    _ensureTicking();
    return c.future;
  }

  static T waitForSync<T>(_SyncCompleter<T> c) {
    while (!c.isCompleted) {
      processEvents();
      if (!c.isCompleted) sleep(_syncPollSleep);
    }
    return c.value;
  }
}
