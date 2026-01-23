import 'package:flutter/material.dart';

class TelemetryCard extends StatelessWidget {
  final String title;
  final IconData topRightIcon;
  final Color accentColor;
  final Widget centerWidget;
  final List<InfoRow> infoRows;

  const TelemetryCard({
    super.key, // Simplified super parameter
    required this.title,
    required this.topRightIcon,
    required this.accentColor,
    required this.centerWidget,
    required this.infoRows,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: Stack(
        clipBehavior: Clip.hardEdge,
        children: [
          // Card Principale
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: accentColor.withValues(alpha: 0.1),
              border: Border.all(color: accentColor.withValues(alpha: 0.3)),
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 5),
                Text(
                  title.toUpperCase(),
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: accentColor,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    // Widget centrale personalizzabile
                    centerWidget,
                    const SizedBox(width: 40),
                    // Informazioni dettagliate a destra
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: infoRows.map((info) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 12),
                            child: info.build(),
                          );
                        }).toList(),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Cerchio con icona nell'angolo in alto a destra con effetto fosforescente
          Positioned(
            top: -20,
            right: -20,
            child: Container(
              padding: const EdgeInsets.fromLTRB(30, 40, 40, 30),
              decoration: BoxDecoration(
                color: accentColor.withValues(alpha: 0.3),
                shape: BoxShape.circle,
                border: Border.all(
                  color: accentColor.withValues(alpha: 0.5),
                  width: 4,
                ),
              ),
              child: Icon(topRightIcon, color: Colors.white, size: 24),
            ),
          ),
        ],
      ),
    );
  }
}

// Classe per rappresentare una riga di informazioni
class InfoRow {
  final IconData? icon;
  final Color? iconColor;
  final String label;
  final String value;
  final Color? valueColor;

  InfoRow({
    this.icon,
    this.iconColor,
    required this.label,
    required this.value,
    this.valueColor,
  });

  Widget build() {
    if (icon != null) {
      // Row con icona
      return Row(
        children: [
          Icon(icon, color: iconColor ?? Colors.grey[600], size: 24),
          const SizedBox(width: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: valueColor ?? Colors.black87,
            ),
          ),
        ],
      );
    } else {
      // Row semplice label-value
      return Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontSize: 13, color: Colors.grey[600])),
          Text(
            value,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: valueColor ?? Colors.black87,
            ),
          ),
        ],
      );
    }
  }
}

// Widget helper per il grafico circolare della batteria
class CircularPercentageWidget extends StatelessWidget {
  final double percentage;
  final Color color;
  final Color? lowLevelColor;
  final double lowLevelThreshold;

  const CircularPercentageWidget({
    super.key,
    required this.percentage,
    required this.color,
    this.lowLevelColor,
    this.lowLevelThreshold = 20,
  });

  @override
  Widget build(BuildContext context) {
    final displayColor = percentage > lowLevelThreshold
        ? color
        : (lowLevelColor ?? Colors.redAccent);

    return Stack(
      alignment: Alignment.center,
      children: [
        SizedBox(
          width: 90,
          height: 90,
          child: CircularProgressIndicator(
            value: percentage / 100,
            strokeWidth: 10,
            backgroundColor: Colors.grey.withValues(alpha: 0.2),
            valueColor: AlwaysStoppedAnimation<Color>(displayColor),
          ),
        ),
        Text(
          '${percentage.toInt()}%',
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
      ],
    );
  }
}

// Widget helper per valori numerici semplici
class SimpleValueWidget extends StatelessWidget {
  final String value;
  final String? unit;
  final Color color;

  const SimpleValueWidget({
    super.key,
    required this.value,
    this.unit,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 90,
      height: 90,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        shape: BoxShape.circle,
        border: Border.all(color: color.withValues(alpha: 0.3), width: 3),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            if (unit != null)
              Text(
                unit!,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: color.withValues(alpha: 0.7),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
