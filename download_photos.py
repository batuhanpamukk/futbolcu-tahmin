import json
import os
import requests
from bs4 import BeautifulSoup
import time

def download_missing_photos():
    json_path = 'assets/data/futbolcular.json'
    players_dir = 'assets/players'
    
    if not os.path.exists(players_dir):
        os.makedirs(players_dir)
        
    with open(json_path, 'r', encoding='utf-8') as f:
        players = json.load(f)
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    count = 0
    errors = 0
    
    print(f"Checking {len(players)} players...")
    
    for player in players:
        # Construct expected filename from photoPath or name
        # The json has "fotoPath": "assets/players/amine_harit.png"
        # We can extract the filename from there
        
        photo_path = player.get('fotoPath')
        if not photo_path:
            print(f"Skipping {player['isim']} - No photoPath defined")
            continue
            
        filename = os.path.basename(photo_path)
        local_path = os.path.join(players_dir, filename)
        
        if os.path.exists(local_path):
            continue
            
        print(f"Downloading photo for: {player['isim']}...")
        
        url = player.get('url')
        if not url:
            print(f"  No URL for {player['isim']}")
            errors += 1
            continue
            
        try:
            # 1. Fetch profile page
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"  Failed to fetch profile: {response.status_code}")
                errors += 1
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 2. Find image URL
            # Transfermarkt usually has the main profile image in a class like 'data-header__profile-image'
            img_tag = soup.find('img', class_='data-header__profile-image')
            
            if not img_tag:
                # Try fallback, sometimes it's different or just 'modal-image'
                img_tag = soup.find('img', {'title': player['isim']})
                
            if not img_tag or not img_tag.get('src'):
                print(f"  Could not find image tag for {player['isim']}")
                errors += 1
                continue
                
            img_url = img_tag['src']
            
            # 3. Download image
            img_response = requests.get(img_url, headers=headers)
            if img_response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"  Saved to {local_path}")
                count += 1
                # Sleep briefly to be nice to the server
                time.sleep(1)
            else:
                print(f"  Failed to download image content: {img_response.status_code}")
                errors += 1
                
        except Exception as e:
            print(f"  Error processing {player['isim']}: {str(e)}")
            errors += 1
            
    print(f"\nCompleted. Downloaded {count} new photos. Encountered {errors} errors.")

if __name__ == "__main__":
    download_missing_photos()
