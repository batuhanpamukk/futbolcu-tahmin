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

  // Define headers to mimic a browser
  final headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
  };

  final jsonString = await file.readAsString();
  final List<dynamic> data = jsonDecode(jsonString);
  bool isModified = false;

  for (var player in data) {
    if (player['url'] != null && player['url'].toString().isNotEmpty) {
      final url = player['url'] as String;
      print('Updating: ${player['isim']} from $url...');

      try {
        final response = await http.get(Uri.parse(url), headers: headers);

        if (response.statusCode == 200) {
          final document = parser.parse(response.body);

          // 1. Piyasa Değeri / Market Value
          final marketValueElement = document.querySelector('.data-header__market-value-wrapper');
          String? marketValue;
          
          if (marketValueElement != null) {
              var rawText = marketValueElement.text.trim();
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
                           marketValue = '${(val/1000).toStringAsFixed(2)} Milyon €';
                        } catch(e) {
                            marketValue = '$amount Bin €';
                        }
                   }
               }
          }

          // 2. Kulüp / Club
          final clubElement = document.querySelector('.data-header__club a');
          String? club = clubElement?.attributes['title'] ?? clubElement?.text.trim();
          
          if(club != null && club.isNotEmpty){
             if(club.contains('Galatasaray')) club = 'Galatasaray';
             if(club.contains('Fenerbahçe')) club = 'Fenerbahçe';
             if(club.contains('Beşiktaş')) club = 'Beşiktaş';
             if(club.contains('Trabzonspor')) club = 'Trabzonspor';
             // Shorten İstanbul Başakşehir
             if(club.contains('Başakşehir')) club = 'İstanbul Başakşehir FK';
          }

          // 3. Resim / Image
          // The profile image is usually the og:image or inside .modal-trigger img
          // Or <img class="data-header__profile-image" src="..." ...>
          var imageUrl = document.querySelector('.data-header__profile-image')?.attributes['src'];
          // Sometimes it might be data-src or something else, but src is standard for this class usually.
          // If not found, try og:image
          if(imageUrl == null) {
             imageUrl = document.querySelector('meta[property="og:image"]')?.attributes['content'];
          }

          if (imageUrl != null && imageUrl.isNotEmpty) {
            final localPath = player['fotoPath'] as String;
            final file = File(localPath);
            // Download if missing or maybe we want to force update? For now, download if missing.
            // Or if the user wants to update everything, we can force it.
            // Let's always download to ensure we get the latest clean image.
            
            // Transfermarkt images often have small sizes or query params.
            // The one finding in source was "https://img.a.transfermarkt.technology/portrait/header/..."
            // We should use that.
            
            try {
                final imageResponse = await http.get(Uri.parse(imageUrl), headers: headers);
                if (imageResponse.statusCode == 200) {
                    await file.writeAsBytes(imageResponse.bodyBytes);
                    print('  - Image downloaded to $localPath');
                }
            } catch (e) {
                print('  - Failed to download image: $e');
            }
          }


          // 4. Pozisyon / Position
          // Search for "Mevki:" label
          String? position;
          final detailsItems = document.querySelectorAll('.data-header__details li');
          for (var item in detailsItems) {
            final label = item.querySelector('.data-header__label')?.text.trim();
            if (label != null && label.startsWith('Mevki')) {
               position = item.querySelector('.data-header__content')?.text.trim();
               break;
            }
          }
          
          if (position != null) {
              // Cleanup position text if needed (e.g. "Defans - Stoper" -> "Stoper")
              // Usually it comes as "Stoper" or "Kaleci" directly on TR site
              // But sometimes "Orta saha" etc.
              // Let's keep it as retrieved for now, maybe trim.
              position = position.trim();
          }

          // Update JSON if we found data
          if(marketValue != null) {
              if (player['piyasaDegeri'] != marketValue) {
                  print('  - Market Value: ${player['piyasaDegeri']} -> $marketValue');
                  player['piyasaDegeri'] = marketValue;
                  isModified = true;
              }
          }
          
          if(club != null) {
              if (player['kulup'] != club) {
                  print('  - Club: ${player['kulup']} -> $club');
                  player['kulup'] = club;
                  isModified = true;
              }
          }
          
          if(position != null) {
              if (player['pozisyon'] != position) {
                  print('  - Position: ${player['pozisyon']} -> $position');
                  player['pozisyon'] = position;
                  isModified = true;
              }
          }

        } else {
          print('Failed to fetch $url: ${response.statusCode}');
        }
      } catch (e) {
        print('Error fetching $url: $e');
      }
      
      // Be nice to the server
      await Future.delayed(Duration(seconds: 1));
    }
  }

  if (isModified) {
    // Pretty print the JSON
    const encoder = JsonEncoder.withIndent('    ');
    await file.writeAsString(encoder.convert(data));
    print('Successfully updated futbolcular.json');
  } else {
    print('No changes made.');
  }
}
