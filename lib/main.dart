// lib/main.dart
import 'package:flutter/material.dart';
import 'tahmin_oyunu.dart'; // Kendi widget'ımızı içeri aktardık

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Futbol Tahmin Oyunu',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const TahminOyunu(), // Uygulamanın başlayacağı ekran
      debugShowCheckedModeBanner:
          false, // Sağ üstteki "DEBUG" yazısını kaldırır
    );
  }
}
