import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import '../models/vehicle.dart';
import '../core/logger/app_logger.dart';

class ApiService {
  final String baseUrl = "http://localhost:8000";

  Future<void> saveVehicleId(String id) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('vehicle_id', id);
  }

  Future<String?> getSavedVehicleId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('vehicle_id');
  }

  //GET 
  Future<Map<String, dynamic>> getVehicleDetails(String vehicleId) async {
    final url = Uri.parse('$baseUrl/vehicles/$vehicleId');
    
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        logger.i('Vehicle data retrieved: ${response.body}');
        return jsonDecode(response.body);
      } else {
        logger.w('Failed to retrieve vehicle data: ${response.body}');
        throw Exception("Error retrieving vehicle data: ${response.body}");
      }
    } catch (e) {
      logger.e('Connection error: $e');
      throw Exception("Unable to connect to the server: $e");
    }
  }


  //POST
  Future<void> registerVehicle(Vehicle vehicle) async {
    final url = Uri.parse('$baseUrl/vehicles');

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(vehicle.toJson()),
      );

      if (response.statusCode != 200 && response.statusCode != 201) {
        throw Exception("Error during registration: ${response.body}");
      } else {
        await saveVehicleId(vehicle.id);
      }
    } catch (e) {
      throw Exception("Unable to connect to the server: $e");
    }
  }

  // POST - Associate vehicle to charging station
  Future<void> associateVehicleToStation(String vehicleId, String stationId) async {
    final url = Uri.parse('$baseUrl/sessions/start');

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'vehicle_id': vehicleId,
          'node_id': stationId,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        logger.i('Vehicle associated to station successfully: ${response.body}');
      } else {
        logger.w('Failed to associate vehicle: ${response.body}');
        throw Exception("Errore durante l'associazione: ${response.body}");
      }
    } catch (e) {
      logger.e('Connection error during association: $e');
      throw Exception("Impossibile connettersi al server: $e");
    }
  }
}
