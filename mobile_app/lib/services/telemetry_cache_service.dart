import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/logger/app_logger.dart';

class TelemetryCacheService {
  static const String _cacheKey = 'last_telemetry_data';

  /// Recupera i dati dell'ultima telemetria salvati in cache
  Future<Map<String, dynamic>?> getLastTelemetryData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cachedData = prefs.getString(_cacheKey);
      
      if (cachedData != null) {
        final data = jsonDecode(cachedData);
        logger.i('Dati telemetria recuperati dalla cache: $data');
        return data;
      }
      
      logger.w('Nessun dato telemetria trovato in cache');
      return null;
    } catch (e) {
      logger.e('Errore recupero telemetria dalla cache: $e');
      return null;
    }
  }

  /// Estrae il livello di batteria dai dati di telemetria
  /// Ritorna null se il dato non è disponibile o non è valido
  int? getBatteryLevel(Map<String, dynamic>? telemetryData) {
    if (telemetryData == null) return null;
    
    try {
      // Il campo potrebbe essere 'battery_level', 'batteryLevel', o simili
      // Proviamo diverse varianti
      final batteryLevel = telemetryData['battery_level'] ?? 
                          telemetryData['batteryLevel'] ??
                          telemetryData['battery'] ??
                          telemetryData['soc'];
      
      if (batteryLevel == null) {
        logger.w('Campo battery_level non trovato nei dati telemetria');
        return null;
      }
      
      // Converti in int se è un double
      if (batteryLevel is num) {
        final level = batteryLevel.round();
        if (level >= 0 && level <= 100) {
          return level;
        }
      }
      
      logger.w('Valore battery_level non valido: $batteryLevel');
      return null;
    } catch (e) {
      logger.e('Errore estrazione battery_level: $e');
      return null;
    }
  }

  /// Recupera direttamente il livello di batteria dalla cache
  Future<int?> getCachedBatteryLevel() async {
    final telemetryData = await getLastTelemetryData();
    return getBatteryLevel(telemetryData);
  }
}
