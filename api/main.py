from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from .routes import books, categories, stats, health


app = FastAPI(
    title="📚 FIAP Books API",
    version="1.0",
    description="""
API pública de livros extraídos de [Books to Scrape](https://books.toscrape.com/).

**Endpoints principais**:
- `/api/v1/books` - lista todos os livros
- `/api/v1/books/{id}` - detalhes de um livro
- `/api/v1/books/search` - busca por título/categoria
- `/api/v1/categories` - lista categorias
- `/api/v1/health` - status da API

**Endpoints de insights**:
- `/api/v1/stats/overview` - estatísticas gerais
- `/api/v1/stats/categories` - estatísticas por categoria
- `/api/v1/books/top-rated` - livros top rated
- `/api/v1/books/price-range` - filtra por faixa de preço
""",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.include_router(health.router)
app.include_router(categories.router)
app.include_router(books.router)
app.include_router(stats.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="📚 FIAP Books API",
        version="1.0",
        description="API de consulta de livros para cientistas de dados e sistemas de recomendação.",
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://upload.wikimedia.org/wikipedia/commons/1/14/Book_icon.svg"
    }


    openapi_schema["tags"] = [
        {"name": "health", "description": "Endpoint de status da API"},
        {"name": "books", "description": "Listagem e detalhes de livros"},
        {"name": "categories", "description": "Categorias de livros disponíveis"},
        {"name": "stats", "description": "Estatísticas e insights dos livros"},
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
