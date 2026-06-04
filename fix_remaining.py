import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin

# List of players with small files
small_file_players = [
    "onur_bulut.png",
    "emre_bilgin.png",
    "onur_ergun.png",
    "engin_can_biterge.png",
    "luca_stancic.png", 
    "volkan_babacan.png",
    "abdou_aziz_fall.png",
    "gokdeniz_gurpuz.png",
    "abdülkerim_bardakcı.png",
    "devrim_sahin.png",
    "omer_ali_sahiner.png",
    "tarik_cetin.png"
]

# Load player data
with open('assets/data/futbolcular.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

# Create a mapping
player_name_to_file = {}
for player in players:
    filename = player['fotoPath'].replace('assets/players/', '')
    player_name_to_file[filename] = player

print("Attempting to download higher quality versions...\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

downloaded = 0
errors = 0

for filename in small_file_players:
    if filename not in player_name_to_file:
        print(f"❌ {filename} not found in JSON")
        errors += 1
        continue
    
    player = player_name_to_file[filename]
    player_name = player.get('isim', 'Unknown')
    url = player.get('url')
    
    if not url:
        print(f"❌ No URL for {player_name}")
        errors += 1
        continue
    
    print(f"[{downloaded + errors + 1}/12] Trying {player_name}...")
    
    try:
        # Fetch the profile page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find the profile image - look for larger versions
        img_tag = soup.find('img', {'class': 'data-header__profile-image'})
        
        if not img_tag or not img_tag.get('src'):
            print(f"  ⚠️  No image found on page")
            errors += 1
            continue
        
        img_url = img_tag['src']
        
        # Try to get the original/max size by removing size parameters
        # Transfermarkt URLs often have patterns like /medium/ or /header/
        # Try replacing with /portrait_big/ or /max/
        original_url = img_url
        
        # Try different size options
        size_options = [
            img_url.replace('/header/', '/portrait_big/'),
            img_url.replace('/medium/', '/portrait_big/'),
            img_url.replace('/header/', '/max/'),
            img_url.replace('/medium/', '/max/'),
            original_url
        ]
        
        best_image = None
        best_size = 0
        
        for test_url in size_options:
            try:
                img_response = requests.get(test_url, headers=headers, timeout=10)
                if img_response.status_code == 200:
                    content_type = img_response.headers.get('Content-Type', '')
                    if 'image' in content_type and len(img_response.content) > best_size:
                        best_image = img_response.content
                        best_size = len(img_response.content)
            except:
                continue
        
        if best_image and best_size > 10000:  # Only save if >10KB
            filepath = f"assets/players/{filename}"
            with open(filepath, 'wb') as f:
                f.write(best_image)
            print(f"  ✅ Saved better quality ({best_size} bytes)")
            downloaded += 1
        else:
            print(f"  ⚠️  Could not find better quality (best: {best_size} bytes)")
            errors += 1
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        errors += 1

print(f"\n{'='*60}")
print(f"✅ Downloaded: {downloaded} improved photos")
print(f"❌ Could not improve: {errors}")
print(f"{'='*60}")
