import json
import sys
import urllib.parse
import urllib.request


def crossref_search(query: str, rows: int = 8):
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {
            "query.bibliographic": query,
            "rows": rows,
            "select": "DOI,title,author,issued,container-title,type",
        }
    )
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.load(response)
    return data["message"]["items"]


def fmt_item(it: dict) -> str:
    year = None
    try:
        year = it.get("issued", {}).get("date-parts", [[None]])[0][0]
    except Exception:
        year = None

    title = (it.get("title") or [""])[0]
    container = (it.get("container-title") or [""])[0]
    doi = it.get("DOI")
    return f"{year} | {title} | {container} | DOI: {doi}"


def main():
    if len(sys.argv) > 1:
        queries = sys.argv[1:]
    else:
        queries = [
            "root growth mechanical impedance soil strength review",
            "soil aeration oxygen diffusion root growth",
            "soil penetration resistance root elongation",
            "soil compaction root growth review Plant and Soil",
            "air-filled porosity oxygen diffusion root growth",
            "pore connectivity root growth soil structure",
            "rhizosphere oxygen diffusion limitation root growth",
        ]

    for q in queries:
        print("\nQUERY:", q)
        try:
            items = crossref_search(q, rows=10)
        except Exception as e:
            print("ERROR:", e)
            continue

        for idx, it in enumerate(items, 1):
            print(f"{idx}. {fmt_item(it)}")


if __name__ == "__main__":
    main()
