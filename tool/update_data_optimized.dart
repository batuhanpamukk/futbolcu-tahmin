import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:html/parser.dart' as parser;

void main() async {
  final file = File('assets/data/futbolcular.json');
  if (!file.existsSync()) {
    print('Error: futbolcular.json not found!');
    exit(1);
  }

  // Mimic browser
  final headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
  };

  final jsonString = await file.readAsString();
  final List<dynamic> data = jsonDecode(jsonString);
  
  int totalWithUrl = 0;
  for (var p in data) {
      if (p['url'] != null && p['url'].toString().isNotEmpty) totalWithUrl++;
  }
  
  print('Total players with URL: $totalWithUrl');
  
  int processedCount = 0;
  int updatedCount = 0;
  bool isModifiedBatch = false;

  for (int i = 0; i < data.length; i++) {
    var player = data[i];
    if (player['url'] == null || player['url'].toString().isEmpty) {
        continue;
    }
    
    final url = player['url'] as String;
    processedCount++; // count only processed
    // print('Processing $processedCount/$totalWithUrl: ${player['isim']}');

    try {
      final response = await http.get(Uri.parse(url), headers: headers);
      if (response.statusCode == 200) {
        final document = parser.parse(response.body);
        
        // 1. Piyasa Değeri
        final marketValueElement = document.querySelector('.data-header__market-value-wrapper');
        String? marketValue;
        
        if (marketValueElement != null) {
            String rawText = marketValueElement.text.trim();
            // multiple spaces to one
            rawText = rawText.replaceAll(RegExp(r'\s+'), ' ');
            
             final valueMatch = RegExp(r'([\d,.]+)\s*(mil\.|bin)\s*€').firstMatch(rawText);
             if(valueMatch != null) {
                 String amount = valueMatch.group(1)!;
                 String unit = valueMatch.group(2)!;
                 
                 if(unit == 'mil.'){
                     marketValue = '$amount Milyon €';
                 } else if (unit == 'bin') {
                      try {
                         double val = double.parse(amount.replaceAll(',', '.'));
                         // e.g. 500 bin -> 0.50 Milyon
                         marketValue = '${(val/1000).toStringAsFixed(2)} Milyon €';
                      } catch(e) {
                          marketValue = '$amount Bin €';
                      }
                 }
             }
        }
        
        // Club
        final clubElement = document.querySelector('.data-header__club a');
          String? club = clubElement?.attributes['title'] ?? clubElement?.text.trim();
          
          if(club != null && club.isNotEmpty){
             if(club.contains('Galatasaray')) club = 'Galatasaray';
             if(club.contains('Fenerbahçe')) club = 'Fenerbahçe';
             if(club.contains('Beşiktaş')) club = 'Beşiktaş';
             if(club.contains('Trabzonspor')) club = 'Trabzonspor';
             if(club.contains('Başakşehir')) club = 'İstanbul Başakşehir FK';
          }
          
        // Position
         String? position;
          final detailsItems = document.querySelectorAll('.data-header__details li');
          for (var item in detailsItems) {
            final label = item.querySelector('.data-header__label')?.text.trim();
            if (label != null && label.startsWith('Mevki')) {
               position = item.querySelector('.data-header__content')?.text.trim();
               break;
            }
          }
          if (position != null) position = position.trim();


        // Update Logic
        bool localChange = false;
        
        if(marketValue != null) {
             if (player['piyasaDegeri'] != marketValue) {
                 print('[UPDATE] ${player['isim']}: ${player['piyasaDegeri']} -> $marketValue');
                 player['piyasaDegeri'] = marketValue;
                 localChange = true;
             }
        }
        
        if(club != null && player['kulup'] != club) {
             // print('[UPDATE] ${player['isim']} Club: ${player['kulup']} -> $club');
             player['kulup'] = club;
             localChange = true;
        }
        
        if(position != null && player['pozisyon'] != position) {
             // print('[UPDATE] ${player['isim']} Pos: ${player['pozisyon']} -> $position');
             player['pozisyon'] = position;
             localChange = true;
        }

        if (localChange) {
            updatedCount++;
            isModifiedBatch = true;
        }

      } else {
        print('[ERROR] ${response.statusCode} for $url');
      }
    } catch (e) {
      print('[EXCEPTION] $e for $url');
    }
    
    // Save every 20 processed items (changed locally) or every 50 loops?
    // Let's check logic: processedCount is incremented.
    // If multiple items are processed and modified, we should save.
    // If not modified, we don't save.
    
    if (processedCount % 50 == 0 || processedCount == totalWithUrl) {
       if (isModifiedBatch) {
           print('Saving progress at $processedCount/$totalWithUrl...');
           const encoder = JsonEncoder.withIndent('    ');
           await file.writeAsString(encoder.convert(data));
           isModifiedBatch = false;
       } else {
           print('Progress $processedCount/$totalWithUrl (no changes to save)');
       }
    }
    
    // Delay 300ms
    await Future.delayed(Duration(milliseconds: 300));
  }
  
  // Final save if pending changes? The loop above covers 'processedCount == totalWithUrl' case.
  // But just in case
  if (isModifiedBatch) {
       print('Saving final changes...');
       const encoder = JsonEncoder.withIndent('    ');
       await file.writeAsString(encoder.convert(data));
  }
  print('Done. Total updated: $updatedCount / $processedCount');
}
