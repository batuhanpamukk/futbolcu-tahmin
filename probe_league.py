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

    # Try to find league info
    # Usually near the club info
    
    # Selector for the league line
    league_box = soup.select_one('.data-header__league')
    if league_box:
        print(f"League (Selector 1): {league_box.text.strip()}")
        
    league_link = soup.select_one('.data-header__league a')
    if league_link:
         print(f"League Link Text: {league_link.text.strip()}")

    # Check the header content generally
    header_content = soup.select_one('.data-header__info-box')
    if header_content:
        print("\n--- Header Info Box Text ---")
        # print(header_content.text.strip()) 
        # Analyzing links inside might be better
        for link in header_content.select('a'):
            print(f"Link: {link.text.strip()} -> {link.get('href')}")


except Exception as e:
    print(f"Error: {e}")
