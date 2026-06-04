import json
import os
import requests
from bs4 import BeautifulSoup
import time
import random

# Italian Teams to add
TEAMS = [
    {"name": "SSC Napoli", "url": "https://www.transfermarkt.com.tr/ssc-neapel/startseite/verein/6195/saison_id/2025"},
    {"name": "Atalanta", "url": "https://www.transfermarkt.com.tr/atalanta-bergamo/startseite/verein/800/saison_id/2025"},
    {"name": "AS Roma", "url": "https://www.transfermarkt.com.tr/as-rom/startseite/verein/12/saison_id/2025"},
    {"name": "Como 1907", "url": "https://www.transfermarkt.com.tr/como-1907/startseite/verein/1047/saison_id/2025"},
    {"name": "Bologna FC", "url": "https://www.transfermarkt.com.tr/fc-bologna/startseite/verein/1025/saison_id/2025"},
    {"name": "Fiorentina", "url": "https://www.transfermarkt.com.tr/ac-florenz/startseite/verein/430/saison_id/2025"},
    {"name": "Lazio", "url": "https://www.transfermarkt.com.tr/lazio-rom/startseite/verein/398/saison_id/2025"},
    {"name": "Sassuolo", "url": "https://www.transfermarkt.com.tr/us-sassuolo/startseite/verein/6574/saison_id/2025"},
    {"name": "Parma Calcio", "url": "https://www.transfermarkt.com.tr/parma-calcio-1913/startseite/verein/130/saison_id/2025"},
    {"name": "Udinese", "url": "https://www.transfermarkt.com.tr/udinese-calcio/startseite/verein/410/saison_id/2025"},
    {"name": "Genoa", "url": "https://www.transfermarkt.com.tr/genua-cfc/startseite/verein/252/saison_id/2025"},
    {"name": "Torino FC", "url": "https://www.transfermarkt.com.tr/fc-turin/startseite/verein/416/saison_id/2025"},
    {"name": "Cagliari", "url": "https://www.transfermarkt.com.tr/cagliari-calcio/startseite/verein/1390/saison_id/2025"},
    {"name": "Hellas Verona", "url": "https://www.transfermarkt.com.tr/hellas-verona/startseite/verein/276/saison_id/2025"},
    {"name": "Pisa", "url": "https://www.transfermarkt.com.tr/ac-pisa-1909/startseite/verein/4172/saison_id/2025"},
    {"name": "Lecce", "url": "https://www.transfermarkt.com.tr/us-lecce/startseite/verein/1005/saison_id/2025"},
    {"name": "Cremonese", "url": "https://www.transfermarkt.com.tr/us-cremonese/startseite/verein/2239/saison_id/2025"}
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Country to Flag File Mapping (Based on assets/flags contents)
# Add more mappings as encountered
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
    "ABD": "united_states_of_america.png",
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
    "Karadağ": "montenegro.png", # Check
    "İzlanda": "iceland.png",
    "Avustralya": "australia.png",
    "Yeni Zelanda": "new_zealand.png",
    "Gambiya": "gambia.png", 
    "Gine": "guinea.png",
    "Burkina Faso": "burkina_faso.png",
    "Kongo": "congo.png", # Check which congo
    "Demokratik Kongo": "democratic_republic_of_the_congo.png",
    "Angola": "angola.png",
    "Zambiya": "zambia.png", # Check
    "Slovakya": "slovakia.png",
    "Amerika Birleşik Devletleri": "united_states_of_america.png",
    "Jamaika": "jamaica.png",
    "Gambia": "gambia.png", 
    "Kongo": "democratic_republic_of_the_congo.png",
    "Karadağ": "montenegro.png",
    "Ekvator Ginesi": "equatorial_guinea.png"
}

def get_flag_path(country_name):
    # Try direct mapping
    if country_name in COUNTRY_MAPPING:
        return f"assets/flags/{COUNTRY_MAPPING[country_name]}"
    
    # Try normalizing/guessing
    # Check if a file exists with the country name lowercased + .png
    # But for now, let's just return a default or try to map roughly
    # We will log missing mappings
    
    # Fallback for now:
    print(f"  ⚠️  No flag mapping for: {country_name}")
    return "assets/flags/international.png" # Fallback

def normalize_market_value(value_str):
    if not value_str or "-" in value_str:
        return None
    
    # Example: "15.00 mil. €" or "500 bin €"
    value_str = value_str.replace("€", "").strip()
    
    try:
        if "mil." in value_str:
            val = float(value_str.replace("mil.", "").strip().replace(",", "."))
            return f"{val:.2f} Milyon €"
        elif "bin" in value_str:
            val = float(value_str.replace("bin", "").strip().replace(",", "."))
            # Convert thousands to millions: 500 bin -> 0.50 Milyon
            val_in_mil = val / 1000
            return f"{val_in_mil:.2f} Milyon €"
        else:
            return f"{value_str} €"
    except:
        return value_str 

