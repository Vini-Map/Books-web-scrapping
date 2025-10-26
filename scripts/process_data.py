import pandas as pd
import re
import os

IN_CSV = os.path.join('data', 'books.csv')
OUT_DIR = os.path.join('data', 'processed')
OUT_CSV = os.path.join(OUT_DIR, 'books_clean.csv')

def parse_price(s):
    if pd.isna(s):
        return None
    s = str(s).replace('£','').replace('\n','').strip()
    m = re.search(r"\d+[.,]?\d*", s)
    if not m:
        return None
    return float(m.group(0).replace(',', '.'))

def parse_stock(s):
    if pd.isna(s):
        return 0
    m = re.search(r"(\d+)", str(s))
    return int(m.group(1)) if m else 0

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv(IN_CSV)
    for col in ['price','stock','title','category','description','rating','product_page_url','upc','id']:
        if col not in df.columns:
            df[col] = None

    df['price'] = df['price'].apply(parse_price)
    df['stock'] = df['stock'].apply(parse_stock)
    df['title'] = df['title'].astype(str).str.strip()
    df['category'] = df['category'].astype(str).str.strip()
    df.to_csv(OUT_CSV, index=False)
    print('Saved cleaned file to', OUT_CSV)

if __name__ == "__main__":
    main()
