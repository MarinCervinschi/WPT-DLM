import 'package:flutter/material.dart';
import 'package:mobile_app/screens/home_screen.dart';
import 'package:mobile_app/screens/qr_scanner.dart';
import 'package:mobile_app/screens/charging_page.dart';

class MainWrapper extends StatefulWidget {
  const MainWrapper({super.key});

  @override
  State<MainWrapper> createState() => _MainWrapperState();
}

class _MainWrapperState extends State<MainWrapper> {
  int _currentIndex = 0;

  // Lista delle pagine principali
  final List<Widget> _pages = [
    const HomeScreen(),     // La Home con i dati real-time
    const ChargingMapPage(), // Placeholder per Charger
    const QRScannerScreen(),      // QR Scanner
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack( 
        index: _currentIndex,
        children: _pages,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.blueAccent,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_rounded), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.ev_station_rounded), label: 'Charger'),
          BottomNavigationBarItem(icon: Icon(Icons.qr_code_scanner_rounded), label: 'QR'),
        ],
      ),
    );
  }
}