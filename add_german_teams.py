import json
import os
import requests
from bs4 import BeautifulSoup
import time
import random

# German Teams to add
TEAMS = [
    {"name": "FC Bayern Münih", "url": "https://www.transfermarkt.com.tr/fc-bayern-munchen/startseite/verein/27/saison_id/2025"},
    {"name": "Borussia Dortmund", "url": "https://www.transfermarkt.com.tr/borussia-dortmund/startseite/verein/16/saison_id/2025"},
    {"name": "Bayer 04 Leverkusen", "url": "https://www.transfermarkt.com.tr/bayer-04-leverkusen/startseite/verein/15/saison_id/2025"},
    {"name": "RB Leipzig", "url": "https://www.transfermarkt.com.tr/rasenballsport-leipzig/startseite/verein/23826/saison_id/2025"},
    {"name": "Eintracht Frankfurt", "url": "https://www.transfermarkt.com.tr/eintracht-frankfurt/startseite/verein/24/saison_id/2025"},
    {"name": "VfB Stuttgart", "url": "https://www.transfermarkt.com.tr/vfb-stuttgart/startseite/verein/79/saison_id/2025"},
    {"name": "VfL Wolfsburg", "url": "https://www.transfermarkt.com.tr/vfl-wolfsburg/startseite/verein/82/saison_id/2025"},
    {"name": "TSG 1899 Hoffenheim", "url": "https://www.transfermarkt.com.tr/tsg-1899-hoffenheim/startseite/verein/533/saison_id/2025"},
    {"name": "SV Werder Bremen", "url": "https://www.transfermarkt.com.tr/sv-werder-bremen/startseite/verein/86/saison_id/2025"},
    {"name": "SC Freiburg", "url": "https://www.transfermarkt.com.tr/sc-freiburg/startseite/verein/60/saison_id/2025"},
    {"name": "FC Augsburg", "url": "https://www.transfermarkt.com.tr/fc-augsburg/startseite/verein/167/saison_id/2025"},
    {"name": "Borussia Mönchengladbach", "url": "https://www.transfermarkt.com.tr/borussia-monchengladbach/startseite/verein/18/saison_id/2025"},
    {"name": "1.FSV Mainz 05", "url": "https://www.transfermarkt.com.tr/1-fsv-mainz-05/startseite/verein/39/saison_id/2025"},
    {"name": "1.FC Köln", "url": "https://www.transfermarkt.com.tr/1-fc-koln/startseite/verein/3/saison_id/2025"},
    {"name": "Hamburger SV", "url": "https://www.transfermarkt.com.tr/hamburger-sv/startseite/verein/41/saison_id/2025"},
    {"name": "1.FC Union Berlin", "url": "https://www.transfermarkt.com.tr/1-fc-union-berlin/startseite/verein/89/saison_id/2025"},
    {"name": "FC St. Pauli", "url": "https://www.transfermarkt.com.tr/fc-st-pauli/startseite/verein/35/saison_id/2025"},
    {"name": "1.FC Heidenheim 1846", "url": "https://www.transfermarkt.com.tr/1-fc-heidenheim-1846/startseite/verein/2036/saison_id/2025"}
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Extensive Country Mapping
COUNTRY_MAPPING = {
    "Türkiye": "turkey.png",
    "Almanya": "germany.png",
    "Fransa": "france.png",
    "İngiltere": "england.png",
    "İspanya": "spain.png",
    "İtalya": "italy.png",
    "Portekiz": "portugal.png",
    "Hollanda": "netherlands.png",
    "Belçika": "belgium.png",
    "Brezilya": "brazil.png",
    "Arjantin": "argentina.png",
    "Uruguay": "uruguay.png",
    "Kolombiya": "colombia.png",
    "Nijerya": "nigeria.png",
    "Gana": "ghana.png",
    "Fildişi Sahili": "ivory_coast.png",
    "Senegal": "senegal.png",
    "Fas": "morocco.png",
    "Cezayir": "algeria.png",
    "Mısır": "egypt.png",
    "Amerika Birleşik Devletleri": "united_states_of_america.png",
    "Kanada": "canada.png",
    "Japonya": "japan.png",
    "Güney Kore": "south_korea.png",
    "Hırvatistan": "croatia.png",
    "Sırbistan": "serbia.png",
    "Polonya": "poland.png",
    "Ukrayna": "ukraine.png",
    "Rusya": "russia.png",
    "İsviçre": "switzerland.png",
    "Avusturya": "austria.png",
    "Danimarka": "denmark.png",
    "İsveç": "sweden.png",
    "Norveç": "norway.png",
    "Finlandiya": "finland.png",
    "Çek Cumhuriyeti": "czech_republic.png",
    "Slovakya": "slovakia.png",
    "Macaristan": "hungary.png",
    "Yunanistan": "greece.png",
    "Romanya": "romania.png",
    "Bulgaristan": "bulgaria.png",
    "Bosna-Hersek": "bosnia_and_herzegovina.png",
    "Arnavutluk": "albania.png",
    "Kosova": "kosovo.png", # Might check if exists
    "Kuzey Makedonya": "north_macedonia.png",
    "İrlanda": "ireland.png",
    "İskoçya": "scotland.png",
    "Galler": "wales.png",
    "Kameron": "cameroon.png",
    "Mali": "mali.png",
    "Gürcistan": "georgia.png",
    "İran": "iran.png",
    "Ekvador": "ecuador.png",
    "Paraguay": "paraguay.png",
    "Şili": "chile.png",
    "Venezuela": "venezuela.png",
    "Meksika": "mexico.png",
    "Tunus": "tunisia.png",
    "Kamerun": "cameroon.png",
    "Slovenya": "slovenia.png",
    "Karadağ": "montenegro.png",
    "İzlanda": "iceland.png",
    "Avustralya": "australia.png",
    "Yeni Zelanda": "new_zealand.png",
    "Gambiya": "gambia.png", 
    "Gine": "guinea.png",
    "Burkina Faso": "burkina_faso.png",
    "Kongo": "democratic_republic_of_the_congo.png",
    "Demokratik Kongo": "democratic_republic_of_the_congo.png",
    "Angola": "angola.png",
    "Zambiya": "zambia.png",
    "Jamaika": "jamaica.png",
    "Gambia": "gambia.png", 
    "Ekvator Ginesi": "equatorial_guinea.png"
}

def get_flag_path(country_name):
    if country_name in COUNTRY_MAPPING:
        return f"assets/flags/{COUNTRY_MAPPING[country_name]}"
    
    # Fallback
    print(f"  ⚠️  No flag mapping for: {country_name}")
    return "assets/flags/international.png"

def normalize_market_value(value_str):
    if not value_str or "-" in value_str:
        return None
    
    value_str = value_str.replace("€", "").strip()
    
    try:
        if "mil." in value_str:
            val = float(value_str.replace("mil.", "").strip().replace(",", "."))
            return f"{val:.2f} Milyon €"
        elif "bin" in value_str:
            val = float(value_str.replace("bin", "").strip().replace(",", "."))
            val_in_mil = val / 1000
            return f"{val_in_mil:.2f} Milyon €"
        else:
            return f"{value_str} €"
    except:
        return value_str 

def scrape_team(team_entry):
    team_name = team_entry["name"]
    team_url = team_entry["url"]
    print(f"\nProcessing {team_name}...")
    
    try:
        response = requests.get(team_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Failed to load page for {team_name}")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Determine the table - usually "items"
        table = soup.find('table', class_='items')
        if not table:
            print("Could not find player table.")
            return []
            
        players_data = []
        rows = table.find_all('tr', class_=['odd', 'even'])
        
        for row in rows:
            inline_table = row.find('table', class_='inline-table')
            
            # Name and URL
            name_cell = row.find('td', class_='hauptlink')
            
            # Additional check for name link inside inline table if main missing
            if not name_cell and inline_table:
                 name_cell = inline_table.find('td', class_='hauptlink')
            
            if not name_cell:
                continue
                
            name_link = name_cell.find('div').find('span').find('a') if name_cell.find('div') else name_cell.find('a')
            if not name_link and inline_table:
                 name_link = inline_table.find('td', class_='hauptlink').find('a')

            if not name_link:
                # Try finding 'hide-for-small' which sometimes contains the name
                name_link = row.find('td', class_='posrela').find('a', class_='hauptlink') if row.find('td', class_='posrela') else None

            if not name_link:
                continue

            full_name = name_link.get_text(strip=True)
            profile_url = "https://www.transfermarkt.com.tr" + name_link['href']
            
            # Position
            position = "Bilinmiyor"
            if inline_table:
                # Standard structure
                pos_cell = inline_table.find_all('tr')[-1].find('td')
                if pos_cell:
                    position = pos_cell.get_text(strip=True)
            
            # Fallback: Check if position is empty or "Bilinmiyor", try alternative
            if position == "Bilinmiyor" or not position:
                 rows_inline = inline_table.find_all('tr') if inline_table else []
                 if len(rows_inline) > 1:
                     position = rows_inline[1].get_text(strip=True)
                 
                
            # Country
            nat_cell = row.find_all('td', class_='zentriert')
            country = "Bilinmiyor"
            for cell in nat_cell:
                flag_img = cell.find('img', class_='flaggenrahmen')
                if flag_img:
                    country = flag_img['title']
                    break
            
            # Market Value
            value_cell = row.find('td', class_='rechts hauptlink')
            raw_value = value_cell.get_text(strip=True) if value_cell else "-"
            market_value = normalize_market_value(raw_value)
            
            if not market_value:
                continue

            # Create standardized filename for photo
            safe_name = full_name.lower().replace(' ', '_').replace('ç', 'c').replace('ş', 's').replace('ğ', 'g').replace('ü', 'u').replace('ö', 'o').replace('ı', 'i').replace('.', '').replace("'", "")
            photo_path = f"assets/players/{safe_name}.png"
            
            # Flag Path
            flag_path = get_flag_path(country)
            
            player_entry = {
                "isim": full_name,
                "url": profile_url,
                "ulke": country,
                "kulup": team_name,
                "bayrakPath": flag_path,
                "pozisyon": position,
                "piyasaDegeri": market_value,
                "fotoPath": photo_path,
                "lig": "Almanya Ligi"
            }
            
            players_data.append(player_entry)
            print(f"  Found: {full_name} ({market_value}) - {position}")
            
        print(f"  Extracted {len(players_data)} players.")
        return players_data
        
    except Exception as e:
        print(f"Error scraping {team_name}: {e}")
        return []

def main():
    json_path = 'assets/data/futbolcular.json'
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            all_players = json.load(f)
    else:
        all_players = []
        
    print(f"Loaded {len(all_players)} existing players.")
    
    # Create a dictionary for faster lookup by URL
    players_by_url = {p.get('url'): p for p in all_players}
    
    new_players_count = 0
    updated_players_count = 0
    
    for team in TEAMS:
        team_players = scrape_team(team)
        
        for p in team_players:
            url = p.get('url')
            if url in players_by_url:
                # Update existing player
                existing_player = players_by_url[url]
                existing_player['pozisyon'] = p['pozisyon']
                existing_player['piyasaDegeri'] = p['piyasaDegeri']
                existing_player['fotoPath'] = p['fotoPath']
                existing_player['lig'] = p['lig'] # Update league to 'Almanya Ligi' if player moved? Or prioritize? 
                # If player moved from Italy to Germany, this updates correctly.
                existing_player['kulup'] = p['kulup']
                existing_player['ulke'] = p['ulke']
                existing_player['bayrakPath'] = p['bayrakPath']
                
                updated_players_count += 1
            else:
                # Add new player
                all_players.append(p)
                players_by_url[url] = p
                new_players_count += 1
                
        time.sleep(1)

    print(f"\nAdding {new_players_count} new players.")
    print(f"Updated {updated_players_count} existing players.")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_players, f, ensure_ascii=False, indent=4)
        
    print("JSON updated successfully.")
    print("\nIMPORTANT: Run 'python3 download_german_photos.py' afterwards.")

if __name__ == "__main__":
    main()
