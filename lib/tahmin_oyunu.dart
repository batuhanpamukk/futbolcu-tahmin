import 'package:flutter/material.dart';
import 'dart:ui';
import 'dart:async';
import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart'; // compute için
import 'package:audioplayers/audioplayers.dart';
import 'futbolcu.dart';
import 'snow_animation.dart';

// Arka planda JSON parse işlemi yapacak fonksiyon (Top-Level olmalı)
List<Futbolcu> parseFutbolcular(String responseBody) {
  final parsed = json.decode(responseBody).cast<Map<String, dynamic>>();
  return parsed.map<Futbolcu>((json) => Futbolcu.fromJson(json)).toList();
}

enum GameMode { easy, hard, god }

class TahminOyunu extends StatefulWidget {
  const TahminOyunu({super.key});

  @override
  State<TahminOyunu> createState() => _TahminOyunuState();
}

class _TahminOyunuState extends State<TahminOyunu> {
  Futbolcu? _tahminEdilecekFutbolcu;
  List<Futbolcu> _tumFutbolcular = [];
  List<Futbolcu> _kalanFutbolcular = [];

  // BU FONKSİYON ARTIK HEM TÜRKÇE HEM DE AKSANLI HARFLERİ (Á, É vb.) TEMİZLİYOR
  String _metniTemizle(String metin) {
    if (metin.isEmpty) return "";
    var kaynak = metin.toLowerCase().trim();

    var degisimler = {
      'á': 'a',
      'à': 'a',
      'â': 'a',
      'ä': 'a',
      'é': 'e',
      'è': 'e',
      'ê': 'e',
      'ë': 'e',
      'í': 'i',
      'ì': 'i',
      'î': 'i',
      'ï': 'i',
      'ı': 'i',
      'ó': 'o',
      'ò': 'o',
      'ô': 'o',
      'ö': 'o',
      'ú': 'u',
      'ù': 'u',
      'û': 'u',
      'ü': 'u',
      'ç': 'c',
      'ş': 's',
      'ğ': 'g',
      'ñ': 'n',
      'ć': 'c',
      'š': 's',
      'İ': 'i',
      'I': 'i',
      'I': 'i',
    };

    degisimler.forEach((eski, yeni) {
      kaynak = kaynak.replaceAll(eski, yeni);
    });

    return kaynak;
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Arka plan resmini önceden yükle (Klavye açılışındaki takılmayı azaltır)
    precacheImage(const AssetImage('assets/backgrounds/saha_background.png'), context);
  }

  final TextEditingController _textController = TextEditingController();
  String _kullaniciTahmini = '';
  String _geriBildirim = '';
  bool _dogruTahminEdildi = false;
  bool _yukleniyor = true;
  int _skor = 0;
  
  int _rekorKolay = 0;
  int _rekorZor = 0;
  int _rekorGod = 0; // Yeni God Mod rekoru

  bool _oyunBasladi = false;
  GameMode _activeMode = GameMode.easy; // Varsayılan mod

  int _kalanSure = 10;
  int _kalanPasHakki = 3;
  Timer? _timer;
  
  // Müzik player
  final AudioPlayer _audioPlayer = AudioPlayer();

  @override
  void initState() {
    super.initState();
    _rekorlariYukle();
    _verileriYukle();
    _muzikBaslat();
  }
  
