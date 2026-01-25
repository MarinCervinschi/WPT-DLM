import 'dart:async';

import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:visibility_detector/visibility_detector.dart';
import '../core/logger/app_logger.dart';
import '../services/vehicle.dart';
import '../widgets/main_wrapper.dart';
import '../widgets/qr/buttons/start_stop_button.dart';
import '../widgets/qr/buttons/switch_camera_button.dart';
import '../widgets/qr/buttons/toggle_flashlight_button.dart';
import '../widgets/qr/scanner_error_widget.dart';

/// QR Scanner for charging station association
class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({super.key});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> with WidgetsBindingObserver {
  MobileScannerController? controller;

  // Services
  final ApiService _vehicleService = ApiService();
  bool isProcessing = false;
  bool _isCameraActive = false;

  MobileScannerController initController() => MobileScannerController(
    autoStart: false,
    detectionSpeed: DetectionSpeed.noDuplicates,
    detectionTimeoutMs: 1000,
  );

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    controller = initController();
    // Non avviamo automaticamente, lo fa il VisibilityDetector
  }

  @override
  Future<void> dispose() async {
    WidgetsBinding.instance.removeObserver(this);
    await _stopCamera();
    await controller?.dispose();
    controller = null;
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.inactive || state == AppLifecycleState.paused) {
      _stopCamera();
    }
  }

  void _startCamera() {
    if (isProcessing || _isCameraActive || !mounted || controller == null) return;

    controller!.start().then((_) {
      if (mounted) {
        setState(() => _isCameraActive = true);
        logger.d('Camera avviata');
      }
    }).catchError((e) {
      logger.e('Errore avvio camera: $e');
    });
  }

  Future<void> _stopCamera() async {
    if (!_isCameraActive || controller == null) return;

    await controller!.stop();
    if (mounted) {
      setState(() => _isCameraActive = false);
      logger.d('Camera fermata');
    }
  }

  Future<void> _processChargingAuthorization(String qrCodeUrl) async {
    setState(() => isProcessing = true);
    await _stopCamera();

    try {
      final success = await _vehicleService.associateVehicleToStation(qrCodeUrl);

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Connessione riuscita!'),
            backgroundColor: Colors.green,
          ),
        );
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            Navigator.of(context).pushAndRemoveUntil(
              MaterialPageRoute(builder: (context) => const MainWrapper()),
              (route) => false,
            );
          }
        });
      } else {
        throw Exception('Errore durante l\'autorizzazione');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Errore: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
        _startCamera();
      }
    } finally {
      if (mounted) setState(() => isProcessing = false);
    }
  }

  void _handleBarcode(BarcodeCapture capture) {
    final String? code = capture.barcodes.firstOrNull?.rawValue;

    if (code != null && !isProcessing) {
      logger.i('QR Code rilevato: $code');
      _processChargingAuthorization(code);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scansiona QR Stazione'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      backgroundColor: Colors.black,
      body: controller == null
          ? const Center(child: CircularProgressIndicator())
          : Stack(
              children: [
                // Scanner camera
                VisibilityDetector(
                  key: const Key('qr-scanner-key'),
                  onVisibilityChanged: (visibilityInfo) {
                    final isVisible = visibilityInfo.visibleFraction > 0.1;
                    if (isVisible && !isProcessing && !_isCameraActive) {
                      _startCamera();
                    } else if (!isVisible && _isCameraActive) {
                      _stopCamera();
                    }
                  },
                  child: MobileScanner(
                    controller: controller,
                    onDetect: _handleBarcode,
                    errorBuilder: (context, error) {
                      return ScannerErrorWidget(error: error);
                    },
                    fit: BoxFit.cover,
                  ),
                ),

                // Cornice centrale
                if (!isProcessing)
                  Center(
                    child: Container(
                      width: 300,
                      height: 300,
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: Colors.white,
                          width: 3,
                        ),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Stack(
                        children: [
                          // Angoli verdi della cornice
                          Positioned(
                            top: 0,
                            left: 0,
                            child: Container(
                              width: 30,
                              height: 30,
                              decoration: const BoxDecoration(
                                border: Border(
                                  top: BorderSide(color: Colors.green, width: 5),
                                  left: BorderSide(color: Colors.green, width: 5),
                                ),
                              ),
                            ),
                          ),
                          Positioned(
                            top: 0,
                            right: 0,
                            child: Container(
                              width: 30,
                              height: 30,
                              decoration: const BoxDecoration(
                                border: Border(
                                  top: BorderSide(color: Colors.green, width: 5),
                                  right: BorderSide(color: Colors.green, width: 5),
                                ),
                              ),
                            ),
                          ),
                          Positioned(
                            bottom: 0,
                            left: 0,
                            child: Container(
                              width: 30,
                              height: 30,
                              decoration: const BoxDecoration(
                                border: Border(
                                  bottom: BorderSide(color: Colors.green, width: 5),
                                  left: BorderSide(color: Colors.green, width: 5),
                                ),
                              ),
                            ),
                          ),
                          Positioned(
                            bottom: 0,
                            right: 0,
                            child: Container(
                              width: 30,
                              height: 30,
                              decoration: const BoxDecoration(
                                border: Border(
                                  bottom: BorderSide(color: Colors.green, width: 5),
                                  right: BorderSide(color: Colors.green, width: 5),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                // Overlay per processing
                if (isProcessing)
                  Container(
                    color: Colors.black87,
                    child: const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                          SizedBox(height: 24),
                          Text(
                            'Invio dati veicolo alla stazione...',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                // Istruzioni in basso
                if (!isProcessing)
                  Positioned(
                    bottom: 0,
                    left: 0,
                    right: 0,
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Colors.transparent,
                            Colors.black.withValues(alpha: 0.8),
                          ],
                        ),
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(
                            Icons.qr_code_scanner_rounded,
                            color: Colors.white,
                            size: 48,
                          ),
                          const SizedBox(height: 12),
                          const Text(
                            'Inquadra il QR Code della stazione',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w500,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Posiziona il codice al centro della cornice',
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 14,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 24),
                          
                          // Controlli camera
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              ToggleFlashlightButton(controller: controller!),
                              StartStopButton(controller: controller!),
                              SwitchCameraButton(controller: controller!),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
    );
  }
}