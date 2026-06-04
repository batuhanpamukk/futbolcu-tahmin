import json

def fix_flags():
    path = 'assets/data/futbolcular.json'
    with open(path, 'r', encoding='utf-8') as f:
        players = json.load(f)
        
    updates = {
        "Amerika Birleşik Devletleri": "assets/flags/united_states_of_america.png",
        "Jamaika": "assets/flags/jamaica.png",
        "Gambia": "assets/flags/gambia.png", 
        "Kongo": "assets/flags/democratic_republic_of_the_congo.png",
        "Zambiya": "assets/flags/zambia.png",
        "Karadağ": "assets/flags/montenegro.png",
        "Angola": "assets/flags/angola.png",
        "Ekvator Ginesi": "assets/flags/equatorial_guinea.png"
    }
    
    count = 0
    for p in players:
        ulke = p.get('ulke')
        if ulke in updates and "international.png" in p.get('bayrakPath', ''):
            p['bayrakPath'] = updates[ulke]
            count += 1
            print(f"Fixed flag for {p['isim']} ({ulke})")
            
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=4)
        
    print(f"Fixed {count} flags.")

if __name__ == "__main__":
    fix_flags()
