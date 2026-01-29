import requests
import urllib.parse

def search(query):
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": query, "rows": 3})
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        items = data['message']['items']
        for item in items:
            print(f"Title: {item.get('title', ['No title'])[0]}")
            print(f"DOI: {item.get('DOI', 'No DOI')}")
            print(f"Journal: {item.get('container-title', [''])[0]}")
            print("-" * 20)
    except Exception as e:
        print(e)

print("Searching for Thombare 2018...")
search("Thombare Guar gum superabsorbent hydrogels agriculture 2018")
