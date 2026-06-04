import json
import os
import requests
from bs4 import BeautifulSoup
import time

def download_images():
    file_path = "assets/data/futbolcular.json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filter for Chelsea players in English League
            chelsea_players = [p for p in data if p.get('lig') == "İngiltere Ligi" and p.get('kulup') == "Chelsea"]
            print(f"Found {len(chelsea_players)} Chelsea players. Starting downloads...")

            for i, player in enumerate(chelsea_players):
                name = player['isim']
                url = player.get('url')
                target_path = player.get('fotoPath')

                if not url or not target_path:
                    print(f"Skipping {name}: Missing URL or photo path.")
                    continue

                if os.path.exists(target_path):
                    print(f"Skipping {name}: Image already exists.")
                    continue

                print(f"[{i+1}/{len(chelsea_players)}] Processing {name}...")
                
                try:
                    site_content = requests.get(url, headers=headers).content
                    soup = BeautifulSoup(site_content, 'html.parser')

                    # Transfermarkt profile image logic
                    img_tag = soup.find('img', class_='data-header__profile-image')
                    
                    if not img_tag:
                         img_tag = soup.find('img', {'title': name})
                    
                    if not img_tag:
                         img_tag = soup.find('img', class_='modal-image')

                    if img_tag:
                        img_url = img_tag.get('src') or img_tag.get('data-src')
                        if img_url:
                            img_data = requests.get(img_url, headers=headers).content
                            
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            with open(target_path, 'wb') as img_f:
                                img_f.write(img_data)
                            print(f"   -> Downloaded to {target_path}")
                        else:
                            print(f"   -> Image URL found but empty src.")
                    else:
                        print(f"   -> Could not find image tag on page.")

                except Exception as e:
                    print(f"   -> Error downloading {name}: {e}")
                
                time.sleep(1) 

        else:
            print("futbolcular.json not found!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_images()
