from pydantic import BaseModel

class Book(BaseModel):
    id: int
    title: str
    price: float
    stock: str
    rating: int
    category: str
    product_page_url: str
    upc: str
    description: str
