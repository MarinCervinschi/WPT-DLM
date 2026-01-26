class Recommendation {
  final String hubId;
  final String nodeId;
  final double hubLatitude;
  final double hubLongitude;
  final double distanceKm;
  final int estimatedWaitTimeMin;
  final double availablePowerKw;

  Recommendation({
    required this.hubId,
    required this.nodeId,
    required this.hubLatitude,
    required this.hubLongitude,
    required this.distanceKm,
    required this.estimatedWaitTimeMin,
    required this.availablePowerKw,
  });

  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      hubId: json['hub_id'],
      nodeId: json['node_id'],
      hubLatitude: json['hub_latitude'].toDouble(),
      hubLongitude: json['hub_longitude'].toDouble(),
      distanceKm: json['distance_km'].toDouble(),
      estimatedWaitTimeMin: json['estimated_wait_time_min'],
      availablePowerKw: json['available_power_kw'].toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'hub_id': hubId,
      'node_id': nodeId,
      'hub_latitude': hubLatitude,
      'hub_longitude': hubLongitude,
      'distance_km': distanceKm,
      'estimated_wait_time_min': estimatedWaitTimeMin,
      'available_power_kw': availablePowerKw,
    };
  }
}
