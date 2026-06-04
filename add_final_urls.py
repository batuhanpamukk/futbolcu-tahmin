import json

# Final batch of missing URLs
final_url_updates = {
    "Abdülkerim Bardakçı": "https://www.transfermarkt.com.tr/abdulkerim-bardakci/profil/spieler/199316",
    "Taylan Bulut": "https://www.transfermarkt.com.tr/taylan-bulut/profil/spieler/810100",
    "Wilfred Ndidi": "https://www.transfermarkt.com.tr/wilfred-ndidi/profil/spieler/274839",
    "Demir Ege Tıknaz": "https://www.transfermarkt.com.tr/demir-ege-tiknaz/profil/spieler/875337",
    "Orkun Kökçü": "https://www.transfermarkt.com.tr/orkun-kokcu/profil/spieler/454567",
    "Jota Silva": "https://www.transfermarkt.com.tr/jota-silva/profil/spieler/663244",
    "Vaclav Cerny": "https://www.transfermarkt.com.tr/vaclav-cerny/profil/spieler/242063",
    "Cengiz Ünder": "https://www.transfermarkt.com.tr/cengiz-under/profil/spieler/341647",
    "El Bilal Touré": "https://www.transfermarkt.com.tr/el-bilal-toure/profil/spieler/649016",
    "Tammy Abraham": "https://www.transfermarkt.com.tr/tammy-abraham/profil/spieler/331726",
    "Andre Onana": "https://www.transfermarkt.com.tr/andre-onana/profil/spieler/234509",
    "Benjamin Bouchouari": "https://www.transfermarkt.com.tr/benjamin-bouchouari/profil/spieler/783094"
}

# Load the JSON file
with open('assets/data/futbolcular.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

# Update the URLs
updated_count = 0
for player in players:
    player_name = player.get('isim')
    if player_name in final_url_updates:
        player['url'] = final_url_updates[player_name]
        updated_count += 1
        print(f"✅ Updated URL for: {player_name}")

# Save the updated JSON
with open('assets/data/futbolcular.json', 'w', encoding='utf-8') as f:
    json.dump(players, f, ensure_ascii=False, indent=4)

print(f"\n✅ Final batch: {updated_count} URLs added!")
print("Now all 189 players should have URLs!")
