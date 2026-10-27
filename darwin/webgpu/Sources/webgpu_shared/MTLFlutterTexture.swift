import CoreVideo
import Foundation
import IOSurface
import Metal

#if canImport(FlutterMacOS)
  import FlutterMacOS
#else
  import Flutter
#endif

@_cdecl("MTLFlutterTexture_create")
func MTLFlutterTexture_create() -> UnsafeMutableRawPointer {
  let texture = MTLFlutterTexture()
  return UnsafeMutableRawPointer(Unmanaged.passRetained(texture).toOpaque())
}

@_cdecl("MTLFlutterTexture_destroy")
func MTLFlutterTexture_destroy(_ ptr: UnsafeMutableRawPointer) {
  let texture = Unmanaged<MTLFlutterTexture>.fromOpaque(ptr)
  texture.release()
}

@_cdecl("MTLFlutterTexture_acquire")
func MTLFlutterTexture_acquire(_ ptr: UnsafeMutableRawPointer, _ width: Int, _ height: Int) -> UnsafeMutableRawPointer? {
  let texture = Unmanaged<MTLFlutterTexture>.fromOpaque(ptr).takeUnretainedValue()
  return texture.acquire(width: width, height: height).map {
    Unmanaged.passUnretained($0).toOpaque()
  }
}

@_cdecl("MTLFlutterTexture_present")
func MTLFlutterTexture_present(_ ptr: UnsafeMutableRawPointer, _ event: MTLSharedEvent, _ value: UInt64) {
  let texture = Unmanaged<MTLFlutterTexture>.fromOpaque(ptr).takeUnretainedValue()
  texture.present(event: event, value: value)
}


@objc public final class MTLFlutterTexture: NSObject, FlutterTexture {
  private var pool: CVPixelBufferPool?
  private var poolSize = (0, 0)
  private var latest: CVPixelBuffer?
  private var acquired: CVPixelBuffer?
  private var pendingRender: (CVPixelBuffer, MTLSharedEvent, UInt64)?
  private let lock = NSLock()

  func createPool(width: Int, height: Int) -> CVPixelBufferPool? {
    let bufferAttributes: [String: Any] = [
      kCVPixelBufferWidthKey as String: width,
      kCVPixelBufferHeightKey as String: height,
      kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
      kCVPixelBufferMetalCompatibilityKey as String: true,
      kCVPixelBufferIOSurfacePropertiesKey as String: [:] as [String: Any],
    ]

    let poolAttributes: [String: Any] = [
      kCVPixelBufferPoolMinimumBufferCountKey as String: 3
    ]

    var pool: CVPixelBufferPool?
    CVPixelBufferPoolCreate(kCFAllocatorDefault, poolAttributes as CFDictionary, bufferAttributes as CFDictionary, &pool)
    return pool
  }

  func acquire(width: Int, height: Int) -> IOSurfaceRef? {
    if pool == nil || poolSize != (width, height) {
      pool = createPool(width: width, height: height)
      poolSize = (width, height)
    }

    guard let pool else { return nil }
  
    var buffer: CVPixelBuffer?
    let status = CVPixelBufferPoolCreatePixelBuffer(kCFAllocatorDefault, pool, &buffer)
    guard status == kCVReturnSuccess, let buffer else { return nil }
  
    acquired = buffer
    return CVPixelBufferGetIOSurface(buffer)?.takeUnretainedValue()
  }

  func present(event: MTLSharedEvent, value: UInt64) {
    guard let buffer = acquired else { return }
    acquired = nil
    lock.withLock {
      pendingRender = (buffer, event, value)
    }
  }

  public func copyPixelBuffer() -> Unmanaged<CVPixelBuffer>? {
    let value = lock.withLock { pendingRender }
    pendingRender = nil
  
    if let (buffer, event, eventValue) = value {
      if event.wait(untilSignaledValue: eventValue, timeoutMS: 8) {
        latest = buffer
      }
    }

    return latest.map { Unmanaged.passRetained($0) }
  }
}