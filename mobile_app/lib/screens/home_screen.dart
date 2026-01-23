import 'package:flutter/material.dart';
import 'package:mobile_app/core/logger/app_logger.dart';
import 'package:mobile_app/theme/theme.dart';
import 'package:mobile_app/widgets/custom_scaffold.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:mobile_app/widgets/telemetry_card.dart';
import '../services/vehicle.dart';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _apiService = ApiService();
  WebSocketChannel? _channel;
  String? _vehicleId;
  Map<String, dynamic>? _vehicleData;
  Map<String, dynamic>? _lastTelemetryData;
  bool _isLoading = true;
  Stream<String>? _realTimeTelemetryStream;

  @override
  void initState() {
    super.initState();
    _loadCachedTelemetry();
    _initRealTime();
    _loadVehicleData();
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }

  Future<void> _loadCachedTelemetry() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cachedData = prefs.getString('last_telemetry_data');
      if (cachedData != null) {
        setState(() {
          _lastTelemetryData = jsonDecode(cachedData);
        });
        logger.i('Dati telemetria caricati dalla cache');
      }
    } catch (e) {
      logger.e('Errore caricamento telemetria dalla cache: $e');
    }
  }

  Future<void> _saveTelemetryToCache(Map<String, dynamic> data) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('last_telemetry_data', jsonEncode(data));
      logger.d('Dati telemetria salvati in cache');
    } catch (e) {
      logger.e('Errore salvataggio telemetria in cache: $e');
    }
  }

  void _initRealTime() async {
    if (_channel != null) {
      logger.i('Chiusura connessione WebSocket esistente...');
      _channel!.sink.close();
      _channel = null;
    }

    _vehicleId = await _apiService.getSavedVehicleId();
    logger.i('Vehicle ID trovato: $_vehicleId');
    if (_vehicleId != null) {
      _channel = WebSocketChannel.connect(
        Uri.parse('ws://localhost:8000/ws/telemetry/$_vehicleId'),
      );
      logger.i('Connesso a WebSocket per veicolo $_vehicleId');

      _realTimeTelemetryStream = _channel!.stream.map((data) => data.toString());
      setState(() {});
    }
  }

  void _loadVehicleData() async {
    try {
      String? savedId = await _apiService.getSavedVehicleId();
      if (savedId != null) {
        final data = await _apiService.getVehicleDetails(savedId);
        setState(() {
          _vehicleData = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      logger.e('Errore caricamento dati: $e');
      setState(() => _isLoading = false);

      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Errore caricamento dati: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return CustomScaffold(
      child: Column(
        children: [
          // --- SEZIONE SUPERIORE (Sullo sfondo trasparente) ---
          Padding(
            padding: const EdgeInsets.fromLTRB(25.0, 25.0, 25.0, 25.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Vehicle info (Manufacturer and Model)
                RichText(
                  textAlign: TextAlign.center,
                  text: TextSpan(
                    style: const TextStyle(
                      fontSize: 28.0,
                      fontWeight: FontWeight.w900,
                    ),
                    children: [
                      TextSpan(
                        text: '${_vehicleData?['manufacturer'] ?? 'N/A'} ',
                        style: const TextStyle(color: Colors.white),
                      ),
                      WidgetSpan(
                        alignment: PlaceholderAlignment.middle,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 1,
                          ),
                          decoration: BoxDecoration(
                            // Il tuo blu con opacità
                            color: const Color.fromARGB(
                              255,
                              160,
                              179,
                              233,
                            ).withValues(alpha: 0.3),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: const Color(
                                0xFF4463C3,
                              ).withValues(alpha: 0.5),
                              width: 1,
                            ),
                          ),
                          child: Text(
                            _vehicleData?['model'] ?? 'N/A',
                            style: const TextStyle(
                              fontSize: 28.0,
                              fontWeight: FontWeight.w900,
                              color: Color(0xFF4463C3), // Testo blu pieno
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // Icona/Immagine auto (senza contenitore bordato o con stile diverso)
                _buildVehicleImage(),

                Text(
                  'Targa: ${_vehicleData?['vehicle_id'] ?? 'N/A'}',
                  style: const TextStyle(
                    color: Colors.white70, // Bianco semitrasparente
                    fontSize: 14.0,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),

          // --- SEZIONE INFERIORE (Il contenitore bianco) ---
          Expanded(
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(25.0, 30.0, 25.0, 20.0),
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(40.0),
                  topRight: Radius.circular(40.0),
                ),
              ),
              child: _realTimeTelemetryStream == null
                  ? _buildTelemetryUI(_lastTelemetryData, isConnecting: true)
                  : StreamBuilder<String>(
                      stream: _realTimeTelemetryStream,
                      builder: (context, snapshot) {
                        // Se abbiamo dati in cache, mostrali mentre attendiamo nuovi dati
                        if (!snapshot.hasData && _lastTelemetryData != null) {
                          return _buildTelemetryUI(_lastTelemetryData, isWaiting: true);
                        }

                        if (_isLoading || !snapshot.hasData) {
                          return const Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                CircularProgressIndicator(),
                                SizedBox(height: 16),
                                Text('In attesa di telemetria...'),
                              ],
                            ),
                          );
                        }

                        if (snapshot.hasError) {
                          logger.e('Errore WebSocket: ${snapshot.error}');
                          // Se c'è un errore ma abbiamo dati in cache, mostrali
                          if (_lastTelemetryData != null) {
                            return _buildTelemetryUI(_lastTelemetryData, hasError: true);
                          }
                          return Center(
                            child: Text('Errore: ${snapshot.error}'),
                          );
                        }

                        Map<String, dynamic> telemetryData;
                        try {
                          telemetryData = jsonDecode(snapshot.data!);
                          logger.d('Dati telemetria ricevuti: $telemetryData');
                          
                          // Salva i nuovi dati in cache e aggiorna lo stato
                          _lastTelemetryData = telemetryData;
                          _saveTelemetryToCache(telemetryData);
                        } catch (e) {
                          logger.e('Errore parsing JSON: $e');
                          // Se c'è un errore di parsing ma abbiamo dati in cache, mostrali
                          if (_lastTelemetryData != null) {
                            return _buildTelemetryUI(_lastTelemetryData, hasError: true);
                          }
                          return Center(
                            child: Text('Errore parsing dati: $e'),
                          );
                        }

                        return _buildTelemetryUI(telemetryData);
                      },
                    ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTelemetryUI(Map<String, dynamic>? telemetryData, {
    bool isConnecting = false,
    bool isWaiting = false,
    bool hasError = false,
  }) {
    if (telemetryData == null) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('In attesa di telemetria...'),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Vehicle Status',
                style: TextStyle(
                  fontSize: 22.0,
                  fontWeight: FontWeight.bold,
                  color: lightColorScheme.primary,
                ),
              ),
              if (isConnecting || isWaiting || hasError)
                Row(
                  children: [
                    if (isConnecting || isWaiting)
                      const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    if (hasError)
                      const Icon(Icons.warning_amber, color: Colors.orange, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      isConnecting
                          ? 'Connessione...'
                          : isWaiting
                              ? 'Aggiornamento...'
                              : 'Dati non aggiornati',
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
            ],
          ),
          const SizedBox(height: 20.0),
          // Battery Energy Card
          TelemetryCard(
            title: 'Battery Energy',
            topRightIcon: Icons.bolt_rounded,
            accentColor: Colors.blueAccent,
            centerWidget: CircularPercentageWidget(
              percentage: (telemetryData['battery_level'] ?? 0).toDouble(),
              color: Colors.blueAccent,
              lowLevelColor: Colors.redAccent,
              lowLevelThreshold: 20,
            ),
            infoRows: [
              InfoRow(
                icon: (telemetryData['is_charging'] ?? false)
                    ? Icons.battery_charging_full
                    : Icons.battery_std,
                iconColor: (telemetryData['is_charging'] ?? false)
                    ? Colors.green
                    : Colors.orange,
                label: '',
                value: (telemetryData['is_charging'] ?? false)
                    ? 'Charging'
                    : 'Battery',
                valueColor: (telemetryData['is_charging'] ?? false)
                    ? Colors.green
                    : Colors.orange,
              ),
              InfoRow(
                label: 'State',
                value: (telemetryData['is_charging'] ?? false)
                    ? 'Connected'
                    : 'Battery',
              ),
              InfoRow(
                label: 'Autonomy',
                value: '${((telemetryData['battery_level'] ?? 0) * 4).toInt()} km',
              ),
            ],
          ),
          const SizedBox(height: 15.0),

          // Velocità
          TelemetryCard(
            title: 'Speed',
            topRightIcon: Icons.speed,
            accentColor: Colors.green,
            centerWidget: SimpleValueWidget(
              value: (telemetryData['speed_kmh'] ?? 0.0).toStringAsFixed(1),
              unit: 'km/h',
              color: Colors.green,
            ),
            infoRows: [
              InfoRow(
                label: 'Last Update',
                value: _formatTimestamp(telemetryData['timestamp'] ?? ''),
              ),
            ],
          ),

          const SizedBox(height: 15.0),

          TelemetryCard(
            title: 'Engine Temperature',
            topRightIcon: Icons.thermostat,
            accentColor: Colors.orange,
            centerWidget: SimpleValueWidget(
              value: (telemetryData['engine_temp_c'] ?? 0.0).toStringAsFixed(0),
              unit: '°C',
              color: ((telemetryData['engine_temp_c'] ?? 0.0) as num) > 90
                  ? Colors.red
                  : Colors.orange,
            ),
            infoRows: [
              InfoRow(
                label: 'Last Update',
                value: _formatTimestamp(telemetryData['timestamp'] ?? ''),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatTimestamp(String? timestamp) {
    if (timestamp == null || timestamp.isEmpty) {
      return 'N/A';
    }
    try {
      final dateTime = DateTime.parse(timestamp);
      return '${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      logger.e('Errore parsing timestamp: $e');
      return 'N/A';
    }
  }

  Widget _buildVehicleImage() {
    final manufacturer = _vehicleData?['manufacturer'] ?? '';
    final imagePath =
        'assets/images/manufacturers/${manufacturer.toLowerCase()}.png';

    return Image.asset(
      imagePath,
      height: 160,
      errorBuilder: (context, error, stackTrace) {
        // Se l'immagine non viene trovata, mostra l'icona
        return Icon(
          Icons.directions_car,
          size: 120,
          color: Colors.white.withValues(alpha: 0.9),
        );
      },
    );
  }
}