def download_image(url, save_path):
    if os.path.exists(save_path):
        # Optional: Skip if exists
        return True
        
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading image: {e}")
    return False

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
            if not name_cell:
                continue
                
            name_link = name_cell.find('div').find('span').find('a') if name_cell.find('div') else name_cell.find('a')
            if not name_link:
                # Try finding 'hide-for-small' which sometimes contains the name
                name_link = row.find('td', class_='posrela').find('a', class_='hauptlink') if row.find('td', class_='posrela') else None
            
            # Alternative selector structure check
            if not name_link:
                 # Check the specific structure for Transfermarkt player lists
                 # Usually inside a table cell with class 'posrela' -> table with class 'inline-table' -> td class 'hauptlink'
                 inline_table = row.find('table', class_='inline-table')
                 if inline_table:
                     name_link = inline_table.find('td', class_='hauptlink').find('a')

            if not name_link:
                continue

            full_name = name_link.get_text(strip=True)
            # Handle cases where full name might be split (sometimes they put first initial)
            # But get_text usually gets it right.
            
            profile_url = "https://www.transfermarkt.com.tr" + name_link['href']
            
            # Position
            # Usually in the row, check standard structure
            # It's usually in the inline table after the name
            # Position scraping logic update
            position = "Bilinmiyor"
            if inline_table:
                # Standard structure
                pos_cell = inline_table.find_all('tr')[-1].find('td')
                if pos_cell:
                    position = pos_cell.get_text(strip=True)
            
            # Fallback: Check if position is empty or "Bilinmiyor", try alternative
            if position == "Bilinmiyor" or not position:
                 # Sometimes it's in the second row of the inline table
                 rows_inline = inline_table.find_all('tr') if inline_table else []
                 if len(rows_inline) > 1:
                     position = rows_inline[1].get_text(strip=True)
                 else:
                     # Try finding ANY text in the inline table that looks like a position
                     # Or check the main row's other cells
                     pass
                
            # Country
            # Found in a td with class 'zentriert', look for img flag
            # There might be multiple 'zentriert' cells (age, nat, etc.)
            # Nat is usually the one with img having class 'flaggenrahmen'
            nat_cell = row.find_all('td', class_='zentriert')
            country = "Bilinmiyor"
            for cell in nat_cell:
                flag_img = cell.find('img', class_='flaggenrahmen')
                if flag_img:
                    country = flag_img['title']
                    break
            
            # Market Value
            # Usually the last cell with class 'rechts hauptlink'
            value_cell = row.find('td', class_='rechts hauptlink')
            raw_value = value_cell.get_text(strip=True) if value_cell else "-"
            market_value = normalize_market_value(raw_value)
            
            if not market_value:
                # Skip players with no market value (often youth or very low value)
                continue

            # Image URL extraction (Attempt to get it from the list view first)
            # The list view usually has a small image. 
            # We can construct the path or try to get it.
            # But better to just store the data and let the download script handle the high-res fetch
            # or fetch it now.
            # Let's use the default "download_photos" logic which fetches from profile.
            
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
                "lig": "İtalya Ligi"
            }
            
            players_data.append(player_entry)
            print(f"  Found: {full_name} ({market_value}) - {position}")
            
        print(f"  Extracted {len(players_data)} players.")
        return players_data
        
    except Exception as e:
        print(f"Error scraping {team_name}: {e}")
        return []

def main():
    # Load existing players
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
                # Update fields that might have been "Bilinmiyor" or missing
                existing_player['pozisyon'] = p['pozisyon']
                existing_player['piyasaDegeri'] = p['piyasaDegeri']
                existing_player['fotoPath'] = p['fotoPath'] # Ensure photo path is consistent
                # Keep other fields like 'lig' if already set? or overwrite?
                # Overwrite 'lig' to be safe
                existing_player['lig'] = p['lig']
                existing_player['kulup'] = p['kulup']
                existing_player['ulke'] = p['ulke']
                existing_player['bayrakPath'] = p['bayrakPath']
                
                updated_players_count += 1
            else:
                # Add new player
                all_players.append(p)
                players_by_url[url] = p # Add to dict for future checks
                new_players_count += 1
                
        # Sleep to be polite
        time.sleep(1)

    print(f"\nAdding {new_players_count} new players.")
    print(f"Updated {updated_players_count} existing players.")
    
    # Save back to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_players, f, ensure_ascii=False, indent=4)
        
    print("JSON updated successfully.")
    
    # Now run the photo downloader
    # We can invoke the other script or just tell the user to run it.
    # For better integration, let's run it via subprocess or just print a message
    # actually, I'll just print a message since I have that script available.
    print("\nIMPORTANT: Run 'python3 download_photos_v2.py' to download the images for the new players.")

if __name__ == "__main__":
    main()
