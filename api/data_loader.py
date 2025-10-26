import csv
from api.models import Book
from api.utils import clean_price
import os

def load_books(csv_path=None):
    if csv_path is None:
        # Caminho padrão relativo
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(BASE_DIR, "..", "data", "books.csv")
    
    print(f"Tentando abrir CSV em: {csv_path}")

    books = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            print(f"Colunas encontradas no CSV: {reader.fieldnames}")
            for i, row in enumerate(reader, 1):
                try:
                    book = Book(
                        id=int(row["id"]),
                        title=row["title"],
                        price=clean_price(row["price"]),
                        stock=row["stock"],
                        rating=int(row["rating"]),
                        category=row["category"],
                        product_page_url=row["product_page_url"],
                        upc=row["upc"],
                        description=row["description"]
                    )
                    books.append(book)
                except Exception as e:
                    print(f"Erro no livro na linha {i}: {e}")
        print(f"Total de livros carregados: {len(books)}")
    except FileNotFoundError:
        print("Arquivo CSV não encontrado!")
    except Exception as e:
        print(f"Erro ao abrir CSV: {e}")

    return books
