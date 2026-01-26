import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:collection/collection.dart';
import 'package:visibility_detector/visibility_detector.dart';
import '../services/location_service.dart';
import '../services/hub_service.dart';
import '../services/recommendation_service.dart';
import '../services/telemetry_cache_service.dart';
import '../models/hub.dart';
import '../models/recommendation.dart';
import '../widgets/hub_card.dart';
import '../widgets/search_bar_widget.dart';
import '../widgets/toggle_button.dart';
import '../core/logger/app_logger.dart';
import '../utils/custom_marker.dart';

class ChargingMapPage extends StatefulWidget {
  const ChargingMapPage({super.key});

  @override
  State<ChargingMapPage> createState() => _ChargingMapPageState();
}

class _ChargingMapPageState extends State<ChargingMapPage> with WidgetsBindingObserver {
  // Controllers
  GoogleMapController? _mapController;

  // State variables
  Position? _currentPosition;
  bool _isMapActive = false;
  List<Hub>? _allHubs = []; // All hubs from API
  List<Hub>? _hubs = []; // Filtered hubs for display
  Hub? _selectedHub;
  bool _isLoading = true;
  bool _isMapView = true;
  String _searchQuery = '';
  Marker? _selectedHubMarker;
  
  // Cache per ottimizzazione performance
  Set<Marker>? _cachedMarkers;
  String? _lastMarkerState;

  // Custom marker icons
  BitmapDescriptor? _availableIcon;
  BitmapDescriptor? _unavailableIcon;
  BitmapDescriptor? _selectedIcon;
  BitmapDescriptor? _currentLocationIcon;

  // Services
  final LocationService _locationService = LocationService();
  final HubService _hubService = HubService();
  final RecommendationService _recommendationService = RecommendationService();
  final TelemetryCacheService _telemetryCacheService = TelemetryCacheService();

