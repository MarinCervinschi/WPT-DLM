import 'package:flutter/material.dart';
import 'package:mobile_app/theme/theme.dart';

class SearchBarWidget extends StatelessWidget {
  final String hintText;
  final ValueChanged<String>? onChanged;
  final IconData icon;

  const SearchBarWidget({
    super.key,
    this.hintText = "Cerca posizione",
    this.onChanged,
    this.icon = Icons.search,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(30),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 10)
        ],
      ),
      child: TextField(
        decoration: InputDecoration(
          hintText: hintText,
          border: InputBorder.none,
          icon: Icon(icon, color: lightColorScheme.primary),
        ),
        onChanged: onChanged,
      ),
    );
  }
}
