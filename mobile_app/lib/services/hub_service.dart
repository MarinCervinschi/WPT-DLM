import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/hub.dart';
import '../core/logger/app_logger.dart';

class HubService {
  final String baseUrl = "http://localhost:8000";

  // GET /hubs - Returns a list of hubs with optional filters
  Future<List<Hub>> getAllHubs({int skip = 0, int limit = 100, bool activeOnly = false}) async {
    final queryParams = {
      'skip': skip.toString(),
      'limit': limit.toString(),
      'active_only': activeOnly.toString(),
    };
    
    final uri = Uri.parse('$baseUrl/hubs').replace(queryParameters: queryParams);
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      logger.i('Hubs retrieved: ${response.body}');
      final Map<String, dynamic> data = json.decode(response.body);
      final List<dynamic> items = data['items'];
      return items.map((json) => Hub.fromJson(json)).toList();
    } else {
      logger.e('Error loading hubs: ${response.body}');
      throw Exception('Error loading hubs: ${response.body}');
    }
  }

  // GET /hubs/{hub_id} - Returns a single hub by ID
  Future<Hub> getHubById(String hubId) async {
    final response = await http.get(Uri.parse('$baseUrl/hubs/$hubId'));

    if (response.statusCode == 200) {
      logger.i('Hub data retrieved: ${response.body}');
      return Hub.fromJson(json.decode(response.body));
    } else if (response.statusCode == 404) {
      logger.w('Hub not found: $hubId');
      throw Exception('Hub not found');
    } else {
      logger.e('Error retrieving hub: ${response.body}');
      throw Exception('Error retrieving hub');
    }
  }
}