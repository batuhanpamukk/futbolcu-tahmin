// lib/futbolcu.dart

class Futbolcu {
  final String isim;
  final String ulke;
  final String kulup;
  final String pozisyon;
  final String piyasaDegeri;
  final String bayrakPath;
  final String fotoPath;
  final String lig; // Yeni alan

  Futbolcu({
    required this.isim,
    required this.ulke,
    required this.kulup,
    required this.pozisyon,
    required this.piyasaDegeri,
    required this.bayrakPath,
    required this.fotoPath,
    required this.lig, // Constructor güncellemesi
  });

  // BURASI EKSİK OLDUĞU İÇİN HATA ALIYORSUN:
  factory Futbolcu.fromJson(Map<String, dynamic> json) {
    return Futbolcu(
      isim: json['isim'],
      ulke: json['ulke'],
      kulup: json['kulup'],
      pozisyon: json['pozisyon'],
      piyasaDegeri: json['piyasaDegeri'],
      bayrakPath: json['bayrakPath'],
      fotoPath: json['fotoPath'],
      lig: json['lig'] ?? "Türkiye Ligi", // Varsayılan değer
    );
  }
}
