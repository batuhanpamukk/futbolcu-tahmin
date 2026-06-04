import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def search_player(name):
    query = name.replace(' ', '+')
    url = f"https://www.transfermarkt.com.tr/schnellsuche/ergebnis/schnellsuche?query={query}"
    print(f"Searching: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # The search result might be a list or a direct redirect if only one match? 
        # Usually it's a list.
        # Select the first result in the table
        # Selector: .items .odd or .even -> td.hauptlink a
        
        # Try to find the table with results
        # The structure is usually a table with class 'items'
        
        # Check if we were redirected to a profile directly
        if "/profil/spieler/" in response.url:
            print(f"Direct Match: {response.url}")
            return response.url

        # Otherwise look for the first player result
        result_table = soup.select_one('.items')
        if result_table:
            # First row
            first_row = result_table.select_one('tbody tr')
            if first_row:
                link = first_row.select_one('td.hauptlink a')
                if link:
                    href = link.get('href')
                    full_url = "https://www.transfermarkt.com.tr" + href
                    print(f"Found: {full_url}")
                    return full_url
        
        print("No result found.")
        return None

    except Exception as e:
        print(f"Error: {e}")
        return None

search_player("İrfan Can Kahveci")
