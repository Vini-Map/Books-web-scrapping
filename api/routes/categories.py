from fastapi import APIRouter
from ..data_loader import load_books

router = APIRouter(
    prefix="/api/v1/categories",
    tags=["categories"]
)

books_data = load_books()

@router.get("/", description="Retorna a lista de todas as categorias de livros disponíveis.")
def get_categories():
    categories = sorted(set([b.category for b in books_data if b.category]))
    return {"categories": categories}
