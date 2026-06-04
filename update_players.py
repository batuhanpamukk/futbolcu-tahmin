import json
import requests
from bs4 import BeautifulSoup
import time
import random
import sys

JSON_PATH = 'assets/data/futbolcular.json'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

# Mapping Transfermarkt League Names to JSON League Names
LEAGUE_MAPPING = {
    "süper lig": "Türkiye Ligi",
    "bundesliga": "Almanya Ligi",
    "premier league": "İngiltere Ligi",
    "serie a": "İtalya Ligi",
    "laliga": "İspanya Ligi",
}

# Valid leagues in our JSON
VALID_LEAGUES = [
    "Almanya Ligi",
    "İngiltere Ligi",
    "İspanya Ligi",
    "İtalya Ligi",
    "Türkiye Ligi"
]

def clean_market_value(mv_text):
    """
    Parses Transfermarkt market value text (e.g., '6.00 mil. €', '500 bin €')
    and returns format 'X.XX Milyon €'.
    """
    if not mv_text: return None
    mv_text = mv_text.lower().replace('son güncelleme:', '').strip()
    if "son" in mv_text:
        mv_text = mv_text.split("son")[0].strip()
    
    if 'mil. €' in mv_text:
        value_str = mv_text.replace('mil. €', '').strip()
        try:
            value = float(value_str.replace(',', '.'))
            return f"{value:.2f} Milyon €"
        except ValueError:
            return None
    
    if 'bin €' in mv_text:
        value_str = mv_text.replace('bin €', '').strip()
        try:
            value = float(value_str.replace(',', '.'))
            value_mil = value / 1000
            return f"{value_mil:.2f} Milyon €"
        except ValueError:
            return None

    return None

def normalize_club(name):
    if not name: return ""
    name = name.lower()
    for suffix in [' sk', ' fk', ' fc', ' as', ' 1.', 'calcio', 'sp', 'jk']:
        name = name.replace(suffix, '')
    return name.strip()

def main():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            players = json.load(f)
    except FileNotFoundError:
        print(f"Error: {JSON_PATH} not found.")
        sys.exit(1)

    updated_count = 0
    deleted_players = []
    
    # We will build a NEW list of players, excluding deleted ones
    remaining_players = []
    
    total_players = len(players)
    print(f"Starting update for {total_players} players...")
    
    MAX_PLAYERS = 200000 
    processed_count = 0

    session = requests.Session()
    session.headers.update(HEADERS)

    for i, player in enumerate(players):
        if processed_count >= MAX_PLAYERS:
            remaining_players.append(player) 
            continue
            
        url = player.get('url')
        if not url:
            remaining_players.append(player)
            continue
            
        name = player.get('isim')
        current_mv = player.get('piyasaDegeri')
        current_club = player.get('kulup')
        current_league = player.get('lig')

        print(f"[{i+1}/{total_players}] Checking {name}...", end='', flush=True)

        try:
            response = session.get(url, timeout=10)
            if response.status_code != 200:
                print(f" Failed (Status {response.status_code})")
                remaining_players.append(player)
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Check League & Club FIRST (Deletion Logic)
            tm_league_name = ""
            league_box = soup.select_one('.data-header__league a')
            if not league_box:
                 league_box = soup.select_one('.data-header__league')
            
            if league_box:
                tm_league_name = league_box.text.strip().replace('\n', '').strip()
            
            mapped_league = None
            if tm_league_name:
                tm_league_lower = tm_league_name.lower()
                if tm_league_name in VALID_LEAGUES:
                    mapped_league = tm_league_name
                else:
                    for k, v in LEAGUE_MAPPING.items():
                        if k in tm_league_lower:
                            mapped_league = v
                            break
            
            # Logic: If mapped_league is None, check if it's a known 'other' league or just valid
            # Actually, if we can't map it, it means they are in a league we don't track.
            
            if mapped_league:
                # Player is in a valid league.
                link_updated = False
                
                if mapped_league != current_league:
                    print(f" League: {current_league} -> {mapped_league}", end='')
                    player['lig'] = mapped_league
                    link_updated = True

                # UPDATE MARKET VALUE
                mv_box = soup.select_one('.data-header__market-value-wrapper')
                if mv_box:
                    new_mv_raw = mv_box.text.strip()
                    new_mv_fmt = clean_market_value(new_mv_raw)
                    if new_mv_fmt and new_mv_fmt != current_mv:
                        print(f" Value: {current_mv} -> {new_mv_fmt}", end='')
                        player['piyasaDegeri'] = new_mv_fmt
                        updated_count += 1
                        link_updated = True

                # UPDATE CLUB (Now applying changes!)
                club_link = soup.select_one('.data-header__club a')
                if club_link:
                    new_club = club_link.get('title')
                    if new_club:
                         if normalize_club(new_club) != normalize_club(current_club):
                            print(f" Club: {current_club} -> {new_club}", end='')
                            player['kulup'] = new_club
                            updated_count += 1
                            link_updated = True
                
                if not link_updated:
                    print(" OK", end='')

                print("")
                remaining_players.append(player)

            else:
                # Player is in a league NOT in our valid list
                # Mark for deletion
                print(f" DELETE: Moved to {tm_league_name}")
                deleted_players.append(f"{name} (Moved to {tm_league_name})")

            processed_count += 1
            time.sleep(random.uniform(0.5, 1.0)) # Slightly faster

        except Exception as e:
            print(f" Error: {e}")
            remaining_players.append(player)

    # Save updates
    if processed_count > 0:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(remaining_players, f, ensure_ascii=False, indent=4)
        print(f"\nSaved updates to {JSON_PATH}")
        print(f"Total processed: {processed_count}")
        print(f"Total deleted: {len(deleted_players)}")
        print(f"Total updates: {updated_count}")

    if deleted_players:
        print("\n--- DELETED PLAYERS ---")
        for p in deleted_players:
            print(f"- {p}")

if __name__ == "__main__":
    main()