  Future<void> _muzikBaslat() async {
    // UI çizildikten sonra çalışması için
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      try {
        debugPrint('AUDIO_DEBUG: Müzik başlatma süreci tetiklendi.');

        // Ses Yöneticisi Ayarları
        await _audioPlayer.setAudioContext(
          AudioContext(
            iOS: AudioContextIOS(
              category: AVAudioSessionCategory.playback,
              options: {
                AVAudioSessionOptions.mixWithOthers, 
              },
            ),
            android: AudioContextAndroid(
              isSpeakerphoneOn: true,
              stayAwake: true,
              contentType: AndroidContentType.music,
              usageType: AndroidUsageType.media,
              audioFocus: AndroidAudioFocus.none,
            ),
          ),
        );
        debugPrint('AUDIO_DEBUG: AudioContext ayarlandı.');

        await _audioPlayer.setReleaseMode(ReleaseMode.loop);
        debugPrint('AUDIO_DEBUG: Loop modu ayarlandı.');

        // 1. YÖNTEM: Normal AssetSource
        try {
           debugPrint('AUDIO_DEBUG: 1. Yöntem (AssetSource) deneniyor...');
           await _audioPlayer.setSource(AssetSource('music/winter_music.mp3'));
           await _audioPlayer.setVolume(1.0);
           await _audioPlayer.resume();
           debugPrint('AUDIO_DEBUG: 1. Yöntem BAŞARILI. Müzik çalıyor olmalı.');
           return; 
        } catch (e1) {
           debugPrint('AUDIO_DEBUG: 1. Yöntem HATA: $e1');
        }

        // 2. YÖNTEM: Manuel Byte Yükleme (Daha garantidir)
        try {
          debugPrint('AUDIO_DEBUG: 2. Yöntem (rootBundle + BytesSource) deneniyor...');
          final bytes = await rootBundle.load('assets/music/winter_music.mp3');
          final audioBytes = bytes.buffer.asUint8List();
          
          await _audioPlayer.setSource(BytesSource(audioBytes));
          await _audioPlayer.setVolume(1.0);
          await _audioPlayer.resume();
          debugPrint('AUDIO_DEBUG: 2. Yöntem BAŞARILI. Byte üzerinden çalınıyor.');
        } catch (e2) {
          debugPrint('AUDIO_DEBUG: 2. Yöntem HATA: $e2');
          debugPrint('AUDIO_DEBUG: Müzik dosyası yüklenemedi. Lütfen dosya yolunu kontrol edin.');
        }
        
      } catch (e) {
        debugPrint('AUDIO_DEBUG: Genel Müzik Başlatma Hatası: $e');
      }
    });
  }

  Future<void> _rekorlariYukle() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _rekorKolay = prefs.getInt('score_easy') ?? 0;
      _rekorZor = prefs.getInt('score_hard') ?? 0;
      _rekorGod = prefs.getInt('score_god') ?? 0;
    });
  }

  double _piyasaDegeriniSayiyaCevir(String metin) {
    if (metin.isEmpty || metin == "-") return 0.0;
    
    // Temel temizlik: "5.00 mil. €" -> "5.00 mil.", "500 bin €" -> "500 bin"
    String islenen = metin.toLowerCase().replaceAll("€", "").trim();
    
    // Bin kontrolü (Bin € -> Milyon € dönüşümü için /1000)
    bool binVar = islenen.contains("bin");
    
    // Sadece sayısal kısmı al (boşluk veya harf görünce kesebiliriz veya regex)
    // Basit yaklaşım: "bin", "mil", "milyon" kelimelerini atıp parse etmek
    String sayiStr = islenen
        .replaceAll("bin", "")
        .replaceAll("mil.", "")
        .replaceAll("milyon", "")
        .trim();
        
    // Virgülleri noktaya çevir (5,00 -> 5.00)
    sayiStr = sayiStr.replaceAll(",", ".");
    
    double deger = double.tryParse(sayiStr) ?? 0.0;
    
    if (binVar) {
      return deger / 1000.0;
    }
    
    return deger;
  }

  Future<void> _verileriYukle() async {
    try {
      final String response = await rootBundle.loadString(
        'assets/data/futbolcular.json',
      );
      // compute ile arka planda parse etme (UI donmasını engeller)
      final List<Futbolcu> data = await compute(parseFutbolcular, response);
      
      setState(() {
        _tumFutbolcular = data;
        _yukleniyor = false;
      });
    } catch (e) {
      debugPrint("Hata oluştu: $e");
    }
  }

  // LİG SEÇİMİ İÇİN YENİ DEĞİŞKENLER
  final List<String> _mevcutLigler = ["Türkiye Ligi", "İngiltere Ligi", "İspanya Ligi", "İtalya Ligi", "Almanya Ligi"];
  List<String> _secilenLigler = [];

  void _oyunModunuSec(GameMode mode) {
    if (_tumFutbolcular.isEmpty) return;
    
    // Modu kaydet (Dialog içinde kullanılacak)
    setState(() {
      _activeMode = mode;
      _secilenLigler = ["Türkiye Ligi"]; // Varsayılan olarak TR seçili gelsin
    });

    // Lig Seçimi Dialogunu Göster
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setStateDialog) {
            return AlertDialog(
              backgroundColor: Colors.grey.shade900,
              title: const Text(
                "LİG SEÇİMİ",
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: _mevcutLigler.map((lig) {
                  // Lig ismine göre bayrak belirle
                  String bayrakPath = "";
                  if (lig == "Türkiye Ligi") {
                    bayrakPath = "assets/flags/turkey.png";
                  } else if (lig == "İngiltere Ligi") {
                    bayrakPath = "assets/flags/england.png";
                  } else if (lig == "İspanya Ligi") {
                    bayrakPath = "assets/flags/spain.png";
                  } else if (lig == "İtalya Ligi") {
                    bayrakPath = "assets/flags/italy.png";
                  } else if (lig == "Almanya Ligi") {
                    bayrakPath = "assets/flags/germany.png";
                  }

                  return CheckboxListTile(
                    title: Row(
                      children: [
                        if (bayrakPath.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(right: 10.0),
                            child: Image.asset(bayrakPath, width: 24, height: 24),
                          ),
                        Text(lig, style: const TextStyle(color: Colors.white)),
                      ],
                    ),
                    value: _secilenLigler.contains(lig),
                    activeColor: Colors.green,
                    checkColor: Colors.white,
                    onChanged: (bool? value) {
                      setStateDialog(() {
                        if (value == true) {
                          _secilenLigler.add(lig);
                        } else {
                          // En az bir lig seçili kalmalı
                          if (_secilenLigler.length > 1) {
                            _secilenLigler.remove(lig);
                          }
                        }
                      });
                    },
                  );
                }).toList(),
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.pop(context); // Dialogu kapat
                    // Seçim iptal edildi, oyun başlamıyor
                  },
                  child: const Text("İPTAL", style: TextStyle(color: Colors.red)),
                ),
                ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context); // Dialogu kapat
                    _oyunuBaslat(); // Oyunu başlat
                  },
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                  child: const Text("DEVAM ET", style: TextStyle(color: Colors.white)),
                ),
              ],
            );
          },
        );
      },
    );
  }

  void _oyunuBaslat() {
      setState(() {
      _oyunBasladi = true;
      _skor = 0;
      _kalanPasHakki = 3; 
      
      _kalanFutbolcular = _tumFutbolcular.where((f) {
        // 1. Lig Filtresi
        if (!_secilenLigler.contains(f.lig)) return false;

        // 2. Piyasa Değeri / Zorluk Filtresi
        double val = _piyasaDegeriniSayiyaCevir(f.piyasaDegeri);
        switch (_activeMode) {
          case GameMode.easy:
            // Kolay: > 10 Milyon
            return val > 10.0;
          case GameMode.hard:
            // Zor: 5 Milyon <= X <= 10 Milyon
            return val >= 5.0 && val <= 10.0;
          case GameMode.god:
            // God Mod: 1 Milyon <= X < 5 Milyon
            return val >= 1.0 && val < 5.0; 
        }
      }).toList();

      if (_kalanFutbolcular.isEmpty) {
        _oyunBasladi = false;
        ScaffoldMessenger.of(context).showSnackBar(
           const SnackBar(content: Text("Bu kriterde oyuncu bulunamadı!")),
        );
        return;
      }
      _kalanFutbolcular.shuffle();
      _yeniOyunBaslat();
    });
  }

  void _yeniOyunBaslat() {
    _timer?.cancel();
    if (_kalanFutbolcular.isEmpty) {
      _oyunBitti("Efsane! Tüm kadroyu bitirdin! 🦁");
      return;
    }
    setState(() {
      _tahminEdilecekFutbolcu = _kalanFutbolcular.removeLast();
      _kullaniciTahmini = '';
      _dogruTahminEdildi = false;
      // God ve Zor modda süre var
      bool sureliMod = (_activeMode == GameMode.hard || _activeMode == GameMode.god);
      _geriBildirim = sureliMod ? '10 Saniyen Var!' : 'Hadi Tahmin Et!';
      _textController.clear();
    });
    
    if (_activeMode == GameMode.hard || _activeMode == GameMode.god) {
        _sureyiBaslat();
    }
  }

  void _sureyiBaslat() {
    _timer?.cancel();
    setState(() => _kalanSure = 10);
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_kalanSure > 0) {
        setState(() => _kalanSure--);
      } else {
        _timer?.cancel();
        _oyunBitti("Süre doldu!");
      }
    });
  }

  void _tahminiKontrolEt() {
    if (_tahminEdilecekFutbolcu == null) return;

    // Hem tahmini hem gerçek ismi gelişmiş temizleyiciden geçiriyoruz
    final tahminTemiz = _metniTemizle(_kullaniciTahmini);
    final tamIsimTemiz = _metniTemizle(_tahminEdilecekFutbolcu!.isim);
    final isimParcalari = tamIsimTemiz.split(' ');

    setState(() {
      // 1. Tam eşleşme (alvarez == alvarez)
      // 2. Soyisim eşleşmesi (isim parçalarından biriyle eşleşme)
      bool dogruMu =
          (tahminTemiz == tamIsimTemiz) ||
          (tahminTemiz.length >= 3 && isimParcalari.contains(tahminTemiz));

      if (dogruMu) {
        _timer?.cancel();
        _dogruTahminEdildi = true;

        _skor++;
        
        // Rekor kontrolü ve kaydetme
        _rekoruGuncelle();
        
        _geriBildirim = '🎉 TEBRİKLER!';
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) _yeniOyunBaslat();
        });
      } else {
        _geriBildirim = '❌ Yanlış! Tekrar dene.';
      }
    });

  }

  Future<void> _rekoruGuncelle() async {
      final prefs = await SharedPreferences.getInstance();
      
      switch (_activeMode) {
        case GameMode.easy:
          if (_skor > _rekorKolay) {
              _rekorKolay = _skor;
              prefs.setInt('score_easy', _rekorKolay);
          }
          break;
        case GameMode.hard:
          if (_skor > _rekorZor) {
              _rekorZor = _skor;
              prefs.setInt('score_hard', _rekorZor);
          }
          break;
        case GameMode.god:
          if (_skor > _rekorGod) {
              _rekorGod = _skor;
              prefs.setInt('score_god', _rekorGod); // God Mode için KEY: score_god
          }
          break;
      }
  }

  void _oyunBitti(String mesaj) {
    _timer?.cancel();
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey.shade900,
        title: const Text(
          "OYUN BİTTİ",
          style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
        ),
        content: Text(
          "$mesaj \nSkorun: $_skor",
          style: const TextStyle(color: Colors.white),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() => _oyunBasladi = false);
            },
            child: const Text("ANA MENÜ"),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _textController.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }

  bool _sesAcik = true;

  void _sesiAcKapat() {
    setState(() {
      _sesAcik = !_sesAcik;
    });
    if (_sesAcik) {
      _audioPlayer.setVolume(1.0);
    } else {
      _audioPlayer.setVolume(0.0);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_yukleniyor) {
      return const Scaffold(
        backgroundColor: Colors.black,
        body: Center(child: CircularProgressIndicator(color: Colors.yellow)),
      );
    }
    // Klavye açık mı kontrolü
    final isKeyboardOpen = MediaQuery.of(context).viewInsets.bottom > 0;

    return Scaffold(
      // resizeToAvoidBottomInset: true, // Varsayılan değer true'dur, ekran klavye açılınca sıkışır
      body: GestureDetector(
        onTap: () => FocusScope.of(context).unfocus(), // 3. Boşluğa tıklayınca klavye kapansın
        child: Stack(
          children: [
            Container(
              width: double.infinity,
              height: double.infinity,
              decoration: const BoxDecoration(
                image: DecorationImage(
                  image: AssetImage('assets/backgrounds/saha_background.png'),
                  fit: BoxFit.cover,
                ),
              ),
              child: _oyunBasladi ? _oyunEkrani() : _menuEkrani(),
            ),
            // Kar animasyonu - menüde yoğun, oyunda hafif
            // IgnorePointer: Kar tıklamaları engellemez
            IgnorePointer(
              child: SnowfallWidget(
                particleCount: _oyunBasladi ? 40 : 120,
                maxRadius: 3.5,
                maxSpeed: 2.0,
              ),
            ),
            // Sadece klavye KAPALIYSA home butonunu göster (Oyun Modunda)
            if (_oyunBasladi && !isKeyboardOpen)
              Positioned(
                bottom: 30,
                right: 20,
                child: GestureDetector(
                  onTap: () {
                    _timer?.cancel();
                    setState(() => _oyunBasladi = false);
                  },
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.7),
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.orange, width: 2),
                    ),
                    child: const Icon(
                      Icons.home_rounded,
                      color: Colors.white,
                      size: 30,
                    ),
                  ),
                ),
              ),

             // Ses Kapatma Butonu (Sadece Menüde) - Sol Alt
            if (!_oyunBasladi)
              Positioned(
                bottom: 30,
                left: 20,
                child: GestureDetector(
                  onTap: _sesiAcKapat,
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.7),
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.orange, width: 2),
                    ),
                    child: Icon(
                      _sesAcik ? Icons.volume_up : Icons.volume_off,
                      color: Colors.white,
                      size: 30,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _menuEkrani() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buyukModButonu("KOLAY", Colors.blue, GameMode.easy),
          const SizedBox(height: 15),
          _buyukModButonu("ZOR", Colors.orange, GameMode.hard),
          const SizedBox(height: 15),
          _buyukModButonu("GOD MOD", Colors.red, GameMode.god),
        ],
      ),
    );
  }

  Widget _buyukModButonu(String metin, Color renk, GameMode mode) {
    return InkWell(
      onTap: () => _oyunModunuSec(mode),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Container(
            width: 250,
            padding: const EdgeInsets.symmetric(vertical: 20),
            decoration: BoxDecoration(
              color: renk.withOpacity(0.8),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.white70, width: 2),
               boxShadow: [
                BoxShadow(
                  color: renk.withOpacity(0.5),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                )
              ],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // İkon kaldırıldı (Kullanıcı isteği)
                // Icon(ikon, color: Colors.white, size: 30),
                // const SizedBox(width: 15),
                Text(
                  metin,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          // Kış şapkası görseli - Sağ üst köşe
          Positioned(
            right: -20, // Kavisin üzerine oturması için
            top: -14,   // Biraz daha aşağı indirildi
            child: Image.asset(
              'assets/images/santa_hat.png',
              width: 75, 
            ),
          ),
        ],
      ),
    );
  }

  Widget _oyunEkrani() {
    return SafeArea(
      child: SingleChildScrollView(
        // Klavye açılınca ekran otomatik küçüldüğü için ekstra padding'e gerek yok
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Column(
            children: [
              _ustBilgiSatiri(),
              const SizedBox(height: 20),
              _oyuncuResmi(),
              const SizedBox(height: 25),
              _ipucuKarti(),
              const SizedBox(height: 25),
              _tahminInput(),
              const SizedBox(height: 20),
              _butonlar(),
              const SizedBox(height: 30),
              Text(
                _geriBildirim,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.yellow,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _ustBilgiSatiri() {
    // Aktif moda göre kaydedilen rekoru seç
    int gosterilecekRekor = 0;
    switch (_activeMode) {
      case GameMode.easy:
        gosterilecekRekor = _rekorKolay;
        break;
      case GameMode.hard:
        gosterilecekRekor = _rekorZor;
        break;
      case GameMode.god:
        gosterilecekRekor = _rekorGod;
        break;
    }

    // Süreli mod mu?
    bool sureliMod = (_activeMode == GameMode.hard || _activeMode == GameMode.god);

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _skorKutusu("SKOR", _skor, Colors.blue),
        if (sureliMod) _skorKutusu("SÜRE", _kalanSure, Colors.red),
        _skorKutusu("REKOR", gosterilecekRekor, Colors.orange),
      ],
    );
  }

  Widget _oyuncuResmi() {
    final String path = _tahminEdilecekFutbolcu!.fotoPath;
    return Container(
      height: 160,
      width: 160,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: Colors.white, width: 3),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(80),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Image.asset(
              path,
              height: 300,
              fit: BoxFit.cover,
              errorBuilder: (c, e, s) => _hataResmi(),
            ),
            if (!_dogruTahminEdildi)
              BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                child: Container(color: Colors.black12),
              ),
          ],
        ),
      ),
    );
  }

  Widget _hataResmi() => Container(
    color: Colors.grey[300],
    child: const Icon(Icons.person, size: 100, color: Colors.grey),
  );

  Widget _ipucuKarti() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.black54,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Ülke: ${_tahminEdilecekFutbolcu!.ulke}',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 10),
              // BURASI ARTIK JSON'DAN GELEN DOĞRU BAYRAK YOLUNU KULLANIYOR
              Image.asset(
                _tahminEdilecekFutbolcu!.bayrakPath,
                width: 30,
                errorBuilder: (c, e, s) =>
                    const Icon(Icons.flag, color: Colors.white),
              ),
            ],
          ),
          const Divider(color: Colors.white24, height: 20),
          _ipucuSatiri("Kulüp", _tahminEdilecekFutbolcu!.kulup),
          _ipucuSatiri("Pozisyon", _tahminEdilecekFutbolcu!.pozisyon),
          _ipucuSatiri("Piyasa Değeri", _tahminEdilecekFutbolcu!.piyasaDegeri),
        ],
      ),
    );
  }

  Widget _tahminInput() {
    return TextField(
      controller: _textController,
      style: const TextStyle(color: Colors.white),
      textAlign: TextAlign.center,
      decoration: InputDecoration(
        hintText: 'Tahminin...',
        hintStyle: const TextStyle(color: Colors.white60),
        filled: true,
        fillColor: Colors.black45,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(15),
          borderSide: BorderSide.none,
        ),
      ),
      onChanged: (v) => _kullaniciTahmini = v,
      onSubmitted: (_) => _tahminiKontrolEt(),
    );
  }

  Widget _butonlar() {
    bool sureliMod = (_activeMode == GameMode.hard || _activeMode == GameMode.god);
    
    return Row(
      children: [
        Expanded(
          flex: 2,
          child: ElevatedButton(
            onPressed: _tahminiKontrolEt,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
            child: const Text(
              "TAHMİN ET",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          flex: 1,
          child: ElevatedButton(
            onPressed: () {
              if (sureliMod && _kalanPasHakki > 0) {
                setState(() => _kalanPasHakki--);
                _yeniOyunBaslat();
              } else if (!sureliMod) {
                _yeniOyunBaslat();
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
            child: Text(
              sureliMod ? "PAS ($_kalanPasHakki)" : "PAS",
              style: const TextStyle(color: Colors.white),
            ),
          ),
        ),
      ],
    );
  }

  Widget _skorKutusu(String baslik, int deger, Color renk) {
    return Container(
      width: 70,
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: renk),
      ),
      child: Column(
        children: [
          Text(baslik, style: TextStyle(color: renk, fontSize: 10)),
          Text(
            deger.toString(),
            style: const TextStyle(color: Colors.white, fontSize: 16),
          ),
        ],
      ),
    );
  }

  Widget _ipucuSatiri(String b, String d) => Padding(
    padding: const EdgeInsets.only(bottom: 5),
    child: Text("$b: $d", style: const TextStyle(color: Colors.white)),
  );
}
