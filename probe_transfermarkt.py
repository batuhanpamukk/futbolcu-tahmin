import requests
from bs4 import BeautifulSoup

url = "https://www.transfermarkt.com.tr/amine-harit/profil/spieler/372711"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # Try to find market value
    # Common selectors based on experience, will print what we find
    mv_box = soup.select_one('.tm-player-market-value-development__current-value')
    if mv_box:
        print(f"Market Value (Selector 1): {mv_box.text.strip()}")
    
    mv_box_2 = soup.select_one('.data-header__market-value-wrapper')
    if mv_box_2:
        print(f"Market Value (Selector 2): {mv_box_2.text.strip()}")

    # Try to find club
    club_box = soup.select_one('.data-header__club-info')
    if club_box:
         print(f"Club (Selector 1): {club_box.text.strip()}")

    club_link = soup.select_one('.data-header__club a')
    if club_link:
        print(f"Club (Selector 2): {club_link.get('title')}")

except Exception as e:
    print(f"Error: {e}")
