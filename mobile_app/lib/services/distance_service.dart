import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/logger/app_logger.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class DistanceInfo {
  final double distanceMeters;
  final int durationSeconds;
  final String distanceText;
  final String durationText;

  DistanceInfo({
    required this.distanceMeters,
    required this.durationSeconds,
    required this.distanceText,
    required this.durationText,
  });

  double get distanceKm => distanceMeters / 1000;
  int get durationMinutes => (durationSeconds / 60).round();
}

class DistanceService {
  // Puoi ottenerla da: https://console.cloud.google.com/google/maps-apis/
  static final String _apiKey = dotenv.env['MAPS_API_KEY'] ?? '';
  
  static const String _baseUrl = 'https://maps.googleapis.com/maps/api/distancematrix/json';

  /// Calcola la distanza e il tempo di percorrenza tra due punti usando Google Distance Matrix API
  Future<DistanceInfo?> getDistance({
    required double originLat,
    required double originLng,
    required double destLat,
    required double destLng,
    String mode = 'driving', // driving, walking, bicycling, transit
  }) async {
    try {
      final uri = Uri.parse(_baseUrl).replace(queryParameters: {
        'origins': '$originLat,$originLng',
        'destinations': '$destLat,$destLng',
        'mode': mode,
        'key': _apiKey,
        'language': 'it',
      });

      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Check API response status
        if (data['status'] != 'OK') {
          logger.e('Google Distance Matrix API error: ${data['status']}');
          return null;
        }

        final rows = data['rows'] as List;
        if (rows.isEmpty) {
          logger.e('No routes found');
          return null;
        }

        final elements = rows[0]['elements'] as List;
        if (elements.isEmpty) {
          logger.e('No route elements found');
          return null;
        }

        final element = elements[0];
        if (element['status'] != 'OK') {
          logger.e('Route calculation failed: ${element['status']}');
          return null;
        }

        final distance = element['distance'];
        final duration = element['duration'];

        return DistanceInfo(
          distanceMeters: (distance['value'] as num).toDouble(),
          durationSeconds: duration['value'] as int,
          distanceText: distance['text'] as String,
          durationText: duration['text'] as String,
        );
      } else {
        logger.e('HTTP Error ${response.statusCode}: ${response.body}');
        return null;
      }
    } catch (e) {
      logger.e('Error calculating distance: $e');
      return null;
    }
  }

  /// Calcola la distanza e il tempo per più destinazioni
  Future<List<DistanceInfo?>> getDistances({
    required double originLat,
    required double originLng,
    required List<Map<String, double>> destinations,
    String mode = 'driving',
  }) async {
    try {
      final destString = destinations
          .map((d) => '${d['lat']},${d['lng']}')
          .join('|');

      final uri = Uri.parse(_baseUrl).replace(queryParameters: {
        'origins': '$originLat,$originLng',
        'destinations': destString,
        'mode': mode,
        'key': _apiKey,
        'language': 'it',
      });

      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        if (data['status'] != 'OK') {
          logger.e('Google Distance Matrix API error: ${data['status']}');
          return List.filled(destinations.length, null);
        }

        final rows = data['rows'] as List;
        if (rows.isEmpty) return List.filled(destinations.length, null);

        final elements = rows[0]['elements'] as List;
        
        return elements.map((element) {
          if (element['status'] != 'OK') return null;

          final distance = element['distance'];
          final duration = element['duration'];

          return DistanceInfo(
            distanceMeters: (distance['value'] as num).toDouble(),
            durationSeconds: duration['value'] as int,
            distanceText: distance['text'] as String,
            durationText: duration['text'] as String,
          );
        }).toList();
      } else {
        logger.e('HTTP Error ${response.statusCode}: ${response.body}');
        return List.filled(destinations.length, null);
      }
    } catch (e) {
      logger.e('Error calculating distances: $e');
      return List.filled(destinations.length, null);
    }
  }
}
