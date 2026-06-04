#!/usr/bin/env python3
"""
Transfermarkt URL'lerinden oyuncu bilgilerini kontrol eden script.
Her oyuncunun güncel kulüp ve piyasa değerini scrape eder.
"""
import json
import time
import re
import sys
import os
import urllib.request
import urllib.error

# Desteklenen ligler
SUPPORTED_LEAGUES = {"Türkiye Ligi", "İngiltere Ligi", "İspanya Ligi", "Almanya Ligi", "İtalya Ligi"}

# Transfermarkt wettbewerb (competition) codes -> Game leagues
WETTBEWERB_TO_LEAGUE = {
    "TR1": "Türkiye Ligi",   # Süper Lig
    "GB1": "İngiltere Ligi",  # Premier League  
    "ES1": "İspanya Ligi",    # La Liga
    "L1":  "Almanya Ligi",    # Bundesliga
    "IT1": "İtalya Ligi",     # Serie A
    # Unsupported leagues
    "FR1": "Fransa Ligi",
    "NL1": "Hollanda Ligi",
    "PO1": "Portekiz Ligi",
    "RU1": "Rusya Ligi",
    "SA1": "Suudi Arabistan Ligi",
    "MLS1": "MLS",
    "L2":  "Almanya 2. Lig",
    "GB2": "İngiltere 2. Lig",
    "IT2": "İtalya 2. Lig",
    "ES2": "İspanya 2. Lig",
    "FR2": "Fransa 2. Lig",
    "TR2": "Türkiye 2. Lig",
    "BE1": "Belçika Ligi",
    "A1":  "Avusturya Ligi",
    "C1":  "İsviçre Ligi",
    "SC1": "İskoçya Ligi",
    "GR1": "Yunanistan Ligi",
    "BRA1": "Brezilya Ligi",
    "JAP1": "Japonya Ligi",
    "MX1": "Meksika Ligi",
    "KR1": "Güney Kore Ligi",
    "DK1": "Danimarka Ligi",
    "SE1": "İsveç Ligi",
    "PL1": "Polonya Ligi",
    "HR1": "Hırvatistan Ligi",
    "RO1": "Romanya Ligi",
    "UA1": "Ukrayna Ligi",
    "SER1": "Sırbistan Ligi",
}


