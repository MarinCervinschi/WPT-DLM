import 'package:flutter/material.dart';
import 'package:mobile_app/screens/registration_screen.dart';
import 'package:mobile_app/widgets/custom_scaffold.dart';
import 'package:mobile_app/widgets/welcome_button.dart';
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return CustomScaffold(
      child: Column(
        children: [
          Expanded( 
            flex: 10, 
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 40.0),
              child: Center( 
                child: RichText(
                  textAlign: TextAlign.center,
                  text: const TextSpan(
                    children: [
                      TextSpan(
                        text: 'Welcome!\n',
                        style: TextStyle(
                          fontSize: 40.0,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      TextSpan(
                        text: '\nEnter vehicle details to start using our app',
                        style: TextStyle(
                          fontSize: 20,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          
          // Parte inferiore: Bottone proporzionato
          Flexible(
            flex: 2, 
            child: Align(
              alignment: Alignment.bottomRight,
              child: Padding(
                padding: const EdgeInsets.all(0.0), 
                child: SizedBox(
                  width: 150, 
                  child: WelcomeButton(
                    buttonText: 'Register',
                    onTap: const RegistrationScreen(),
                    color: Colors.white,
                    textColor: const Color(0xFF416FDF),
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