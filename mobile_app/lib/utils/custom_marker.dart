import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class CustomMarker {
  /// Create a custom marker with a specific color
  static Future<BitmapDescriptor> createCustomMarker({
    required Color color,
    required IconData icon,
    double size = 50,
  }) async {
    final recorder = ui.PictureRecorder();
    final canvas = Canvas(recorder);
    final paint = Paint()..color = color;

    // Draw circle background
    canvas.drawCircle(
      Offset(size / 2, size / 2),
      size / 2,
      paint,
    );

    // Draw white inner circle
    final innerPaint = Paint()..color = Colors.white;
    canvas.drawCircle(
      Offset(size / 2, size / 2),
      size / 2.5,
      innerPaint,
    );

    // Draw icon
    final textPainter = TextPainter(textDirection: TextDirection.ltr);
    textPainter.text = TextSpan(
      text: String.fromCharCode(icon.codePoint),
      style: TextStyle(
        fontSize: size / 2.5,
        fontFamily: icon.fontFamily,
        color: color,
      ),
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        (size - textPainter.width) / 2,
        (size - textPainter.height) / 2,
      ),
    );

    final picture = recorder.endRecording();
    final img = await picture.toImage(size.toInt(), size.toInt());
    final bytes = await img.toByteData(format: ui.ImageByteFormat.png);

    return BitmapDescriptor.bytes(bytes!.buffer.asUint8List());
  }

  /// Create marker for available hub (green)
  static Future<BitmapDescriptor> availableMarker() async {
    return createCustomMarker(
      color: const Color(0xFF4CAF50), // Green
      icon: Icons.ev_station,
    );
  }

  /// Create marker for unavailable hub (red)
  static Future<BitmapDescriptor> unavailableMarker() async {
    return createCustomMarker(
      color: const Color(0xFFF44336), // Red
      icon: Icons.ev_station,
    );
  }

  /// Create marker for selected hub (orange)
  static Future<BitmapDescriptor> selectedMarker() async {
    return createCustomMarker(
      color: const Color(0xFFFF9800), // Orange
      icon: Icons.ev_station,
      size: 50, 
    );
  }

  /// Create marker for current location (blue)
  static Future<BitmapDescriptor> currentLocationMarker() async {
    return createCustomMarker(
      color: const Color(0xFF2196F3), // Blue
      icon: Icons.my_location,
    );
  }
}
