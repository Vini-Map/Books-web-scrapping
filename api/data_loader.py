import csv
from .utils import clean_price
from .models import Book

def load_books(csv_path="data/books.csv"):
    books = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                books.append(Book(
                    id=int(row["id"]),
                    title=row["title"],
                    price=clean_price(row["price"]),
                    stock=row["stock"],
                    rating=int(row["rating"]),
                    category=row["category"],
                    product_page_url=row["product_page_url"],
                    upc=row["upc"],
                    description=row["description"]
                ))
            except Exception:
                continue
    return books
