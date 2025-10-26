from fastapi import APIRouter
from ..data_loader import load_books
from collections import defaultdict

router = APIRouter(
    prefix="/api/v1/stats",
    tags=["stats"]
)

books_data = load_books()

@router.get("/overview", description="Exibe estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings).")
def stats_overview():
    total_books = len(books_data)
    avg_price = sum([b.price for b in books_data]) / total_books if total_books else 0
    rating_counts = {}
    for b in books_data:
        rating_counts[b.rating] = rating_counts.get(b.rating, 0) + 1
    return {"total_books": total_books, "avg_price": round(avg_price,2), "ratings_distribution": rating_counts}

@router.get("/categories", description="Exibe estatísticas detalhadas por categoria (quantidade de livros, preço médio por categoria).")
def stats_by_category():
    data = defaultdict(lambda: {"count": 0, "avg_price": 0})
    for b in books_data:
        cat = b.category
        data[cat]["count"] += 1
        data[cat]["avg_price"] += b.price
    for cat in data:
        data[cat]["avg_price"] = round(data[cat]["avg_price"] / data[cat]["count"],2)
    return data
