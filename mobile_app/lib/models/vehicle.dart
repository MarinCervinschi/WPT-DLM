
class Vehicle {
  final String id;
  final String manufacturer;
  final String model;
  final String driverId;
  final double? currentBatteryLevel;

  Vehicle({
    required this.id,
    required this.manufacturer,
    required this.model,
    required this.driverId,
    this.currentBatteryLevel,
  });

  Map<String, dynamic> toJson() => {
    'vehicle_id': id,
    'manufacturer': manufacturer,
    'model': model,
    'driver_id': driverId,
  };
}