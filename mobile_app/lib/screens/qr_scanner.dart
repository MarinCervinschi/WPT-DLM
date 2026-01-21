import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/logger/app_logger.dart';
import '../services/vehicle.dart';

class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({super.key});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  final MobileScannerController controller = MobileScannerController();
  final ApiService apiService = ApiService();
  bool isProcessing = false;

  @override
  void initState() {
    super.initState();
    controller.start();
  }

  @override
  void dispose() {
    controller.stop();
    controller.dispose();
    super.dispose();
  }

  Future<void> sendVehicleData(String qrCodeUrl) async {
    if (isProcessing) return;

    setState(() {
      isProcessing = true;
    });

    try {
      // Recupera l'ID del veicolo salvato
      final vehicleId = await apiService.getSavedVehicleId();
      
      if (vehicleId == null) {
        throw Exception('Nessun veicolo registrato. Registra prima il tuo veicolo.');
      }

      // Recupera i dati completi del veicolo
      logger.i('Recupero dati del veicolo: $vehicleId');
      final vehicleData = await apiService.getVehicleDetails(vehicleId);

      // Invia i dati del veicolo all'URL del QR code
      logger.i('Invio dati veicolo a: $qrCodeUrl');
      
      final response = await http.post(
        Uri.parse(qrCodeUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(vehicleData),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        logger.i('Connessione alla stazione riuscita: ${response.body}');
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Connessione alla stazione riuscita!'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 2),
            ),
          );

          // Torna indietro dopo il successo
          Future.delayed(const Duration(seconds: 2), () {
            if (mounted) Navigator.pop(context, true);
          });
        }
      } else {
        logger.w('Errore nella connessione: ${response.body}');
        throw Exception('Errore nella connessione: ${response.body}');
      }
    } catch (e) {
      logger.e('Errore: $e');
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Errore: ${e.toString()}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } finally {
      setState(() {
        isProcessing = false;
      });
    }
  }

  void _handleBarcode(BarcodeCapture capture) {
    final List<Barcode> barcodes = capture.barcodes;
    
    for (final barcode in barcodes) {
      final String? code = barcode.rawValue;
      
      if (code != null && !isProcessing) {
        logger.i('QR Code rilevato: $code');
        sendVehicleData(code);
        break;
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scansiona QR Stazione'),
        actions: [
          IconButton(
            icon: const Icon(Icons.flash_on),
            onPressed: () => controller.toggleTorch(),
          ),
          IconButton(
            icon: const Icon(Icons.cameraswitch),
            onPressed: () => controller.switchCamera(),
          ),
        ],
      ),
      body: Stack(
        children: [
          MobileScanner(
            controller: controller,
            onDetect: _handleBarcode,
          ),
          if (isProcessing)
            Container(
              color: Colors.black54,
              child: const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(color: Colors.white),
                    SizedBox(height: 16),
                    Text(
                      'Invio dati veicolo alla stazione...',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.all(16),
              color: Colors.black87,
              child: const Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.qr_code_scanner,
                    color: Colors.white,
                    size: 48,
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Posiziona il codice QR entro la cornice',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                    textAlign: TextAlign.center,
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
