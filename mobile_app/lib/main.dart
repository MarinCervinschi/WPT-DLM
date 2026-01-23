import 'package:flutter/material.dart';
import 'package:mobile_app/screens/welcome_screen.dart';
import 'package:mobile_app/services/vehicle.dart';
import 'package:mobile_app/theme/theme.dart';
import 'package:mobile_app/widgets/main_wrapper.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<void> main() async {
  await dotenv.load(fileName: ".env");
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'WPT-DLM',
      theme: lightMode,
      home: const InitialScreen(),
    );
  }
}

class InitialScreen extends StatefulWidget {
  const InitialScreen({super.key});

  @override
  State<InitialScreen> createState() => _InitialScreenState();
}

class _InitialScreenState extends State<InitialScreen> {
  final _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _checkVehicleRegistration();
  }

  Future<void> _checkVehicleRegistration() async {
    try {
      String? savedId = await _apiService.getSavedVehicleId();
      if (!mounted) return;

      if (savedId != null) {
        // Veicolo già registrato, vai alla home
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const MainWrapper()),
        );
      } else {
        // Nessun veicolo registrato, vai alla welcome
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const WelcomeScreen()),
        );
      }
    } catch (e) {
      // In caso di errore, vai alla welcome
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const WelcomeScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}
