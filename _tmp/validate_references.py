import re
import requests
import time
from difflib import SequenceMatcher
import urllib3
import logging

# Suppress insecure request warnings if they occur (though we use https)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BIB_FILE = r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2 - HIDRORRETENTOR\3 - MANUSCRITO\1-MARKDOWN\1-MANUSCRITOS\referencias.bib"
MD_FILE = r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2 - HIDRORRETENTOR\3 - MANUSCRITO\1-MARKDOWN\1-MANUSCRITOS\Hidrorretentor_Taboa.md"

def get_cited_keys(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Find all @key citations. 
    keys = re.findall(r'@([a-zA-Z0-9_:-]+)', content)
    
    valid_keys = set()
    for k in keys:
        if len(k) > 2 and not k[0].isdigit(): # basic heuristic
             valid_keys.add(k)
    return valid_keys

def parse_bib_file(bib_path):
    with open(bib_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = {}
    
    raw_entries = content.split('@')
    for raw in raw_entries:
        if not raw.strip(): continue
        
        match = re.match(r'^(\w+)\s*{\s*([^,]+),', raw)
        if match:
            type_ = match.group(1)
            key = match.group(2).strip()
            
            title_match = re.search(r'title\s*=\s*{([^}]+)}', raw, re.IGNORECASE | re.DOTALL)
            if not title_match:
                 title_match = re.search(r'title\s*=\s*"([^"]+)"', raw, re.IGNORECASE | re.DOTALL)
            
            title = title_match.group(1) if title_match else None
            if title:
                title = " ".join(title.split()) # Normalize whitespace

            doi_match = re.search(r'doi\s*=\s*{([^}]+)}', raw, re.IGNORECASE)
            if not doi_match:
                 doi_match = re.search(r'doi\s*=\s*"([^"]+)"', raw, re.IGNORECASE)
                 
            doi = doi_match.group(1) if doi_match else None
            
            entries[key] = {
                'type': type_,
                'title': title,
                'doi': doi
            }
    return entries

def check_crossref(title, doi=None):
    url = "https://api.crossref.org/works"
    params = {'rows': 1}
    
    if doi:
        doi = doi.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')

    if doi:
        # Check specific DOI first
        try:
            r = requests.get(f"{url}/{doi}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                return data['message'], "DOI_MATCH"
        except Exception:
            pass # Fallback to title search

    if title:
        params['query.title'] = title
        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                items = data['message']['items']
                if items:
                    return items[0], "TITLE_SEARCH"
        except Exception as e:
            pass
            
    return None, "NOT_FOUND"

def similarity(a, b):
    if not a or not b: return 0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def main():
    print(f"Analyzing citations in manuscript...")
    cited_keys = get_cited_keys(MD_FILE)
    print(f"Found {len(cited_keys)} unique cited keys.")
    
    print(f"Parsing bibliography...")
    bib_entries = parse_bib_file(BIB_FILE)
    print(f"Found {len(bib_entries)} entries in bib file.")
    
    missing_in_bib = [k for k in cited_keys if k not in bib_entries]
    if missing_in_bib:
        print(f"\n WARNING: {len(missing_in_bib)} keys cited but missing in bib file:")
        for k in missing_in_bib:
            print(f"  - {k}")
            
    keys_to_check = [k for k in cited_keys if k in bib_entries]
    
    print(f"\nVerifying {len(keys_to_check)} citations against Crossref...")
    print("-" * 60)
    
    issues = []
    
    for i, key in enumerate(keys_to_check):
        entry = bib_entries[key]
        title = entry.get('title')
        doi = entry.get('doi')
        
        if not title and not doi:
            continue
            
        result, method = check_crossref(title, doi)
        
        remote_title = "N/A"
        
        if result:
            remote_title_list = result.get('title', [''])
            remote_title = remote_title_list[0] if remote_title_list else "No Title"
            
            title_sim = similarity(title, remote_title) if title else 0
            
            if method == "DOI_MATCH":
                 pass
            elif title_sim > 0.75:
                 pass
            else:
                 print(f" SUSPICIOUS: Title mismatch for '{key}'")
                 print(f"    Local:  {title}")
                 print(f"    Remote: {remote_title}")
                 print(f"    Match Score: {title_sim:.2f}")
                 issues.append({'key': key, 'issue': 'Title mismatch', 'local': title, 'remote': remote_title})
        else:
            print(f" NOT FOUND: '{key}'")
            print(f"    Local Title: {title}")
            issues.append({'key': key, 'issue': 'Not found in Crossref', 'local': title})
            
        time.sleep(0.1) 

    print("\n" + "="*50)
    print("SUMMARY OF INVESTIGATION")
    print("="*50)
    
    if missing_in_bib:
        print(f"\nMISSING KEYS (Not in .bib):")
        for k in missing_in_bib:
            print(f"- {k}")

    if not issues:
        print("\nAll found references seem to match Crossref records reasonably well.")
    else:
        print(f"\nFound {len(issues)} potential issues:")
        for issue in issues:
            print(f"\nKey: {issue['key']}")
            print(f"  Issue: {issue['issue']}")
            
if __name__ == "__main__":
    main()
