import os
from fastapi import APIRouter, HTTPException, Query
from api.data_loader import load_books

router = APIRouter(
    prefix="/api/v1/books",
    tags=["books"]
)
CSV_PATH = os.path.join(os.getcwd(), "data", "books.csv")
books_data = load_books(CSV_PATH)
print(f"Total de livros carregados: {len(books_data)}") 

@router.get("/", description="Lista todos os livros disponíveis na base de dados.")
def list_books():
   
    return [b.dict() for b in books_data]

@router.get("/{book_id}", description="Retorna os detalhes completos de um livro específico pelo ID.")
def get_book(book_id: int):
    for book in books_data:
        if book.id == book_id:
            return book.dict()
    raise HTTPException(status_code=404, detail="Livro não encontrado")

@router.get("/search", description="Busca livros por título e/ou categoria.")
def search_books(title: str = Query(None), category: str = Query(None)):
    results = books_data
    if title:
        results = [b for b in results if title.lower() in b.title.lower()]
    if category:
        results = [b for b in results if category.lower() in b.category.lower()]
    return [b.dict() for b in results]

@router.get("/top-rated")
def top_rated(limit: int = Query(10)):
    top = sorted(books_data, key=lambda x: x.rating, reverse=True)[:limit]
    return [b.dict() for b in top]

@router.get("/price-range")
def price_range(min: float = Query(0), max: float = Query(1000)):
    filtered = [b for b in books_data if min <= b.price <= max]
    return [b.dict() for b in filtered]
