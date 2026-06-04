import json
import os
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, 'assets', 'data', 'futbolcular.json')
results_path = os.path.join(base_dir, 'verification_results.json')
backup_path = os.path.join(base_dir, 'assets', 'data', 'futbolcular.json.bak')

# Known name variants that shouldn't trigger a club name update if the league is the same
NAME_VARIANTS = {
    ('Galatasaray', 'Galatasaray SK'),
    ('Beşiktaş', 'Beşiktaş JK'),
    ('Fenerbahçe', 'Fenerbahçe SK'),
    ('Lecce', 'US Lecce'),
    ('Cremonese', 'US Cremonese'),
    ('Sassuolo', 'US Sassuolo'),
    ('AFC Sunderland U21', 'Sunderland'),
    ('Leeds United U21', 'Leeds United'),
    ('Pisa', 'Pisa Sporting Club'),
    ('Brighton & Hove Albion', 'Brighton &amp; Hove Albion'),
    ('Brighton & Hove Albion', 'Brighton Hove Albion')
}

def is_variant(club1, club2):
    return (club1, club2) in NAME_VARIANTS or (club2, club1) in NAME_VARIANTS

def main():
    with open(json_path, 'r', encoding='utf-8') as f:
        players = json.load(f)
        
    with open(results_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    to_remove_data = {}
    for r in data.get('removal_list', []):
        to_remove_data[r['index']] = r
        
    to_remove_indices = sorted(list(to_remove_data.keys()), reverse=True)
        
    updates = {}
    for r in data.get('update_list', []):
        updates[r['index']] = r
        
    removed_count = 0
    updated_count = 0
    
    print("--- UPDATING PLAYERS ---")
    for idx, r in updates.items():
        player = players[idx]
        changes_applied = False
        
        # Check value change
        vc = r.get('changes', {}).get('value_changed')
        if vc and r['tm_value'] is not None:
            old_val = player.get('piyasaDegeri')
            player['piyasaDegeri'] = r['tm_value']
            print(f"[{idx}] {player['isim']}: Value updated {old_val} -> {player['piyasaDegeri']}")
            changes_applied = True
            
        # Check real club change
        cc = r.get('changes', {}).get('club_changed')
        if cc:
            from_club = cc['from']
            to_club = cc['to']
            if not is_variant(from_club, to_club):
                player['kulup'] = to_club
                print(f"[{idx}] {player['isim']}: Club updated {from_club} -> {to_club}")
                changes_applied = True
                
        # Check league change
        lc = r.get('changes', {}).get('league_changed')
        if lc:
            old_lig = player.get('lig', 'Unknown')
            player['lig'] = lc['to']
            print(f"[{idx}] {player['isim']}: League updated {old_lig} -> {lc['to']}")
            changes_applied = True
            
        if changes_applied:
            updated_count += 1
            
    print("\n--- REMOVING PLAYERS ---")
    for idx in to_remove_indices:
        player = players[idx]
        reason = to_remove_data[idx].get('changes', {}).get('reason', 'unsupported')
        print(f"Removed: {player['isim']} ({player['kulup']} / {player['lig']}) - Reason: {reason}")
        del players[idx]
        removed_count += 1
        
    # Make backup
    shutil.copy2(json_path, backup_path)
    print(f"\nBackup created at {backup_path}")
    
    # Write to file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=4)
        
    print(f"\nDone! Removed {removed_count} players, Updated {updated_count} players.")
    print(f"New total players: {len(players)}")

if __name__ == '__main__':
    main()
