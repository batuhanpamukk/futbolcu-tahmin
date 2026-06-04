import json
import os
import requests
import time

def download_german_photos():
    json_path = 'assets/data/futbolcular.json'
    players_dir = 'assets/players'
    
    if not os.path.exists(players_dir):
        os.makedirs(players_dir)
        
    with open(json_path, 'r', encoding='utf-8') as f:
        players = json.load(f)
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Filter for German League players
    german_players = [p for p in players if p.get('lig') == 'Almanya Ligi']
    
    print(f"Found {len(german_players)} German League players.")
    
    count = 0
    errors = 0
    
    for i, player in enumerate(german_players):
        photo_path = player.get('fotoPath')
        if not photo_path:
            continue
            
        filename = os.path.basename(photo_path)
        local_path = os.path.join(players_dir, filename)
        
        # Check if exists and size > 10KB
        if os.path.exists(local_path):
            if os.path.getsize(local_path) > 10000:
                # Already good
                continue
                
        print(f"[{i+1}/{len(german_players)}] Downloading {player['isim']}...")
        
        url = player.get('url')
        if not url:
            print(f"  ❌ No URL for {player['isim']}")
            errors += 1
            continue
            
        try:
             # 1. Fetch profile page to get image URL
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"  ❌ Failed to fetch profile")
                errors += 1
                continue
                
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            img_url = None
            img_tag = soup.find('img', class_='data-header__profile-image')
            if img_tag and img_tag.get('src'):
                img_url = img_tag['src']
                
            if not img_url:
                img_container = soup.find('div', class_='data-header__profile-container')
                if img_container:
                    img_tag = img_container.find('img')
                    if img_tag and img_tag.get('src'):
                        img_url = img_tag['src']
            
            # Try to get high quality
            if img_url and '/header/' in img_url:
                 big_url = img_url.replace('/header/', '/big/')
                 img_url = big_url
                 
            if not img_url:
                print(f"  ❌ No image found")
                errors += 1
                continue
                
            # Download
            img_response = requests.get(img_url, headers=headers, timeout=10)
            if img_response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"  ✅ Saved {local_path}")
                count += 1
            else:
                # Fallback to medium if big failed?
                if '/big/' in img_url:
                    medium_url = img_url.replace('/big/', '/medium/')
                    img_response = requests.get(medium_url, headers=headers, timeout=10)
                    if img_response.status_code == 200:
                         with open(local_path, 'wb') as f:
                            f.write(img_response.content)
                         print(f"  ✅ Saved {local_path} (medium)")
                         count += 1
                    else:
                        print("  ❌ Failed download")
                        errors += 1
                else:
                    print(f"  ❌ Failed download")
                    errors += 1

            time.sleep(0.2)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors += 1
            
    print(f"Done. Downloaded {count} images.")

if __name__ == "__main__":
    download_german_photos()
