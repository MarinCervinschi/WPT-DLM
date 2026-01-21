import 'package:flutter/material.dart';
import 'package:mobile_app/theme/theme.dart';
import 'package:mobile_app/widgets/custom_scaffold.dart';
import 'package:mobile_app/widgets/main_wrapper.dart';
import '../models/vehicle.dart';
import '../services/vehicle.dart';

class RegistrationScreen extends StatefulWidget {
  const RegistrationScreen({super.key});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _apiService = ApiService();

  // Controller per i campi di testo
  final _idController = TextEditingController();
  final _manufacturerController = TextEditingController();
  final _modelController = TextEditingController();
  final _driverNameController = TextEditingController();
  final _driverDocumentController = TextEditingController();

  bool _isLoading = false;

  void _submitData() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _isLoading = true);

      // Genera l'ID del driver combinando nome e numero documento
      final driverId = '${_driverNameController.text.replaceAll(' ', '_')}_${_driverDocumentController.text}';
      
      final newVehicle = Vehicle(
        id: _idController.text,
        manufacturer: _manufacturerController.text,
        model: _modelController.text,
        driverId: driverId,
      );

      try {
        await _apiService.registerVehicle(newVehicle);
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Veicolo registrato con successo!')),
        );
        // Navigate to MainWrapper
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const MainWrapper()),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      } finally {
        setState(() => _isLoading = false);
      }
    }
  }

   @override
  Widget build(BuildContext context) {
    return CustomScaffold(
      child: Column(
        children: [
          const Expanded(
            flex: 1,
            child: SizedBox(
              height: 10,
            ),
          ),
          Expanded(
            flex: 7,
            child: Container(
              padding: const EdgeInsets.fromLTRB(25.0, 50.0, 25.0, 20.0),
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(40.0),
                  topRight: Radius.circular(40.0),
                ),
              ),
              child: SingleChildScrollView(
                // vehicle registration form
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      // registration title
                      Text(
                        'Registra il tuo Veicolo',
                        style: TextStyle(
                          fontSize: 30.0,
                          fontWeight: FontWeight.w900,
                          color: lightColorScheme.primary,
                        ),
                      ),
                      const SizedBox(
                        height: 10.0,
                      ),
                      const Text(
                        'Inserisci i dati del veicolo e del conducente',
                        style: TextStyle(
                          color: Colors.black45,
                          fontSize: 14.0,
                        ),
                      ),
                      const SizedBox(
                        height: 40.0,
                      ),
                      // vehicle license plate
                      TextFormField(
                        controller: _idController,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Inserisci la targa del veicolo';
                          }
                          return null;
                        },
                        decoration: InputDecoration(
                          label: const Text('Targa Veicolo'),
                          hintText: 'es. AB123CD',
                          prefixIcon: const Icon(Icons.credit_card, color: Color(0xFF416FDF)),
                          hintStyle: const TextStyle(
                            color: Colors.black26,
                          ),
                          border: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                      const SizedBox(
                        height: 25.0,
                      ),
                      // manufacturer
                      TextFormField(
                        controller: _manufacturerController,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Inserisci la marca del veicolo';
                          }
                          return null;
                        },
                        decoration: InputDecoration(
                          label: const Text('Marca'),
                          hintText: 'es. Tesla, BMW, Audi',
                          prefixIcon: const Icon(Icons.business, color: Color(0xFF416FDF)),
                          hintStyle: const TextStyle(
                            color: Colors.black26,
                          ),
                          border: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                      const SizedBox(
                        height: 25.0,
                      ),
                      // model
                      TextFormField(
                        controller: _modelController,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Inserisci il modello del veicolo';
                          }
                          return null;
                        },
                        decoration: InputDecoration(
                          label: const Text('Modello'),
                          hintText: 'es. Model 3, i4, e-tron',
                          prefixIcon: const Icon(Icons.directions_car, color: Color(0xFF416FDF)),
                          hintStyle: const TextStyle(
                            color: Colors.black26,
                          ),
                          border: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                      const SizedBox(
                        height: 25.0,
                      ),
                      // driver name
                      TextFormField(
                        controller: _driverNameController,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Inserisci il nome del conducente';
                          }
                          return null;
                        },
                        decoration: InputDecoration(
                          label: const Text('Nome Conducente'),
                          hintText: 'Nome e Cognome',
                          prefixIcon: const Icon(Icons.person, color: Color(0xFF416FDF)),
                          hintStyle: const TextStyle(
                            color: Colors.black26,
                          ),
                          border: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                      const SizedBox(
                        height: 25.0,
                      ),
                      // driver document
                      TextFormField(
                        controller: _driverDocumentController,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Inserisci il numero documento';
                          }
                          return null;
                        },
                        decoration: InputDecoration(
                          label: const Text('Numero Documento'),
                          hintText: 'Numero carta d\'identità o patente',
                          prefixIcon: const Icon(Icons.badge, color: Color(0xFF416FDF)),
                          hintStyle: const TextStyle(
                            color: Colors.black26,
                          ),
                          border: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderSide: const BorderSide(
                              color: Colors.black12,
                            ),
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                      const SizedBox(
                        height: 40.0,
                      ),
                      // register button
                      _isLoading
                          ? const CircularProgressIndicator()
                          : SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: _submitData,
                                child: const Text('Registra Veicolo'),
                              ),
                            ),
                      const SizedBox(
                        height: 20.0,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}