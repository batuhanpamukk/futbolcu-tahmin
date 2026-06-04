import json
import os
import requests
from bs4 import BeautifulSoup
import time

def download_player_photos(force_redownload=False):
    """
    Download player photos from Transfermarkt.
    
    Args:
        force_redownload: If True, re-download even if file exists
    """
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
    skipped = 0
    
    print(f"Checking {len(players)} players...")
    
    for i, player in enumerate(players):
        photo_path = player.get('fotoPath')
        if not photo_path:
            print(f"[{i+1}/{len(players)}] Skipping {player['isim']} - No photoPath defined")
            skipped += 1
            continue
            
        filename = os.path.basename(photo_path)
        local_path = os.path.join(players_dir, filename)
        
        # Check if we should skip
        if os.path.exists(local_path) and not force_redownload:
            # Check file size - if too small, it's likely a placeholder
            file_size = os.path.getsize(local_path)
            if file_size > 10000:  # 10KB threshold
                continue
            else:
                print(f"[{i+1}/{len(players)}] Re-downloading {player['isim']} (current file too small: {file_size} bytes)...")
        else:
            print(f"[{i+1}/{len(players)}] Downloading photo for: {player['isim']}...")
        
        url = player.get('url')
        if not url:
            print(f"  ❌ No URL for {player['isim']}")
            errors += 1
            continue
            
        try:
            # 1. Fetch profile page
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"  ❌ Failed to fetch profile: {response.status_code}")
                errors += 1
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 2. Find image URL - Try multiple methods
            img_url = None
            
            # Method 1: Look for the main profile image
            img_tag = soup.find('img', class_='data-header__profile-image')
            if img_tag and img_tag.get('src'):
                img_url = img_tag['src']
            
            # Method 2: Try to get the "big" version from the image modal
            if not img_url or 'header/default' in img_url or 'header/missing' in img_url:
                # Look for image in a different location
                img_container = soup.find('div', class_='data-header__profile-container')
                if img_container:
                    img_tag = img_container.find('img')
                    if img_tag and img_tag.get('src'):
                        img_url = img_tag['src']
            
            # Method 3: Replace 'header' with 'big' or 'medium' to get higher quality
            if img_url and '/header/' in img_url:
                # Try to get bigger version
                big_url = img_url.replace('/header/', '/big/')
                medium_url = img_url.replace('/header/', '/medium/')
                
                # Try big version first
                test_response = requests.head(big_url, headers=headers, timeout=5)
                if test_response.status_code == 200:
                    img_url = big_url
                else:
                    # Try medium version
                    test_response = requests.head(medium_url, headers=headers, timeout=5)
                    if test_response.status_code == 200:
                        img_url = medium_url
                        
            if not img_url or 'default' in img_url or 'missing' in img_url:
                print(f"  ⚠️  Could not find valid image for {player['isim']} (placeholder detected)")
                errors += 1
                continue
                
            # 3. Download image
            img_response = requests.get(img_url, headers=headers, timeout=10)
            if img_response.status_code == 200:
                # Check if downloaded content is actually an image (not HTML error page)
                content_type = img_response.headers.get('content-type', '')
                if 'image' not in content_type:
                    print(f"  ❌ Downloaded content is not an image: {content_type}")
                    errors += 1
                    continue
                    
                with open(local_path, 'wb') as f:
                    f.write(img_response.content)
                    
                file_size = len(img_response.content)
                print(f"  ✅ Saved to {local_path} ({file_size} bytes)")
                count += 1
                
                # Sleep briefly to be nice to the server
                time.sleep(0.5)
            else:
                print(f"  ❌ Failed to download image: {img_response.status_code}")
                errors += 1
                
        except Exception as e:
            print(f"  ❌ Error processing {player['isim']}: {str(e)}")
            errors += 1
            
    print(f"\n{'='*60}")
    print(f"✅ Completed!")
    print(f"   Downloaded: {count} photos")
    print(f"   Errors: {errors}")
    print(f"   Skipped: {skipped}")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Re-download small files (placeholders)
    download_player_photos(force_redownload=False)
