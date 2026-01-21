import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../models/hub.dart';
import '../services/distance_service.dart';

class HubCard extends StatefulWidget {
  final Hub hub;
  final Position? currentPosition;
  final VoidCallback onClose;
  final VoidCallback? onNavigate;
  final VoidCallback? onFavorite;

  const HubCard({
    super.key,
    required this.hub,
    this.currentPosition,
    required this.onClose,
    this.onNavigate,
    this.onFavorite,
  });

  @override
  State<HubCard> createState() => _HubCardState();
}

class _HubCardState extends State<HubCard> {

  final DistanceService _distanceService = DistanceService();
  DistanceInfo? _distanceInfo;
  bool _isLoadingDistance = false;

  @override
  void initState() {
    super.initState();
    _loadDistanceInfo();
  }

  Future<void> _loadDistanceInfo() async {
    if (widget.currentPosition == null || widget.hub.lat == null || widget.hub.lon == null) {
      return;
    }

    setState(() {
      _isLoadingDistance = true;
    });

    final info = await _distanceService.getDistance(
      originLat: widget.currentPosition!.latitude,
      originLng: widget.currentPosition!.longitude,
      destLat: widget.hub.lat!,
      destLng: widget.hub.lon!,
    );

    if (mounted) {
      setState(() {
        _distanceInfo = info;
        _isLoadingDistance = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return _buildBasicView(context);
  }

  Widget _buildBasicView(BuildContext context) {
    return Positioned(
      bottom: 20,
      left: 16,
      right: 16,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: const [
            BoxShadow(color: Colors.black26, blurRadius: 15)
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    widget.hub.hubId,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                if (widget.onFavorite != null)
                  IconButton(
                    icon: Icon(Icons.favorite_border, color: Theme.of(context).colorScheme.primary),
                    onPressed: widget.onFavorite,
                  ),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.grey),
                  onPressed: widget.onClose,
                ),
              ],
            ),
            
            // Indirizzo
            Text(
              widget.hub.lat != null && widget.hub.lon != null
                  ? 'Lat: ${widget.hub.lat}, Lon: ${widget.hub.lon}'
                  : 'Posizione non disponibile',
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 16),
            
            // Status
            Row(
              children: [
                Icon(
                  widget.hub.isActive ? Icons.check_circle : Icons.cancel,
                  color: widget.hub.isActive ? Theme.of(context).colorScheme.primary : Colors.red,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  widget.hub.isActive ? 'Disponibile' : 'Non disponibile',
                  style: TextStyle(
                    color: widget.hub.isActive ? Theme.of(context).colorScheme.primary : Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            
            // Pulsanti azione
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _showHubDetailsBottomSheet(context),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Theme.of(context).colorScheme.primary,
                      side: BorderSide(color: Theme.of(context).colorScheme.primary),
                    ),
                    child: const Text("Dettagli"),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Theme.of(context).colorScheme.primary,
                      foregroundColor: Colors.white,
                    ),
                    onPressed: widget.hub.isActive && widget.onNavigate != null ? widget.onNavigate : null,
                    child: const Text("Naviga"),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showHubDetailsBottomSheet(BuildContext context) {
    final distanceText = _isLoadingDistance
        ? 'Caricamento...'
        : (_distanceInfo?.distanceText ?? 'N/A');
    final durationText = _isLoadingDistance
        ? 'Caricamento...'
        : (_distanceInfo?.durationText ?? 'N/A');
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.75,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
        ),
        child: Column(
          children: [
            // Handle bar
            Container(
              margin: const EdgeInsets.only(top: 12, bottom: 8),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            
            // Scrollable content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(
                            Icons.ev_station,
                            color: Theme.of(context).colorScheme.primary,
                            size: 32,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                widget.hub.hubId,
                                style: const TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  Icon(
                                    widget.hub.isActive ? Icons.check_circle : Icons.cancel,
                                    color: widget.hub.isActive 
                                        ? Theme.of(context).colorScheme.primary 
                                        : Colors.red,
                                    size: 16,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    widget.hub.isActive ? 'Disponibile' : 'Non disponibile',
                                    style: TextStyle(
                                      color: widget.hub.isActive 
                                          ? Theme.of(context).colorScheme.primary 
                                          : Colors.red,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        if (widget.onFavorite != null)
                          IconButton(
                            icon: const Icon(Icons.favorite_border),
                            color: Theme.of(context).colorScheme.primary,
                            onPressed: () {
                              Navigator.pop(context);
                              widget.onFavorite?.call();
                            },
                          ),
                      ],
                    ),
                    const SizedBox(height: 32),
                    
                    // Info Section
                    Text(
                      'Informazioni Stazione',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[800],
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    _buildDetailCard(
                      context,
                      icon: Icons.access_time,
                      title: 'Tempo di arrivo',
                      value: durationText,
                      iconColor: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 12),
                    
                    _buildDetailCard(
                      context,
                      icon: Icons.directions_car,
                      title: 'Distanza',
                      value: distanceText,
                      iconColor: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 12),
                    
                    _buildDetailCard(
                      context,
                      icon: Icons.bolt,
                      title: 'Capacità massima',
                      value: '${widget.hub.maxGridCapacityKw.toStringAsFixed(1)} kW',
                      iconColor: Colors.amber,
                    ),
                    const SizedBox(height: 12),
                    
                    _buildDetailCard(
                      context,
                      icon: Icons.location_on,
                      title: 'Coordinate',
                      value: widget.hub.lat != null && widget.hub.lon != null
                          ? '${widget.hub.lat!.toStringAsFixed(6)}, ${widget.hub.lon!.toStringAsFixed(6)}'
                          : 'N/A',
                      iconColor: Colors.red,
                    ),
                    
                    if (widget.hub.lastSeen != null) ...[
                      const SizedBox(height: 12),
                      _buildDetailCard(
                        context,
                        icon: Icons.update,
                        title: 'Ultimo aggiornamento',
                        value: _formatLastSeen(widget.hub.lastSeen!),
                        iconColor: Colors.green,
                      ),
                    ],
                    
                    const SizedBox(height: 32),
                    
                    // Action buttons
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: widget.hub.isActive && widget.onNavigate != null 
                            ? () {
                                Navigator.pop(context);
                                widget.onNavigate?.call();
                              }
                            : null,
                        icon: const Icon(Icons.navigation),
                        label: const Text('Avvia Navigazione'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Theme.of(context).colorScheme.primary,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          textStyle: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildDetailCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String value,
    required Color iconColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  String _formatLastSeen(DateTime lastSeen) {
    final now = DateTime.now();
    final difference = now.difference(lastSeen);
    
    if (difference.inMinutes < 1) {
      return 'Proprio ora';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} minuti fa';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} ore fa';
    } else {
      return '${difference.inDays} giorni fa';
    }
  }

}
