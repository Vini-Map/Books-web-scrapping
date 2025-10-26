import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin
import os

BASE_URL = "https://books.toscrape.com/"
OUTPUT_CSV = os.path.join("data", "books.csv")
HEADERS = [
    "id",
    "title",
    "price",
    "stock",
    "rating",
    "category",
    "product_page_url",
    "upc",
    "description",
]

def rating_to_int(class_list):
    mapping = {"One":1, "Two":2, "Three":3, "Four":4, "Five":5}
    for c in class_list:
        if c in mapping:
            return mapping[c]
    return 0

def parse_book(book_url, session):
    r = session.get(book_url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1").text.strip() if soup.find("h1") else ""
    product_main = soup.find("div", class_="product_main")
    price = ""
    stock = ""
    rating = 0
    if product_main:
        p_tag = product_main.find("p", class_="price_color")
        price = p_tag.text.strip() if p_tag else ""
        s_tag = product_main.find("p", class_="instock availability")
        stock = s_tag.text.strip() if s_tag else ""
        r_tag = product_main.find("p", class_="star-rating")
        rating = rating_to_int(r_tag.get("class", [])) if r_tag else 0

    # category via breadcrumb
    breadcrumb = soup.find("ul", class_="breadcrumb")
    category = ""
    if breadcrumb:
        items = breadcrumb.find_all("li")
        if len(items) >= 3:
            category = items[2].text.strip()

    # product info table (UPC etc)
    table = soup.find("table", class_="table table-striped")
    upc = ""
    if table:
        for tr in table.find_all("tr"):
            th = tr.find("th")
            td = tr.find("td")
            if th and th.text.strip() == "UPC":
                upc = td.text.strip()

    # description
    desc = ""
    desc_tag = soup.find("div", id="product_description")
    if desc_tag and desc_tag.find_next_sibling("p"):
        desc = desc_tag.find_next_sibling("p").text.strip()

    return {
        "title": title,
        "price": price,
        "stock": stock,
        "rating": rating,
        "category": category,
        "product_page_url": book_url,
        "upc": upc,
        "description": desc,
    }

def run_scraper(pages_limit=None, delay=0.5):
    session = requests.Session()
    results = []
    # start in catalogue (site uses catalogue/page-1.html)
    page_path = "catalogue/page-1.html"
    idx = 0

    while True:
        url = urljoin(BASE_URL, page_path)
        print(f"Fetching {url}")
        r = session.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        articles = soup.find_all("article", class_="product_pod")
        for card in articles:
            # link can be relative like '../../../the-book_1/index.html'
            href = card.find("h3").find("a")["href"]
            book_url = urljoin(url, href).replace('../', '')
            try:
                idx += 1
                item = parse_book(book_url, session)
                item["id"] = idx
                results.append(item)
                print(f"  - [{idx}] {item['title']}")
            except Exception as e:
                print("  ! error parsing:", e)

            if pages_limit and idx >= pages_limit:
                break
        if pages_limit and idx >= pages_limit:
            break

        next_btn = soup.find("li", class_="next")
        if not next_btn:
            break
        next_href = next_btn.find("a")["href"]
        # build next page path relative to current page_path
        page_path = urljoin(page_path, next_href)
        time.sleep(delay)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k, "") for k in HEADERS})

    print(f"Saved {len(results)} books to {OUTPUT_CSV}")

if __name__ == "__main__":
    run_scraper()
