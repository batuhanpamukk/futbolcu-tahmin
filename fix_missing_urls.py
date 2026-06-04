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

def search_player(name):
    query = name.replace(' ', '+')
    url = f"https://www.transfermarkt.com.tr/schnellsuche/ergebnis/schnellsuche?query={query}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        # Check if redirected directly
        if "/profil/spieler/" in response.url:
            return response.url

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for result table
        result_table = soup.select_one('.items')
        if result_table:
            first_row = result_table.select_one('tbody tr')
            if first_row:
                link = first_row.select_one('td.hauptlink a')
                if link:
                    href = link.get('href')
                    full_url = "https://www.transfermarkt.com.tr" + href
                    return full_url
        
        return None

    except Exception as e:
        print(f"Error searching for {name}: {e}")
        return None

def main():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            players = json.load(f)
    except FileNotFoundError:
        print(f"Error: {JSON_PATH} not found.")
        sys.exit(1)

    updated_count = 0
    missing_count = 0
    total = len(players)
    
    # Identify missing URLs
    players_missing_url = [p for p in players if not p.get('url')]
    missing_count = len(players_missing_url)
    
    print(f"Found {missing_count} players without URLs out of {total} total.")
    
    if missing_count == 0:
        print("No missing URLs to fix.")
        return

    for i, player in enumerate(players):
        if not player.get('url'):
            name = player.get('isim')
            print(f"[{updated_count+1}/{missing_count}] Searching for: {name}...", end='', flush=True)
            
            url = search_player(name)
            
            if url:
                print(f" Found: {url}")
                player['url'] = url
                updated_count += 1
            else:
                print(" Not found.")
            
            # Sleep to avoid rate limits
            time.sleep(random.uniform(1.0, 2.0))

    if updated_count > 0:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(players, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully updated {updated_count} URLs.")
    else:
        print("\nNo URLs updated.")

if __name__ == "__main__":
    main()
