import json

# Mapping of player names to their Transfermarkt URLs
url_updates = {
    "Abdülkerim Bardakçı": "https://www.transfermarkt.com.tr/abdulkerim-bardakci/profil/spieler/199316",
    "Ismail Jakobs": "https://www.transfermarkt.com.tr/ismail-jakobs/profil/spieler/375137",
    "Kaan Ayhan": "https://www.transfermarkt.com.tr/kaan-ayhan/profil/spieler/119031",
    "Ahmed Kutucu": "https://www.transfermarkt.com.tr/ahmed-kutucu/profil/spieler/452084",
    "Leroy Sané": "https://www.transfermarkt.com.tr/leroy-sane/profil/spieler/192565",
    "Victor Osimhen": "https://www.transfermarkt.com.tr/victor-osimhen/profil/spieler/401923",
    "Ederson": "https://www.transfermarkt.com.tr/ederson/profil/spieler/238223",
    "Jayden Oosterwolde": "https://www.transfermarkt.com.tr/jayden-oosterwolde/profil/spieler/591361",
    "Rodrigo Becão": "https://www.transfermarkt.com.tr/rodrigo-becao/profil/spieler/410158",
    "Yiğit Efe Demir": "https://www.transfermarkt.com.tr/yigit-efe-demir/profil/spieler/889136",
    "Levent Mercan": "https://www.transfermarkt.com.tr/levent-mercan/profil/spieler/388820",
    "Nélson Semedo": "https://www.transfermarkt.com.tr/nelson-semedo/profil/spieler/231572",
    "Mert Müldür": "https://www.transfermarkt.com.tr/mert-muldur/profil/spieler/353922",
    "Edson Álvarez": "https://www.transfermarkt.com.tr/edson-alvarez/profil/spieler/401356",
    "İsmail Yüksek": "https://www.transfermarkt.com.tr/ismail-yuksek/profil/spieler/613725",
    "Sebastian Szymanski": "https://www.transfermarkt.com.tr/sebastian-szymanski/profil/spieler/320748",
    "Talisca": "https://www.transfermarkt.com.tr/talisca/profil/spieler/258626",
    "Tiago Djaló": "https://www.transfermarkt.com.tr/tiago-djalo/profil/spieler/420465",
    "David Jurásek": "https://www.transfermarkt.com.tr/david-jurasek/profil/spieler/500054",
    "Rıdvan Yılmaz": "https://www.transfermarkt.com.tr/ridvan-yilmaz/profil/spieler/477930"
}

# Load the JSON file
with open('assets/data/futbolcular.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

# Update the URLs
updated_count = 0
for player in players:
    player_name = player.get('isim')
    if player_name in url_updates:
        player['url'] = url_updates[player_name]
        updated_count += 1
        print(f"✅ Updated URL for: {player_name}")

# Save the updated JSON
with open('assets/data/futbolcular.json', 'w', encoding='utf-8') as f:
    json.dump(players, f, ensure_ascii=False, indent=4)

print(f"\nTotal: {updated_count} URLs added successfully!")
