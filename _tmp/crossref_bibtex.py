import sys
import urllib.parse
import urllib.request


def get_bibtex(doi: str) -> str:
    doi_enc = urllib.parse.quote(doi)
    url = f"https://api.crossref.org/works/{doi_enc}/transform/application/x-bibtex"
    req = urllib.request.Request(url, headers={"User-Agent": "hidrorretentor-manuscript/1.0 (mailto:example@example.com)"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def main(dois: list[str]):
    for doi in dois:
        print("\n" + "=" * 120)
        print("DOI:", doi)
        try:
            print(get_bibtex(doi).strip())
        except Exception as e:
            print("ERROR:", e)


if __name__ == "__main__":
    dois = sys.argv[1:]
    if not dois:
        dois = [
            "10.1016/j.pbi.2004.05.007",
            "10.1007/s11738-005-0017-3",
            "10.4161/psb.2.4.4116",
            "10.3390/antiox10111648",
        ]
    main(dois)
