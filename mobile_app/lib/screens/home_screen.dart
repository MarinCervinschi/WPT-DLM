import 'package:flutter/material.dart';
import 'package:mobile_app/theme/theme.dart';
import 'package:mobile_app/widgets/custom_scaffold.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:mobile_app/widgets/telemetry_card.dart';
import '../services/vehicle.dart';
import 'dart:convert';
import 'dart:math';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _apiService = ApiService();
  late WebSocketChannel _channel;
  String? _vehicleId;
  Map<String, dynamic>? _vehicleData;
  bool _isLoading = true;
  late Stream<String> _mockTelemetryStream;
  final Random _random = Random();

  @override
  void initState() {
    super.initState();
    _initMockStream();
    _loadVehicleData();
  }

  @override
  void dispose() {
    _channel.sink.close();
    super.dispose();
  }

  void _initMockStream() {
    // Simuliamo l'invio di dati ogni 2 secondi
    _mockTelemetryStream = Stream.periodic(Duration(seconds: 2), (
      computationCount,
    ) {
      // Creiamo un oggetto che rispetti lo schema VehicleTelemetry del tuo brain_api
      final mockData = {
        "battery_level": (65 + _random.nextInt(5)).toDouble(), // Simula una ricarica lenta
        "speed": 10.0 + _random.nextDouble() * 2,
        "engine_temp": (80 + _random.nextInt(20)).toDouble(),
        "is_charging": true,
        "latitude": 44.6488,
        "longitude": 10.9200,
        "timestamp": DateTime.now().toIso8601String(),
      };

      return jsonEncode(mockData);
    });
  }

  void _initRealTime() async {
    _vehicleId = await _apiService.getSavedVehicleId();
    if (_vehicleId != null) {
      // Ci connettiamo all'endpoint WebSocket del tuo brain_api
      _channel = WebSocketChannel.connect(
        Uri.parse('ws://localhost:8000/vehicles/websockets/$_vehicleId'),
      );
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
              child: StreamBuilder(
                stream: _mockTelemetryStream,
                builder: (context, snapshot) {
                  if (_isLoading || !snapshot.hasData) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  final telemetryData = jsonDecode(snapshot.data as String);

                  return SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            'Vehicle Status',
                            style: TextStyle(
                              fontSize: 22.0,
                              fontWeight: FontWeight.bold,
                              color: lightColorScheme.primary,
                            ),
                          ),
                        ),
                        const SizedBox(height: 20.0),
                        // Battery Energy Card
                        TelemetryCard(
                          title: 'Battery Energy',
                          topRightIcon: Icons.bolt_rounded,
                          accentColor: Colors.blueAccent,
                          centerWidget: CircularPercentageWidget(
                            percentage: telemetryData['battery_level']
                                .toDouble(),
                            color: Colors.blueAccent,
                            lowLevelColor: Colors.redAccent,
                            lowLevelThreshold: 20,
                          ),
                          infoRows: [
                            InfoRow(
                              icon: telemetryData['is_charging']
                                  ? Icons.battery_charging_full
                                  : Icons.battery_std,
                              iconColor: telemetryData['is_charging']
                                  ? Colors.green
                                  : Colors.orange,
                              label: '',
                              value: telemetryData['is_charging']
                                  ? 'Charging'
                                  : 'Battery',
                              valueColor: telemetryData['is_charging']
                                  ? Colors.green
                                  : Colors.orange,
                            ),
                            InfoRow(
                              label: 'State',
                              value: telemetryData['is_charging']
                                  ? 'Connected'
                                  : 'Battery',
                            ),
                            InfoRow(
                              label: 'Autonomy',
                              value:
                                  '${(telemetryData['battery_level'] * 4).toInt()} km',
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
                            value: telemetryData['speed'].toStringAsFixed(1),
                            unit: 'km/h',
                            color: Colors.green,
                          ),
                          infoRows: [
                            InfoRow(
                              label: 'Last Update',
                              value: _formatTimestamp(
                                telemetryData['timestamp'],
                              ),
                            ),
                          ],
                        ),

                        const SizedBox(height: 15.0),

                        TelemetryCard(
                          title: 'Engine Temperature',
                          topRightIcon: Icons.thermostat,
                          accentColor: Colors.orange,
                          centerWidget: SimpleValueWidget(
                            value: telemetryData['engine_temp'].toStringAsFixed(0),
                            unit: '°C',
                            color: (telemetryData['engine_temp'] as num) > 90
                                ? Colors.red
                                : Colors.orange,
                          ),
                          infoRows: [
                            InfoRow(
                              label: 'Last Update',
                              value: _formatTimestamp(
                                telemetryData['timestamp'],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _formatTimestamp(String timestamp) {
    try {
      final dateTime = DateTime.parse(timestamp);
      return '${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
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
