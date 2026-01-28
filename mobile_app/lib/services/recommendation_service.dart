import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/recommendation.dart';
import '../core/logger/app_logger.dart';

class RecommendationService {
  final String baseUrl = "http://127.0.0.1:8000";

  /// POST /recommendations - Get a charging station recommendation
  /// 
  /// Parameters:
  /// - latitude: Vehicle's current latitude
  /// - longitude: Vehicle's current longitude  
  /// - batteryLevel: Current battery level (0-100)
  Future<Recommendation> getRecommendation({
    required double latitude,
    required double longitude,
    required int batteryLevel,
  }) async {
    final url = Uri.parse('$baseUrl/recommendations');
    
    final requestBody = {
      'latitude': latitude,
      'longitude': longitude,
      'battery_level': batteryLevel,
    };

    try {
      logger.i('Requesting recommendation: $requestBody');
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      );

      if (response.statusCode == 200) {
        logger.i('Recommendation received: ${response.body}');
        final data = jsonDecode(response.body);
        return Recommendation.fromJson(data);
      } else if (response.statusCode == 404) {
        logger.w('No available charging stations found');
        throw Exception('Nessuna stazione di ricarica disponibile trovata');
      } else {
        logger.e('Error getting recommendation: ${response.statusCode} - ${response.body}');
        throw Exception('Errore nel recupero della raccomandazione: ${response.body}');
      }
    } catch (e) {
      logger.e('Connection error: $e');
      if (e is Exception) {
        rethrow;
      }
      throw Exception('Impossibile connettersi al server: $e');
    }
  }
}
