import requests
from bs4 import BeautifulSoup
from pathlib import Path
import sys
import time
OUTFILE = Path("nifty50_symbols.txt")
WIKI_URL = "https://en.wikipedia.org/wiki/NIFTY_50"

def fetch_wikipedia_nifty50():
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; NIFTY50-Scraper/1.0; +https://example.com/)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        resp = requests.get(WIKI_URL, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching {WIKI_URL}: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table", {"class": "wikitable"})
    symbols = []

    for table in tables:
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if not headers:
            continue
        if any("symbol" in h or "scrip code" in h or "isin" in h for h in headers):
            for tr in table.find_all("tr")[1:]:
                tds = tr.find_all(["td", "th"])
                if not tds:
                    continue
                row_cells = [td.get_text(strip=True) for td in tds]
                symbol_candidate = None
                for cell in row_cells:
                    if cell and cell.replace(".", "").replace("-", "").isalnum():
                        if cell.upper() == cell and 1 < len(cell) <= 10:
                            symbol_candidate = cell
                            break
                if symbol_candidate is None:
                    try:
                        sym_index = next(i for i, h in enumerate(headers) if "symbol" in h or "scrip code" in h)
                        symbol_candidate = row_cells[sym_index]
                    except StopIteration:
                        symbol_candidate = row_cells[0] if row_cells else None
                    except Exception:
                        pass

                if symbol_candidate:
                    sym = symbol_candidate.split()[0].strip().replace("\u200b", "")
                    symbols.append(sym)
            if len(symbols) >= 40:
                break
    symbols = sorted(list(dict.fromkeys(symbols)))
    return symbols

def main():
    print("Fetching NIFTY 50 symbols from Wikipedia:")
    symbols = fetch_wikipedia_nifty50()
    if not symbols:
        print("Failed to fetch symbols.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(symbols)} candidate symbols. Saving to {OUTFILE}")
    with OUTFILE.open("w", encoding="utf-8") as f:
        for s in symbols:
            f.write(s + "\n")
    print(f"Wrote {len(symbols)} symbols to {OUTFILE}")

if __name__ == "__main__":
    main()
