import 'package:flutter/material.dart';
import 'dart:math' as math;

class Snowflake {
  double x;
  double y;
  double radius;
  double speed;
  double drift; // Yatay hareket için

  Snowflake({
    required this.x,
    required this.y,
    required this.radius,
    required this.speed,
    required this.drift,
  });
}

class SnowfallWidget extends StatefulWidget {
  final int particleCount;
  final double maxRadius;
  final double maxSpeed;

  const SnowfallWidget({
    Key? key,
    this.particleCount = 100,
    this.maxRadius = 3.0,
    this.maxSpeed = 2.0,
  }) : super(key: key);

  @override
  State<SnowfallWidget> createState() => _SnowfallWidgetState();
}

class _SnowfallWidgetState extends State<SnowfallWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  List<Snowflake> snowflakes = [];
  final math.Random random = math.Random();

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat();

    _controller.addListener(() {
      setState(() {
        _updateSnowflakes();
      });
    });
  }

  void _initSnowflakes(Size size) {
    if (snowflakes.isEmpty) {
      for (int i = 0; i < widget.particleCount; i++) {
        snowflakes.add(Snowflake(
          x: random.nextDouble() * size.width,
          y: random.nextDouble() * size.height,
          radius: random.nextDouble() * widget.maxRadius + 1,
          speed: random.nextDouble() * widget.maxSpeed + 0.5,
          drift: (random.nextDouble() - 0.5) * 0.5, // Hafif sağa sola kayma
        ));
      }
    }
  }

  void _updateSnowflakes() {
    for (var snowflake in snowflakes) {
      snowflake.y += snowflake.speed;
      snowflake.x += snowflake.drift;

      // Ekranın altına ulaştığında yukarıdan başlat
      if (snowflake.y > MediaQuery.of(context).size.height) {
        snowflake.y = -10;
        snowflake.x = random.nextDouble() * MediaQuery.of(context).size.width;
      }

      // Yanlara taşarsa karşı taraftan getir
      if (snowflake.x < 0) {
        snowflake.x = MediaQuery.of(context).size.width;
      } else if (snowflake.x > MediaQuery.of(context).size.width) {
        snowflake.x = 0;
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        _initSnowflakes(constraints.biggest);
        return CustomPaint(
          size: constraints.biggest,
          painter: SnowfallPainter(snowflakes: snowflakes),
        );
      },
    );
  }
}

class SnowfallPainter extends CustomPainter {
  final List<Snowflake> snowflakes;

  SnowfallPainter({required this.snowflakes});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.8)
      ..style = PaintingStyle.fill;

    for (var snowflake in snowflakes) {
      canvas.drawCircle(
        Offset(snowflake.x, snowflake.y),
        snowflake.radius,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
