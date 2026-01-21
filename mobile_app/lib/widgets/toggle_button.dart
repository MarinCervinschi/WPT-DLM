import 'package:flutter/material.dart';
import '../theme/theme.dart';

class ToggleButton extends StatelessWidget {
  final String text;
  final bool isActive;
  final VoidCallback onTap;

  const ToggleButton({
    super.key,
    required this.text,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(right: 8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isActive ? lightColorScheme.primary : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: lightColorScheme.primary),
        ),
        child: Text(
          text,
          style: TextStyle(
            color: isActive ? Colors.white : lightColorScheme.primary,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}
