import datetime
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")


def _make_session():
    s = requests.Session()
    retry = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


def _month_is_complete(year, month):
    """Return True if the given month is entirely in the past."""
    today = datetime.date.today()
    if year < today.year:
        return True
    if year == today.year and month < today.month:
        return True
    return False


def _cache_path(year, month, page):
    return os.path.join(CACHE_DIR, f"{year:04d}-{month:02d}_p{page}.html")


def _fetch_page(year, month, page):
    """Fetch a single archive page, using cache if the month is complete."""
    cache_file = _cache_path(year, month, page)
    use_cache = _month_is_complete(year, month)

    if use_cache and os.path.exists(cache_file):
        print(f"  (cached) page {page}")
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()

    url = f"http://blog.livedoor.jp/bachelor_seal-puzzle/archives/{year:04d}-{month:02d}.html"
    page_url = url if page == 1 else f"{url}?p={page}"
    print(f"  Fetching {page_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    session = _make_session()
    resp = session.get(page_url, timeout=30, headers=headers)
    resp.raise_for_status()
    html = resp.text

    if use_cache:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(html)

    return html


def _parse_page(html):
    """Parse a single page of HTML, return list of (date, title, puzz_link_url) and whether there's a next page."""
    soup = BeautifulSoup(html, "html.parser")
    puzzles = []

    divs = soup.find_all("div", class_="article-outer")
    for div in divs:
        date_span = div.find("span", class_="article-date")
        date = date_span.text.strip() if date_span else ""

        title_tag = div.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else ""

        links = [a.get("href", "") for a in div.find_all("a") if a.get("href")]
        puzz_link = None
        for link in links:
            if "puzz.link/p" in link or "pzv.jp/p" in link:
                puzz_link = link
                break

        # Extract star rating from category
        stars = 0
        for a in div.find_all("a"):
            text = a.get_text(strip=True)
            if "難易度" in text:
                stars = text.count("☆")
                break

        if puzz_link:
            puzzles.append((date, title, puzz_link, stars))

    has_next = False
    pager = soup.find("div", class_="pager")
    if pager and pager.find("a", rel="next"):
        has_next = True

    return puzzles, has_next


def fetch_month(year, month):
    """Fetch all blog posts from a given month, return list of (date, title, puzz_link_url)."""
    all_puzzles = []
    page = 1

    while True:
        html = _fetch_page(year, month, page)
        puzzles, has_next = _parse_page(html)
        if not puzzles:
            break
        all_puzzles.extend(puzzles)
        if has_next:
            page += 1
            time.sleep(2)
        else:
            break

    return all_puzzles
