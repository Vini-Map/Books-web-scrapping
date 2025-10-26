from fastapi import APIRouter, HTTPException, Query
from ..data_loader import load_books

router = APIRouter(
    prefix="/api/v1/books",
    tags=["books"]
)

books_data = load_books()

@router.get("/", description="Lista todos os livros disponíveis na base de dados.")
def list_books():
    return books_data

@router.get("/{book_id}", description="Retorna os detalhes completos de um livro específico pelo ID.")
def get_book(book_id: int):
    for book in books_data:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Livro não encontrado")

@router.get("/search", description="Busca livros por título e/ou categoria.")
def search_books(title: str = Query(None, description="Título parcial do livro"),
                 category: str = Query(None, description="Categoria do livro")):
    results = books_data
    if title:
        results = [b for b in results if title.lower() in b.title.lower()]
    if category:
        results = [b for b in results if category.lower() in b.category.lower()]
    return results

@router.get("/top-rated", description="Lista os livros com melhor avaliação (rating mais alto).")
def top_rated(limit: int = Query(10, description="Quantidade máxima de livros a retornar")):
    return sorted(books_data, key=lambda x: x.rating, reverse=True)[:limit]

@router.get("/price-range", description="Filtra livros dentro de uma faixa de preço específica.")
def price_range(min: float = Query(0, description="Preço mínimo"),
                max: float = Query(1000, description="Preço máximo")):
    return [b for b in books_data if min <= b.price <= max]
