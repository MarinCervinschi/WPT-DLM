
class Hub {
  final String hubId;
  final double? lat;
  final double? lon;
  final double? alt;
  final double maxGridCapacityKw;
  final bool isActive;
  final DateTime? lastSeen;

  Hub({
    required this.hubId,
    this.lat,
    this.lon,
    this.alt,
    required this.maxGridCapacityKw,
    required this.isActive,
    this.lastSeen,
  });

  factory Hub.fromJson(Map<String, dynamic> json) {
    return Hub(
      hubId: json['hub_id'].toString(),
      lat: (json['lat'] as num?)?.toDouble(),
      lon: (json['lon'] as num?)?.toDouble(),
      alt: (json['alt'] as num?)?.toDouble(),
      maxGridCapacityKw: (json['max_grid_capacity_kw'] as num).toDouble(),
      isActive: json['is_active'] == true,
      lastSeen: json['last_seen'] != null 
          ? DateTime.parse(json['last_seen']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'hub_id': hubId,
    'lat': lat,
    'lon': lon,
    'alt': alt,
    'max_grid_capacity_kw': maxGridCapacityKw,
    'is_active': isActive,
    'last_seen': lastSeen?.toIso8601String(),
  };
}