  //default position (Modena, Italy)
  static const LatLng _defaultPosition = LatLng(44.647128, 10.925226);

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _loadCustomMarkers();
    _initializeData();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _mapController?.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.inactive || state == AppLifecycleState.paused) {
      _pauseMap();
    }
  }

  void _activateMap() {
    if (_isMapActive || !mounted) return;
    setState(() => _isMapActive = true);
    logger.d('Mappa attivata');
  }

  void _pauseMap() {
    if (!_isMapActive || !mounted) return;
    setState(() => _isMapActive = false);
    logger.d('Mappa in pausa');
  }

  Future<void> _loadCustomMarkers() async {
    _availableIcon = await CustomMarker.availableMarker();
    _unavailableIcon = await CustomMarker.unavailableMarker();
    _selectedIcon = await CustomMarker.selectedMarker();
    _currentLocationIcon = await CustomMarker.currentLocationMarker();

    // Trigger rebuild to show markers once loaded
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _initializeData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final results = await Future.wait([
        _locationService.getCurrentLocation(),
        _hubService.getAllHubs(activeOnly: false),
      ]);

      if (!mounted) return;

      setState(() {
        _currentPosition = results[0] as Position;
        _allHubs = results[1] as List<Hub>;
        _hubs = _allHubs; // Initially show all hubs
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
            action: SnackBarAction(
              label: 'Riprova',
              textColor: Colors.white,
              onPressed: _initializeData,
            ),
          ),
        );
      }
    }
  }

  LatLng get _initialPosition {
    if (_currentPosition != null) {
      logger.i(
        'Initial position set to current location: ${_currentPosition!.latitude}, ${_currentPosition!.longitude}',
      );
      return LatLng(_currentPosition!.latitude, _currentPosition!.longitude);
    }
    return _defaultPosition;
  }

  void _moveCameraToCurrentPosition() {
    if (_mapController != null && _currentPosition != null) {
      _mapController!.animateCamera(
        CameraUpdate.newLatLng(
          LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
        ),
      );
    }
  }

  Set<Marker> _buildMarkers() {
    // Calcola un hash per determinare se i marker devono essere ricostruiti
    final currentState = '${_currentPosition?.latitude}_${_currentPosition?.longitude}_'
        '${_hubs?.length}_${_selectedHub?.hubId}';
    
    // Se lo stato non è cambiato, usa la cache
    if (_lastMarkerState == currentState && _cachedMarkers != null) {
      return _cachedMarkers!;
    }
    
    // Ricostruisci i marker solo se necessario
    final markers = <Marker>{
      // 1. La tua posizione (BLU con icona personalizzata)
      if (_currentPosition != null)
        Marker(
          markerId: const MarkerId('current_pos'),
          position: LatLng(
            _currentPosition!.latitude,
            _currentPosition!.longitude,
          ),
          icon: _currentLocationIcon ?? BitmapDescriptor.defaultMarker,
          infoWindow: const InfoWindow(title: 'La mia posizione'),
        ),

      // 2. Tutti gli hub con icone personalizzate
      ...(_hubs ?? [])
          .where((h) => h.lat != null && h.lon != null)
          .where((h) => h.hubId != _selectedHub?.hubId)
          .map(
            (hub) => Marker(
              markerId: MarkerId(hub.hubId),
              position: LatLng(hub.lat!, hub.lon!),
              icon: hub.isActive
                  ? (_availableIcon ?? BitmapDescriptor.defaultMarker)
                  : (_unavailableIcon ?? BitmapDescriptor.defaultMarker),
              onTap: () => _onHubTapped(hub),
              infoWindow: InfoWindow(
                title: hub.hubId,
                snippet: hub.isActive ? 'Disponibile' : 'Non disponibile',
              ),
            ),
          ),

      // 3. L'hub selezionato (ARANCIONE con icona personalizzata più grande)
      if (_selectedHubMarker != null) _selectedHubMarker!,
    };
    
    // Aggiorna cache
    _cachedMarkers = markers;
    _lastMarkerState = currentState;
    
    return markers;
  }

  void _onHubTapped(Hub hub) {
    setState(() {
      _selectedHub = hub;
      _cachedMarkers = null; // Invalida cache per ricostruire marker

      // Creiamo il marker per l'hub selezionato con icona personalizzata ARANCIONE
      if (hub.lat != null && hub.lon != null) {
        _selectedHubMarker = Marker(
          markerId: const MarkerId('selected_hub'),
          infoWindow: InfoWindow(title: 'Stazione: ${hub.hubId}'),
          icon: _selectedIcon ?? BitmapDescriptor.defaultMarker,
          position: LatLng(hub.lat!, hub.lon!),
        );
      }
    });

    // Centra la mappa sull'hub selezionato
    if (hub.lat != null && hub.lon != null) {
      _mapController?.animateCamera(
        CameraUpdate.newLatLng(LatLng(hub.lat!, hub.lon!)),
      );
    }
  }

  void _filterHubs(String query) {
    setState(() {
      _searchQuery = query.toLowerCase().trim();
      _cachedMarkers = null; // Invalida cache quando cambiano i filtri

      if (_searchQuery.isEmpty) {
        // If search is empty, show all hubs
        _hubs = _allHubs;
        _selectedHub = null;
        _selectedHubMarker = null;
      } else {
        // Filter hubs by hubId or availability status
        _hubs = _allHubs?.where((hub) {
          final hubId = hub.hubId.toLowerCase();
          final status = hub.isActive ? 'disponibile' : 'non disponibile';

          return hubId.contains(_searchQuery) || status.contains(_searchQuery);
        }).toList();

        // If we found hubs, zoom on the first one and select it
        if (_hubs != null && _hubs!.isNotEmpty) {
          final firstHub = _hubs!.first;
          _selectedHub = firstHub;

          // Create the custom marker for the selected hub
          if (firstHub.lat != null && firstHub.lon != null) {
            _selectedHubMarker = Marker(
              markerId: const MarkerId('selected_hub'),
              infoWindow: InfoWindow(title: 'Stazione: ${firstHub.hubId}'),
              icon: _selectedIcon ?? BitmapDescriptor.defaultMarker,
              position: LatLng(firstHub.lat!, firstHub.lon!),
            );
          }

          // Zoom and center on the found hub
          if (firstHub.lat != null &&
              firstHub.lon != null &&
              _mapController != null) {
            _mapController!.animateCamera(
              CameraUpdate.newLatLngZoom(
                LatLng(firstHub.lat!, firstHub.lon!),
                15.0, // Closer zoom level
              ),
            );
          }

          // Switch to map view if in list view
          if (!_isMapView) {
            _isMapView = true;
          }
        } else {
          _selectedHub = null;
          _selectedHubMarker = null;
        }
      }
    });
  }

  // ============================================================================
  // UI BUILDERS
  // ============================================================================

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return _buildLoadingScreen();
    }

    if (_hubs == null || _hubs!.isEmpty) {
      return _buildErrorScreen();
    }

    return Scaffold(
      body: Stack(
        children: [
          // Mappa o Lista
          _isMapView ? _buildMapView() : _buildListView(),

          // Overlay superiore (ricerca e toggle)
          _buildTopOverlay(),

          // Pulsante ML Prediction
          _buildMLButton(),

          // Scheda hub selezionato
          if (_selectedHub != null)
            HubCard(
              hub: _selectedHub!,
              currentPosition: _currentPosition,
              onClose: () => setState(() {
                _selectedHub = null;
                _selectedHubMarker = null;
              }),
              onNavigate: () => _startNavigation(_selectedHub!),
              onFavorite: () {
                // TODO: Aggiungi ai preferiti
              },
            ),
        ],
      ),
    );
  }

  Widget _buildLoadingScreen() {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Colors.blueAccent),
            SizedBox(height: 16),
            Text('Caricamento stazioni di ricarica...'),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorScreen() {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              const Text(
                'Nessuna stazione disponibile',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _initializeData,
                icon: const Icon(Icons.refresh),
                label: const Text('Riprova'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMapView() {
    return VisibilityDetector(
      key: const Key('charging-map-key'),
      onVisibilityChanged: (visibilityInfo) {
        final isVisible = visibilityInfo.visibleFraction > 0.1;
        if (isVisible && !_isMapActive) {
          _activateMap();
        } else if (!isVisible && _isMapActive) {
          _pauseMap();
        }
      },
      child: GoogleMap(
        initialCameraPosition: CameraPosition(target: _initialPosition, zoom: 15),
        onMapCreated: (controller) {
          _mapController = controller;
          if (_currentPosition != null) {
            _moveCameraToCurrentPosition();
          }
        },
        markers: _buildMarkers(),
        myLocationEnabled: false,
        myLocationButtonEnabled: false,
        zoomControlsEnabled: false,
        mapToolbarEnabled: false,
        compassEnabled: false,
        rotateGesturesEnabled: false,
        tiltGesturesEnabled: false,
        buildingsEnabled: false,
        trafficEnabled: false,
        onTap: (_) {
          // Deseleziona l'hub quando si clicca sulla mappa
          if (_selectedHub != null) {
            setState(() {
              _selectedHub = null;
              _selectedHubMarker = null;
              _cachedMarkers = null; // Invalida cache
            });
          }
        },
      ),
    );
  }

  Widget _buildListView() {
    if (_hubs == null || _hubs!.isEmpty) {
      return _buildEmptyState(); // È meglio separare lo stato vuoto
    }

    return ListView.builder(
      padding: const EdgeInsets.only(top: 160, bottom: 24, left: 12, right: 12),
      itemCount: _hubs!.length,
      itemBuilder: (context, index) {
        final hub = _hubs![index];
        final bool isSelected = _selectedHub?.hubId == hub.hubId;

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: Material(
              color: isSelected ? Colors.blue.shade50 : Colors.white,
              child: InkWell(
                onTap: () {
                  setState(() {
                    _selectedHub = hub;
                    _isMapView = true;
                  });
                },
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      // Icona con sfondo circolare
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: hub.isActive
                              ? Colors.blueAccent.withValues(alpha: 0.1)
                              : Colors.grey.withValues(alpha: 0.1),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          Icons.ev_station_rounded,
                          color: hub.isActive ? Colors.blueAccent : Colors.grey,
                          size: 28,
                        ),
                      ),
                      const SizedBox(width: 16),

                      // Informazioni Hub
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "Stazione ${hub.hubId}",
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                                color: Colors.blueGrey.shade900,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                Icon(
                                  Icons.location_on,
                                  size: 14,
                                  color: Colors.grey.shade600,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  hub.lat != null
                                      ? "${hub.lat!.toStringAsFixed(4)}, ${hub.lon!.toStringAsFixed(4)}"
                                      : "Posizione ignota",
                                  style: TextStyle(
                                    color: Colors.grey.shade600,
                                    fontSize: 13,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),

                      // Badge di Stato
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: hub.isActive
                                  ? Colors.green.shade100
                                  : Colors.red.shade100,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              hub.isActive ? "DISPONIBILE" : "OCCUPATA",
                              style: TextStyle(
                                color: hub.isActive
                                    ? Colors.green.shade700
                                    : Colors.red.shade700,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Icon(
                            Icons.arrow_forward_ios_rounded,
                            size: 16,
                            color: Colors.grey.shade400,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  // Widget opzionale per quando la lista è vuota
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.search_off_rounded, size: 80, color: Colors.grey.shade300),
          const SizedBox(height: 16),
          Text(
            'Nessuna stazione trovata',
            style: TextStyle(color: Colors.grey.shade600, fontSize: 18),
          ),
        ],
      ),
    );
  }

  Widget _buildTopOverlay() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            SearchBarWidget(hintText: "Cerca stazione", onChanged: _filterHubs),
            const SizedBox(height: 12),

            // Toggle Map/List view
            Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                ToggleButton(
                  text: "Mappa",
                  isActive: _isMapView,
                  onTap: () => setState(() => _isMapView = true),
                ),
                ToggleButton(
                  text: "Lista",
                  isActive: !_isMapView,
                  onTap: () => setState(() => _isMapView = false),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMLButton() {
    return Positioned(
      right: 16,
      bottom: _selectedHub == null ? 10 : 240,
      child: FloatingActionButton(
        backgroundColor: Theme.of(context).colorScheme.primary,
        onPressed: _handleMLPrediction,
        heroTag: 'mlButton', // Evita conflitti se ci sono altri FAB
        child: const Icon(Icons.bolt, color: Colors.white),
      ),
    );
  }

  // ============================================================================
  // ACTIONS
  // ============================================================================

  void _handleMLPrediction() async {
    if (_currentPosition == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Posizione non disponibile'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    int? batteryLevel = await _telemetryCacheService.getCachedBatteryLevel();

    if (batteryLevel == null) {
      batteryLevel = await _showBatteryLevelDialog();
      if (batteryLevel == null) return;
    }

    if (!mounted) return;
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) =>
          const Center(child: CircularProgressIndicator(color: Colors.white)),
    );

    try {
      final recommendation = await _recommendationService.getRecommendation(
        latitude: _currentPosition!.latitude,
        longitude: _currentPosition!.longitude,
        batteryLevel: batteryLevel,
      );

      // Chiudi loading
      if (!mounted) return;
      Navigator.of(context).pop();

      final recommendedHub = _allHubs?.firstWhereOrNull(
        (hub) => hub.hubId == recommendation.hubId,
      );

      if (recommendedHub == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Hub did not found in the list'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      } 

      _onHubTapped(recommendedHub);
      // Mostra i dettagli della raccomandazione
      if (mounted) {
        _showRecommendationDialog(recommendation);
      }      

    } catch (e) {
      // Chiudi loading
      if (!mounted) return;
      Navigator.of(context).pop();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Errore: ${e.toString().replaceAll("Exception: ", "")}',
          ),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 4),
        ),
      );
    }
  }

  Future<int?> _showBatteryLevelDialog() async {
    final controller = TextEditingController(text: '50');

    return showDialog<int>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Livello Batteria'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Inserisci il livello attuale della batteria:'),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                suffixText: '%',
                border: OutlineInputBorder(),
                hintText: '0-100',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Annulla'),
          ),
          ElevatedButton(
            onPressed: () {
              final value = int.tryParse(controller.text);
              if (value != null && value >= 0 && value <= 100) {
                Navigator.of(context).pop(value);
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Inserisci un valore tra 0 e 100'),
                    backgroundColor: Colors.orange,
                  ),
                );
              }
            },
            child: const Text('Conferma'),
          ),
        ],
      ),
    );
  }

  void _showRecommendationDialog(Recommendation recommendation) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.bolt, color: Theme.of(context).colorScheme.primary),
            const SizedBox(width: 8),
            const Text('Raccommendation'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildRecommendationRow(
              Icons.ev_station,
              'Stazione',
              recommendation.hubId,
            ),
            const SizedBox(height: 8),
            _buildRecommendationRow(Icons.power, 'Nodo', recommendation.nodeId),
            const SizedBox(height: 8),
            _buildRecommendationRow(
              Icons.route,
              'Distanza',
              '${recommendation.distanceKm.toStringAsFixed(2)} km',
            ),
            const SizedBox(height: 8),
            _buildRecommendationRow(
              Icons.schedule,
              'Tempo attesa',
              '~${recommendation.estimatedWaitTimeMin} min',
            ),
            const SizedBox(height: 8),
            _buildRecommendationRow(
              Icons.flash_on,
              'Potenza',
              '${recommendation.availablePowerKw.toStringAsFixed(1)} kW',
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Chiudi'),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 20, color: Colors.blueGrey),
        const SizedBox(width: 8),
        Text('$label: ', style: const TextStyle(fontWeight: FontWeight.bold)),
        Expanded(
          child: Text(value, style: const TextStyle(color: Colors.black87)),
        ),
      ],
    );
  }

  Future<void> _startNavigation(Hub hub) async {
    if (hub.lat == null || hub.lon == null) return;

    // Usa lo schema 'google.navigation' per Android o 'maps.apple.com' per iOS
    // Oppure un link universale standard:
    final Uri googleMapsUrl = Uri.parse(
      "google.navigation:q=${hub.lat},${hub.lon}",
    );
    final Uri appleMapsUrl = Uri.parse(
      "http://maps.apple.com/?daddr=${hub.lat},${hub.lon}",
    );

    try {
      if (await canLaunchUrl(googleMapsUrl)) {
        await launchUrl(googleMapsUrl);
      } else if (await canLaunchUrl(appleMapsUrl)) {
        await launchUrl(appleMapsUrl);
      } else {
        // Se non ci sono app mappe, apri nel browser
        final Uri webUrl = Uri.parse(
          "https://www.google.com/maps/dir/?api=1&destination=${hub.lat},${hub.lon}",
        );
        await launchUrl(webUrl, mode: LaunchMode.externalApplication);
      }
    } catch (e) {
      logger.e('Errore: $e');
    }
  }
}