def fetch_page(url, max_retries=3):
    """Fetch page with retries and proper headers."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'identity',
    }
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = 15 * (attempt + 1)
                print(f"  Rate limited, waiting {wait_time}s...", flush=True)
                time.sleep(wait_time)
            elif e.code == 404:
                return None
            else:
                print(f"  HTTP Error {e.code}, retrying...", flush=True)
                time.sleep(5)
        except Exception as e:
            print(f"  Error: {e}, retrying...", flush=True)
            time.sleep(5)
    return None


def extract_player_info(html):
    """Extract current club, market value, and league from Transfermarkt player page."""
    if not html:
        return None, None, None
    
    current_club = None
    market_value = None
    detected_league = None
    
    # 1. EXTRACT CLUB (from data-header__club section)
    # Pattern: <a title="FULL CLUB NAME" href="...">Short Name</a>
    club_match = re.search(
        r'class="data-header__club"[^>]*>.*?<a\s+title="([^"]+)"',
        html, re.DOTALL
    )
    if club_match:
        current_club = club_match.group(1).strip()
    else:
        # Fallback: get text from <a> inside data-header__club
        club_match2 = re.search(
            r'class="data-header__club"[^>]*>.*?<a[^>]*>([^<]+)</a>',
            html, re.DOTALL
        )
        if club_match2:
            current_club = club_match2.group(1).strip()
    
    # Handle free agents / retired
    if current_club and current_club.lower() in ('serbest', 'retired', 'karriereende', '-', 'bilinmiyor', 'unknown', 'without club'):
        current_club = 'Serbest'
    
    # 2. EXTRACT MARKET VALUE
    # Pattern: class="data-header__market-value-wrapper">VALUE <span class="waehrung">mil./bin. €
    value_match = re.search(
        r'class="data-header__market-value-wrapper"[^>]*>\s*([\d.,]+)\s*<span[^>]*class="waehrung"[^>]*>\s*(mil\.|Mio\.|bin\.|Tsd\.)\s*€',
        html, re.DOTALL | re.IGNORECASE
    )
    if value_match:
        value_str = value_match.group(1).strip().replace(',', '.')
        unit = value_match.group(2).strip().lower()
        try:
            value = float(value_str)
            if unit in ('mil.', 'mio.'):
                market_value = f"{value:.2f} Milyon €"
            elif unit in ('bin.', 'tsd.'):
                market_value = f"{value:.0f} Bin €"
        except ValueError:
            pass
    
    # 3. DETECT LEAGUE from data-header__league-link
    # This is the most reliable method: the league link contains the wettbewerb code
    # Pattern: <a class="data-header__league-link" href="/premier-liga/startseite/wettbewerb/RU1">
    league_link_match = re.search(
        r'class="data-header__league-link"[^>]*href="[^"]*wettbewerb/([A-Z0-9]+)"',
        html, re.DOTALL | re.IGNORECASE
    )
    if league_link_match:
        wettbewerb_code = league_link_match.group(1).upper()
        detected_league = WETTBEWERB_TO_LEAGUE.get(wettbewerb_code, f"Unknown ({wettbewerb_code})")
    else:
        # Fallback: try to find league info from the club section
        league_section = re.search(
            r'class="data-header__league".*?href="([^"]*)".*?>([\w\s.]+)<',
            html, re.DOTALL
        )
        if league_section:
            league_url = league_section.group(1)
            league_name = league_section.group(2).strip()
            # Try to extract wettbewerb code from URL
            wb_match = re.search(r'wettbewerb/([A-Z0-9]+)', league_url, re.IGNORECASE)
            if wb_match:
                wettbewerb_code = wb_match.group(1).upper()
                detected_league = WETTBEWERB_TO_LEAGUE.get(wettbewerb_code, f"Unknown ({wettbewerb_code})")
    
    return current_club, market_value, detected_league


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'assets', 'data', 'futbolcular.json')
    results_path = os.path.join(base_dir, 'verification_results.json')
    
    # Load previous results for resume support
    processed_urls = {}
    if os.path.exists(results_path):
        try:
            with open(results_path, 'r', encoding='utf-8') as f:
                prev_results = json.load(f)
                for r in prev_results.get('results', []):
                    url = r.get('url', '')
                    if url:
                        processed_urls[url] = r
            print(f"Loaded {len(processed_urls)} previous results, resuming...", flush=True)
        except:
            pass
    
    with open(json_path, 'r', encoding='utf-8') as f:
        players = json.load(f)
    
    total = len(players)
    print(f"Total players: {total}", flush=True)
    
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else total
    end_idx = min(start_idx + batch_size, total)
    
    print(f"Processing players {start_idx} to {end_idx-1}", flush=True)
    
    results = []
    to_remove = []
    to_update = []
    
    for i in range(start_idx, end_idx):
        player = players[i]
        name = player.get('isim', 'Unknown')
        url = player.get('url', '')
        game_club = player.get('kulup', '')
        game_value = player.get('piyasaDegeri', '')
        game_league = player.get('lig', '')
        
        if not url:
            print(f"[{i}] {name}: NO URL - skipping", flush=True)
            results.append({
                'index': i, 'name': name, 'url': '', 'status': 'NO_URL',
                'game_club': game_club, 'game_league': game_league,
            })
            continue
        
        # Check cache
        if url in processed_urls:
            prev = processed_urls[url]
            prev['index'] = i
            results.append(prev)
            status = prev.get('status', '?')
            if status == 'REMOVE':
                to_remove.append(prev)
            elif status in ('UPDATE', 'CHECK'):
                to_update.append(prev)
            print(f"[{i}] {name}: cached -> {status}", flush=True)
            continue
        
        print(f"[{i}/{end_idx-1}] {name} ({game_club})...", end='', flush=True)
        
        html = fetch_page(url)
        if html is None:
            print(f" FETCH_ERROR", flush=True)
            results.append({
                'index': i, 'name': name, 'url': url, 'status': 'FETCH_ERROR',
                'game_club': game_club, 'game_league': game_league,
            })
            time.sleep(2)
            continue
        
        tm_club, tm_value, tm_league = extract_player_info(html)
        
        status = 'OK'
        changes = {}
        
        # Check free agent / retired
        if tm_club == 'Serbest':
            status = 'REMOVE'
            changes['reason'] = 'Player is free agent / retired'
        # Check if league is unsupported
        elif tm_league is not None and tm_league not in SUPPORTED_LEAGUES:
            status = 'REMOVE'
            changes['reason'] = f"Transferred to unsupported league: {tm_league}"
            changes['tm_club'] = tm_club
            changes['tm_league'] = tm_league
        else:
            # Check club change
            if tm_club and tm_club != game_club:
                if tm_league and tm_league in SUPPORTED_LEAGUES:
                    changes['club_changed'] = {'from': game_club, 'to': tm_club}
                    if tm_league != game_league:
                        changes['league_changed'] = {'from': game_league, 'to': tm_league}
                    status = 'UPDATE'
                elif tm_league is None:
                    changes['club_changed'] = {'from': game_club, 'to': tm_club}
                    changes['note'] = 'League could not be detected'
                    status = 'CHECK'
                else:
                    status = 'REMOVE'
                    changes['reason'] = f"Transferred to unsupported league: {tm_league}"
                    changes['tm_club'] = tm_club
            
            # Check value change
            if tm_value and tm_value != game_value:
                changes['value_changed'] = {'from': game_value, 'to': tm_value}
                if status == 'OK':
                    status = 'VALUE_CHANGED'
        
        result = {
            'index': i, 'name': name, 'url': url, 'status': status,
            'game_club': game_club, 'game_league': game_league,
            'tm_club': tm_club, 'tm_value': tm_value, 'tm_league': tm_league,
            'changes': changes,
        }
        
        results.append(result)
        if status == 'REMOVE':
            to_remove.append(result)
        elif status in ('UPDATE', 'CHECK'):
            to_update.append(result)
        
        print(f" {status} | Club: {tm_club} | Value: {tm_value} | League: {tm_league}", flush=True)
        
        # Rate limiting
        time.sleep(1.5)
        
        # Save progress every 30 players
        if (i - start_idx + 1) % 30 == 0:
            save_data = {
                'total_checked': len(results),
                'to_remove_count': len(to_remove),
                'to_update_count': len(to_update),
                'results': results,
            }
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"\n--- Progress: {len(results)} checked | {len(to_remove)} remove | {len(to_update)} update ---\n", flush=True)
    
    # Final save
    save_data = {
        'total_checked': len(results),
        'to_remove_count': len(to_remove),
        'to_update_count': len(to_update),
        'results': results,
        'removal_list': to_remove,
        'update_list': to_update,
    }
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}", flush=True)
    print(f"COMPLETED: {len(results)} checked", flush=True)
    print(f"  To REMOVE: {len(to_remove)}", flush=True)
    print(f"  To UPDATE/CHECK: {len(to_update)}", flush=True)
    
    if to_remove:
        print(f"\n--- PLAYERS TO REMOVE ---", flush=True)
        for r in to_remove:
            reason = r.get('changes', {}).get('reason', 'unknown')
            print(f"  [{r['index']}] {r['name']} ({r['game_club']}) -> {reason}", flush=True)
    
    if to_update:
        print(f"\n--- PLAYERS TO UPDATE/CHECK ---", flush=True)
        for r in to_update:
            print(f"  [{r['index']}] {r['name']}: {r.get('changes', {})}", flush=True)
    
    print(f"\nResults saved to: {results_path}", flush=True)


if __name__ == '__main__':
    main()
