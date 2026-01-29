import json
import urllib.parse
import urllib.request


def crossref_search(query: str, rows: int = 5):
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {
            "query.bibliographic": query,
            "rows": rows,
            "select": "DOI,title,author,issued,container-title,publisher,type",
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
    queries = [
        "Biochemical and physiological mechanisms mediated by allelochemicals Weir Vivanco",
        "Allelopathic interactions between plants multi site action of allelochemicals Gniazdowska Bogatek",
        "reactive oxygen species allelopathy review",
        "phenolic allelochemicals root growth oxidative stress review",
    ]

    for q in queries:
        print("\nQUERY:", q)
        try:
            items = crossref_search(q, rows=8)
        except Exception as e:
            print("ERROR:", e)
            continue

        for idx, it in enumerate(items, 1):
            print(f"{idx}. {fmt_item(it)}")


if __name__ == "__main__":
    main()
