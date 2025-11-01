# 🏗️ Plano Arquitetural — Books Web Scraping & API

## 📋 Índice

1. [Visão Geral da Arquitetura Atual](#1-visão-geral-da-arquitetura-atual)
2. [Pipeline de Dados Detalhado](#2-pipeline-de-dados-detalhado)
3. [Arquitetura da API](#3-arquitetura-da-api)
4. [Escalabilidade Futura](#4-escalabilidade-futura)
5. [Cenários de Uso para Cientistas de Dados/ML](#5-cenários-de-uso-para-cientistas-de-dadosml)
6. [Plano de Integração com Modelos de ML](#6-plano-de-integração-com-modelos-de-ml)

---

## 1. Visão Geral da Arquitetura Atual

### 1.1 Diagrama de Alto Nível

```
┌─────────────────────┐
│  Books to Scrape    │  ← Fonte de Dados Externa
│  (Site Web)         │
└──────────┬──────────┘
           │ HTTP Requests
           ▼
┌─────────────────────┐
│   SCRAPER           │
│   (BeautifulSoup)   │  ← scripts/scraper.py
└──────────┬──────────┘
           │ CSV Raw
           ▼
┌─────────────────────┐
│   data/books.csv    │  ← Armazenamento Raw
└──────────┬──────────┘
           │ Read CSV
           ▼
┌─────────────────────┐
│ DATA PROCESSOR      │
│ (Pandas)            │  ← scripts/process_data.py
└──────────┬──────────┘
           │ CSV Processed
           ▼
┌─────────────────────┐
│ data/processed/     │  ← Dados Limpos
│ books_clean.csv     │
└──────────┬──────────┘
           │ Load & Cache
           ▼
┌─────────────────────┐
│   FASTAPI           │
│   REST API          │  ← api/
└──────────┬──────────┘
           │ JSON via HTTP
           ▼
┌─────────────────────┐
│   CONSUMIDORES      │
│   • Web Apps        │
│   • Data Scientists │
│   • ML Engineers    │
│   • BI Tools        │
└─────────────────────┘
```

### 1.2 Arquitetura em Camadas

```
╔═══════════════════════════════════════════════════════╗
║              CAMADA DE APRESENTAÇÃO                   ║
║  • Swagger UI (Documentação Interativa)              ║
║  • ReDoc (Documentação Alternativa)                  ║
║  • JSON Responses                                     ║
╚═══════════════════════════════════════════════════════╝
                        ▲
                        │
╔═══════════════════════════════════════════════════════╗
║              CAMADA DE APLICAÇÃO (API)                ║
║  FastAPI Framework:                                   ║
║  • api/main.py        - Aplicação principal          ║
║  • api/routes/        - Endpoints organizados        ║
║  • api/models.py      - Schemas Pydantic             ║
║  • api/utils.py       - Funções auxiliares           ║
║  • api/data_loader.py - Carregamento de dados        ║
╚═══════════════════════════════════════════════════════╝
                        ▲
                        │
╔═══════════════════════════════════════════════════════╗
║           CAMADA DE ARMAZENAMENTO                     ║
║  • data/books.csv         - Dados brutos             ║
║  • data/processed/        - Dados processados        ║
║  • Cache em memória       - DataFrame carregado      ║
╚═══════════════════════════════════════════════════════╝
                        ▲
                        │
╔═══════════════════════════════════════════════════════╗
║            CAMADA DE PROCESSAMENTO                    ║
║  • scripts/process_data.py - Limpeza e validação    ║
║  • Pandas transformations  - ETL                     ║
╚═══════════════════════════════════════════════════════╝
                        ▲
                        │
╔═══════════════════════════════════════════════════════╗
║             CAMADA DE INGESTÃO                        ║
║  • scripts/scraper.py     - Web scraping             ║
║  • BeautifulSoup4         - HTML parsing             ║
║  • Requests               - HTTP client              ║
╚═══════════════════════════════════════════════════════╝
```

---

## 2. Pipeline de Dados Detalhado

### 2.1 Fase 1: INGESTÃO - Web Scraping

**Arquivo:** `scripts/scraper.py`

#### Fluxo de Execução

```
INÍCIO
  │
  ├─► 1. Inicializar sessão HTTP
  │   └─► requests.Session()
  │
  ├─► 2. Loop pelas páginas do catálogo
  │   ├─► GET /catalogue/page-1.html
  │   ├─► Parse HTML com BeautifulSoup
  │   ├─► Identificar cards de livros
  │   └─► Para cada livro:
  │       ├─► Extrair link do produto
  │       ├─► GET página individual do livro
  │       ├─► Extrair dados (parse_book)
  │       │   ├─► Título (tag h1)
  │       │   ├─► Preço (class price_color)
  │       │   ├─► Estoque (class instock)
  │       │   ├─► Rating (class star-rating)
  │       │   ├─► Categoria (breadcrumb)
  │       │   ├─► UPC (tabela product info)
  │       │   └─► Descrição (tag p após product_description)
  │       └─► Adicionar à lista de resultados
  │
  ├─► 3. Navegar para próxima página
  │   └─► Verificar botão "next"
  │
  ├─► 4. Consolidar dados
  │   └─► Criar lista com todos os livros
  │
  └─► 5. Salvar em CSV
      └─► data/books.csv (UTF-8)
FIM
```

#### Dados Coletados

| Campo | Origem no HTML | Tipo | Exemplo |
|-------|---------------|------|---------|
| `id` | Gerado sequencialmente | int | 1 |
| `title` | `<h1>` | str | "A Light in the Attic" |
| `price` | `<p class="price_color">` | str | "£51.77" |
| `stock` | `<p class="instock availability">` | str | "In stock (22 available)" |
| `rating` | `<p class="star-rating Three">` | int | 3 |
| `category` | `<ul class="breadcrumb">` > li[2] | str | "Poetry" |
| `product_page_url` | URL construída | str | "https://books.toscrape..." |
| `upc` | `<table>` > tr com th="UPC" | str | "a897fe39b1053632" |
| `description` | `<p>` após `#product_description` | str | "It's hard to imagine..." |

#### Características Técnicas

```python
# Rate Limiting
time.sleep(0.5)  # Delay entre requests

# Error Handling por livro
try:
    item = parse_book(book_url, session)
except Exception as e:
    print("  ! error parsing:", e)
    # Continua para o próximo livro

# Timeout configurado
session.get(url, timeout=10)

# Normalização de URLs relativas
book_url = urljoin(url, href).replace('../', '')
```

#### Qualidade da Extração

- ✅ **Completude**: Extrai todos os 9 campos disponíveis
- ✅ **Robustez**: Try/catch individual por livro
- ✅ **Resiliência**: Não interrompe scraping por falhas pontuais
- ✅ **Performance**: Session reutilizada, delay controlado
- ⚠️ **Limitação**: Single-threaded (sequencial)

---

### 2.2 Fase 2: PROCESSAMENTO - Limpeza de Dados

**Arquivo:** `scripts/process_data.py`

#### Pipeline de Transformação

```
LEITURA
  │
  ├─► pd.read_csv('data/books.csv')
  │
  ▼
VALIDAÇÃO DE COLUNAS
  │
  ├─► Verificar presença de campos obrigatórios
  ├─► Criar colunas ausentes com None
  │
  ▼
TRANSFORMAÇÕES
  │
  ├─► 1. PRICE
  │   ├─► Remover símbolo £
  │   ├─► Extrair números com regex
  │   ├─► Converter para float
  │   │   "£51.77" → 51.77
  │
  ├─► 2. STOCK
  │   ├─► Extrair número com regex
  │   ├─► Converter para int
  │   │   "In stock (22 available)" → 22
  │
  ├─► 3. TITLE
  │   ├─► Converter para string
  │   ├─► Remover espaços em branco
  │   │   "  A Light  " → "A Light"
  │
  └─► 4. CATEGORY
      ├─► Converter para string
      └─► Remover espaços em branco
  │
  ▼
PERSISTÊNCIA
  │
  └─► df.to_csv('data/processed/books_clean.csv')
```

#### Funções de Limpeza

```python
def parse_price(s):
    """
    Converte string de preço em float
    Entrada: "£51.77"
    Saída: 51.77
    """
    if pd.isna(s):
        return None
    s = str(s).replace('£','').replace('\n','').strip()
    m = re.search(r"\d+[.,]?\d*", s)
    if not m:
        return None
    return float(m.group(0).replace(',', '.'))

def parse_stock(s):
    """
    Extrai quantidade numérica de estoque
    Entrada: "In stock (22 available)"
    Saída: 22
    """
    if pd.isna(s):
        return 0
    m = re.search(r"(\d+)", str(s))
    return int(m.group(1)) if m else 0
```

#### Métricas de Qualidade

| Aspecto | Implementação | Resultado |
|---------|---------------|-----------|
| **Completude** | Validação de colunas | 100% de campos |
| **Consistência** | Conversão forçada de tipos | Tipos uniformes |
| **Precisão** | Regex para extração | Valores corretos |
| **Padronização** | strip() em strings | Sem espaços extras |

---

### 2.3 Fase 3: API - Exposição dos Dados

**Estrutura:** `api/`

#### Componentes da API

```
api/
│
├── main.py                 ← Aplicação FastAPI principal
│   ├─► Configuração CORS
│   ├─► Inclusão de routers
│   ├─► Customização Swagger
│   └─► Inicialização da app
│
├── data_loader.py          ← Gerenciamento de dados
│   ├─► Carregamento do CSV
│   ├─► Cache em memória (DataFrame)
│   └─► Funções de acesso
│
├── models.py               ← Schemas Pydantic
│   ├─► BookResponse
│   ├─► BookList
│   └─► Modelos de validação
│
├── utils.py                ← Funções auxiliares
│   └─► Helpers diversos
│
└── routes/                 ← Endpoints organizados
    ├── books.py            ← CRUD de livros
    ├── categories.py       ← Operações com categorias
    ├── stats.py            ← Estatísticas
    └── health.py           ← Health check
```

#### Endpoints Implementados

**1. Books (api/routes/books.py)**

```python
GET /api/v1/books
    Parâmetros:
    - page: int = 1
    - size: int = 10
    - category: str | None
    - min_price: float | None
    - max_price: float | None
    - min_rating: int | None
    
    Retorna: Lista paginada de livros

GET /api/v1/books/{book_id}
    Retorna: Detalhes de um livro específico

GET /api/v1/books/search
    Parâmetros:
    - title: str | None
    - category: str | None
    
    Retorna: Livros que correspondem à busca
```

**2. Categories (api/routes/categories.py)**

```python
GET /api/v1/categories
    Retorna: Dicionário {categoria: quantidade}
```

**3. Stats (api/routes/stats.py)**

```python
GET /api/v1/stats/overview
    Retorna:
    - total_books: int
    - total_categories: int
    - average_price: float
    - average_rating: float
    - price_range: {min, max}

GET /api/v1/stats/categories
    Retorna: Estatísticas por categoria
```

**4. Health (api/routes/health.py)**

```python
GET /api/v1/health
    Retorna:
    - status: "healthy"
    - timestamp: datetime
    - data_loaded: bool
    - total_books: int
```

#### Fluxo de Requisição

```
Cliente HTTP
    │
    ▼
┌─────────────────────┐
│  FastAPI Routing    │
│  (Decorators @app)  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Validação Pydantic │
│  (Request params)   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Lógica de Negócio  │
│  (Route handler)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Data Loader        │
│  (Acesso ao cache)  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  DataFrame Pandas   │
│  (Operações)        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Serialização JSON  │
│  (Response model)   │
└─────────┬───────────┘
          │
          ▼
    Response HTTP
```

#### Gerenciamento de Dados em Memória

```python
# api/data_loader.py (Exemplo simplificado)

class DataLoader:
    def __init__(self):
        self._df = None
    
    def load_data(self):
        """Carrega CSV uma única vez na inicialização"""
        if self._df is None:
            self._df = pd.read_csv('data/books.csv')
    
    def get_all_books(self):
        """Retorna todos os livros"""
        return self._df.to_dict('records')
    
    def get_book_by_id(self, book_id: int):
        """Busca livro por ID"""
        book = self._df[self._df['id'] == book_id]
        return book.to_dict('records')[0] if not book.empty else None
    
    def filter_books(self, **filters):
        """Aplica filtros ao DataFrame"""
        df_filtered = self._df.copy()
        
        if 'category' in filters:
            df_filtered = df_filtered[
                df_filtered['category'] == filters['category']
            ]
        
        if 'min_price' in filters:
            df_filtered = df_filtered[
                df_filtered['price'] >= filters['min_price']
            ]
        
        # ... outros filtros
        
        return df_filtered.to_dict('records')

# Instância global
data_loader = DataLoader()
```

#### Características da API

| Característica | Implementação | Benefício |
|----------------|---------------|-----------|
| **Documentação Automática** | Swagger + ReDoc | Fácil consumo |
| **Validação** | Pydantic models | Type safety |
| **CORS** | CORSMiddleware | Cross-origin |
| **Paginação** | Query params | Performance |
| **Filtros** | Query params | Flexibilidade |
| **Cache** | DataFrame em memória | Velocidade |
| **Rotas organizadas** | APIRouter | Manutenibilidade |

---

## 3. Arquitetura da API

### 3.1 Design Patterns Utilizados

#### 3.1.1 Repository Pattern (Simplificado)

```python
# data_loader.py age como um Repository
# Abstrai acesso aos dados do resto da aplicação

┌──────────────┐
│   Routes     │  ← Não conhecem detalhes de armazenamento
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Data Loader  │  ← Interface de acesso aos dados
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  CSV/Pandas  │  ← Implementação de armazenamento
└──────────────┘
```

#### 3.1.2 Router Pattern

```python
# Organização modular por domínio

main.py
  ├─► books_router      (api/routes/books.py)
  ├─► categories_router (api/routes/categories.py)
  ├─► stats_router      (api/routes/stats.py)
  └─► health_router     (api/routes/health.py)
```

### 3.2 Modelo de Dados

#### Schema Principal: Book

```python
class BookResponse(BaseModel):
    id: int
    title: str
    price: Optional[float] = None
    stock: Optional[int] = None
    rating: Optional[int] = None
    category: Optional[str] = None
    product_page_url: Optional[str] = None
    upc: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "A Light in the Attic",
                "price": 51.77,
                "stock": 22,
                "rating": 3,
                "category": "Poetry",
                "product_page_url": "https://books.toscrape.com/...",
                "upc": "a897fe39b1053632",
                "description": "It's hard to imagine..."
            }
        }
```

### 3.3 Fluxo de Dados Completo

```
┌─────────────────────────────────────────────────────┐
│  1. STARTUP                                         │
│     • FastAPI app criado                            │
│     • CORS configurado                              │
│     • Routers incluídos                             │
│     • DataLoader inicializado                       │
│     • CSV carregado em memória                      │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  2. REQUEST                                         │
│     • Cliente faz HTTP GET /api/v1/books           │
│     • FastAPI valida query parameters              │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  3. ROUTING                                         │
│     • FastAPI router direciona para handler        │
│     • Parâmetros extraídos e validados             │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  4. PROCESSING                                      │
│     • Handler chama DataLoader                      │
│     • Filtros aplicados no DataFrame               │
│     • Paginação aplicada                            │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  5. SERIALIZATION                                   │
│     • Dados convertidos para dicionários           │
│     • Pydantic valida/serializa response           │
│     • JSON gerado                                   │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  6. RESPONSE                                        │
│     • HTTP 200 OK                                   │
│     • Headers (Content-Type: application/json)     │
│     • Body com lista de livros                      │
└─────────────────────────────────────────────────────┘
```

---

## 4. Escalabilidade Futura

### 4.1 Limitações Atuais

| Limitação | Impacto | Quando se torna problema |
|-----------|---------|--------------------------|
| **Dados em CSV** | Performance de leitura | > 100k registros |
| **Cache em memória** | Não compartilhado entre instâncias | Deploy multi-instância |
| **Single instance** | Limite de throughput | > 100 req/s |
| **Scraping manual** | Dados desatualizados | Necessidade de atualização frequente |

### 4.2 Próximos Passos de Evolução

#### Fase 1: Banco de Dados (Curto Prazo)

```
Atual:                      Proposta:
┌──────────┐               ┌──────────┐
│   CSV    │   ──────►     │PostgreSQL│
└──────────┘               └──────────┘

Benefícios:
✓ Queries mais eficientes
✓ Índices para performance
✓ Suporte a concorrência
✓ Backup automatizado
```

**Implementação sugerida:**

```python
# Migração simples com SQLAlchemy
from sqlalchemy import create_engine
import pandas as pd

# Carregar CSV
df = pd.read_csv('data/books.csv')

# Criar conexão PostgreSQL
engine = create_engine('postgresql://user:pass@localhost/books')

# Migrar dados
df.to_sql('books', engine, if_exists='replace', index=False)
```

#### Fase 2: Cache Distribuído (Médio Prazo)

```
Atual:                      Proposta:
┌──────────┐               ┌──────────┐
│ In-Memory│   ──────►     │  Redis   │
└──────────┘               └──────────┘

Benefícios:
✓ Cache compartilhado
✓ Suporte a múltiplas instâncias
✓ TTL configurável
✓ Performance consistente
```

#### Fase 3: Orquestração (Longo Prazo)

```
Atual:                      Proposta:
┌──────────┐               ┌──────────┐
│  Manual  │   ──────►     │ Airflow  │
└──────────┘               └──────────┘

Benefícios:
✓ Scraping agendado
✓ Pipeline automatizado
✓ Monitoramento
✓ Retry automático
```

### 4.3 Arquitetura Escalável (Visão Futura)

```
                    ┌──────────────┐
                    │ Load Balancer│
                    └───────┬──────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
        ┌──────────┐              ┌──────────┐
        │ API #1   │              │ API #2   │
        └────┬─────┘              └────┬─────┘
             │                         │
             └──────────┬──────────────┘
                        ▼
                 ┌────────────┐
                 │   Redis    │
                 │   Cache    │
                 └─────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │ PostgreSQL  │
                │  Database   │
                └─────────────┘
```

---

## 5. Cenários de Uso para Cientistas de Dados/ML

### 5.1 Análise Exploratória de Dados (EDA)

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Conectar à API
API_URL = "http://localhost:8000/api/v1"

# Carregar todos os livros
response = requests.get(f"{API_URL}/books", params={"size": 1000})
books = pd.DataFrame(response.json())

# Análises possíveis:

# 1. Distribuição de preços por categoria
plt.figure(figsize=(12, 6))
books.groupby('category')['price'].mean().sort_values().plot(kind='barh')
plt.title('Preço Médio por Categoria')
plt.xlabel('Preço (£)')
plt.tight_layout()
plt.show()

# 2. Correlação entre rating e preço
sns.scatterplot(data=books, x='price', y='rating', hue='category')
plt.title('Relação entre Preço e Rating')
plt.show()

# 3. Análise de estoque
stock_analysis = books.groupby('category').agg({
    'stock': ['sum', 'mean', 'median'],
    'id': 'count'
})
print(stock_analysis)

# 4. Top categorias
top_categories = books['category'].value_counts().head(10)
print(top_categories)
```

### 5.2 Feature Engineering

```python
# Criar features derivadas para ML

# 1. Faixa de preço
def price_category(price):
    if price < 20:
        return 'Barato'
    elif price < 40:
        return 'Médio'
    else:
        return 'Caro'

books['price_category'] = books['price'].apply(price_category)

# 2. Disponibilidade
books['in_stock'] = books['stock'] > 0
books['stock_level'] = pd.cut(
    books['stock'], 
    bins=[0, 5, 15, 50], 
    labels=['Baixo', 'Médio', 'Alto']
)

# 3. Rating binarizado
books['high_rating'] = (books['rating'] >= 4).astype(int)

# 4. Tamanho do título
books['title_length'] = books['title'].str.len()

# 5. Tem descrição
books['has_description'] = books['description'].notna()

# Exportar para análise
books.to_csv('features_engenharia.csv', index=False)
```

### 5.3 Integração com Notebooks

```python
# notebook_template.ipynb

"""
Notebook Template para Análise de Livros
Conecta automaticamente à API local
"""

import requests
import pandas as pd
from typing import Optional

class BooksAPI:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
    
    def get_books(self, 
                  page: int = 1, 
                  size: int = 100,
                  category: Optional[str] = None,
                  min_price: Optional[float] = None) -> pd.DataFrame:
        """Busca livros com filtros"""
        params = {
            "page": page,
            "size": size
        }
        if category:
            params["category"] = category
        if min_price:
            params["min_price"] = min_price
            
        response = requests.get(f"{self.base_url}/books", params=params)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_stats(self) -> dict:
        """Busca estatísticas gerais"""
        response = requests.get(f"{self.base_url}/stats/overview")
        response.raise_for_status()
        return response.json()
    
    def get_categories(self) -> dict:
        """Lista todas as categorias"""
        response = requests.get(f"{self.base_url}/categories")
        response.raise_for_status()
        return response.json()

# Instanciar cliente
api = BooksAPI()

# Exemplo de uso
df = api.get_books(size=1000)
stats = api.get_stats()
categories = api.get_categories()

print(f"Total de livros carregados: {len(df)}")
print(f"Estatísticas gerais: {stats}")
print(f"Categorias disponíveis: {len(categories)}")
```

### 5.4 Pipeline de Dados para ML

```python
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# 1. Carregar dados da API
api = BooksAPI()
df = api.get_books(size=10000)

# 2. Preparação para ML
# Features numéricas
numeric_features = ['price', 'stock', 'rating']

# Encoding de categorias
le_category = LabelEncoder()
df['category_encoded'] = le_category.fit_transform(df['category'])

# Features derivadas
df['price_per_star'] = df['price'] / df['rating']
df['in_stock'] = (df['stock'] > 0).astype(int)

# 3. Split treino/teste
X = df[['price', 'stock', 'rating', 'category_encoded', 'price_per_star']]
y = df['in_stock']  # Exemplo: prever disponibilidade

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Dados de treino: {X_train.shape}")
print(f"Dados de teste: {X_test.shape}")
```

### 5.5 Casos de Uso Práticos

#### 5.5.1 Recomendação de Preços

```python
"""
Análise: Qual o preço ideal para um livro de determinada categoria?
"""
import numpy as np

# Buscar livros de uma categoria
category = 'Fiction'
response = requests.get(
    f"{API_URL}/books",
    params={"category": category, "size": 1000}
)
fiction_books = pd.DataFrame(response.json())

# Análise estatística
price_stats = fiction_books['price'].describe()
print(f"\nEstatísticas de preço para {category}:")
print(f"Média: £{price_stats['mean']:.2f}")
print(f"Mediana: £{price_stats['50%']:.2f}")
print(f"Percentil 75: £{price_stats['75%']:.2f}")

# Correlação rating x preço
correlation = fiction_books[['price', 'rating']].corr()
print(f"\nCorrelação preço x rating: {correlation.iloc[0,1]:.2f}")
```

#### 5.5.2 Análise de Estoque

```python
"""
Análise: Categorias com maior risco de falta de estoque
"""
# Buscar estatísticas por categoria
response = requests.get(f"{API_URL}/stats/categories")
category_stats = response.json()

# Calcular média de estoque por categoria
stock_by_category = pd.DataFrame([
    {
        'category': cat,
        'avg_stock': stats['average_stock'],
        'total_books': stats['total_books']
    }
    for cat, stats in category_stats.items()
])

# Ordenar por menor estoque médio
low_stock = stock_by_category.sort_values('avg_stock').head(10)
print("Categorias com menor estoque médio:")
print(low_stock)
```

#### 5.5.3 Segmentação de Clientes

```python
"""
Análise: Agrupar livros por perfil de cliente
"""
from sklearn.cluster import KMeans

# Preparar features
X = books[['price', 'rating']].fillna(0)

# Aplicar K-means
kmeans = KMeans(n_clusters=3, random_state=42)
books['segment'] = kmeans.fit_predict(X)

# Analisar segmentos
segment_analysis = books.groupby('segment').agg({
    'price': ['mean', 'min', 'max'],
    'rating': 'mean',
    'id': 'count'
})

print("\nSegmentos de livros:")
print(segment_analysis)

# Nomear segmentos
segment_names = {
    0: 'Econômico',
    1: 'Premium',
    2: 'Popular'
}
books['segment_name'] = books['segment'].map(segment_names)
```

---

## 6. Plano de Integração com Modelos de ML

### 6.1 Arquitetura ML Proposta

```
┌─────────────────────────────────────────────────────┐
│                  DADOS (API)                        │
│  GET /api/v1/books → DataFrame                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              FEATURE ENGINEERING                    │
│  • Encoding de categorias                           │
│  • Normalização de preços                           │
│  • Features derivadas                               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              TREINAMENTO DE MODELO                  │
│  • Train/Test Split                                 │
│  • Validação Cruzada                                │
│  • Otimização de Hiperparâmetros                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              MODELO TREINADO                        │
│  • Salvar como pickle/joblib                        │
│  • Versionamento do modelo                          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              DEPLOY DO MODELO                       │
│  • Endpoint /api/v1/ml/predict                      │
│  • Carregamento do modelo na inicialização          │
│  • Inferência em tempo real                         │
└─────────────────────────────────────────────────────┘
```

### 6.2 Casos de Uso de ML

#### 6.2.1 Sistema de Recomendação

**Objetivo:** Recomendar livros similares baseado em características

```python
# models/recommendation.py

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import numpy as np

class BookRecommender:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.model = None
        self.scaler = StandardScaler()
        self.books_data = None
        
    def fit(self):
        """Treina o modelo de recomendação"""
        # Carregar dados
        response = requests.get(f"{self.api_url}/books", params={"size": 10000})
        self.books_data = pd.DataFrame(response.json())
        
        # Features para similaridade
        features = ['price', 'rating', 'category_encoded', 'stock']
        
        # Encoding
        le = LabelEncoder()
        self.books_data['category_encoded'] = le.fit_transform(
            self.books_data['category']
        )
        
        # Normalização
        X = self.books_data[features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Treinar KNN
        self.model = NearestNeighbors(n_neighbors=6, metric='cosine')
        self.model.fit(X_scaled)
        
    def recommend(self, book_id: int, n: int = 5):
        """Recomenda N livros similares"""
        # Encontrar índice do livro
        idx = self.books_data[self.books_data['id'] == book_id].index[0]
        
        # Encontrar vizinhos mais próximos
        distances, indices = self.model.kneighbors(
            self.scaler.transform([self.books_data.iloc[idx][features]]),
            n_neighbors=n+1
        )
        
        # Retornar livros similares (exceto o próprio)
        recommendations = self.books_data.iloc[indices[0][1:]].copy()
        recommendations['similarity_score'] = 1 - distances[0][1:]
        
        return recommendations[['id', 'title', 'category', 'price', 'similarity_score']]

# Uso
recommender = BookRecommender("http://localhost:8000/api/v1")
recommender.fit()
similar_books = recommender.recommend(book_id=1, n=5)
print(similar_books)
```

#### 6.2.2 Predição de Rating

**Objetivo:** Prever a avaliação de um livro baseado em suas características

```python
# models/rating_predictor.py

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, r2_score

class RatingPredictor:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.feature_names = []
        
    def prepare_features(self, df: pd.DataFrame):
        """Prepara features para o modelo"""
        # Features numéricas
        df['price_range'] = pd.cut(df['price'], bins=5, labels=False)
        df['stock_level'] = pd.cut(df['stock'], bins=3, labels=False)
        
        # Encoding de categoria
        le = LabelEncoder()
        df['category_encoded'] = le.fit_transform(df['category'])
        
        # Features finais
        self.feature_names = ['price', 'stock', 'category_encoded', 
                             'price_range', 'stock_level']
        
        return df[self.feature_names].fillna(0)
    
    def train(self):
        """Treina o modelo"""
        # Carregar dados
        response = requests.get(f"{self.api_url}/books", params={"size": 10000})
        df = pd.DataFrame(response.json())
        
        # Preparar features e target
        X = self.prepare_features(df)
        y = df['rating']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Treinar
        self.model.fit(X_train, y_train)
        
        # Avaliar
        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"RMSE: {rmse:.2f}")
        print(f"R²: {r2:.2f}")
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nImportância das features:")
        print(importance)
        
        return self.model
    
    def predict(self, book_data: dict):
        """Prediz rating para um novo livro"""
        df = pd.DataFrame([book_data])
        X = self.prepare_features(df)
        prediction = self.model.predict(X)[0]
        return round(prediction)

# Uso
predictor = RatingPredictor("http://localhost:8000/api/v1")
predictor.train()

# Prever rating de novo livro
new_book = {
    'price': 25.99,
    'stock': 15,
    'category': 'Fiction'
}
predicted_rating = predictor.predict(new_book)
print(f"Rating previsto: {predicted_rating}")
```

#### 6.2.3 Classificação de Categorias

**Objetivo:** Classificar automaticamente livros em categorias baseado no título e descrição

```python
# models/category_classifier.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

class CategoryClassifier:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('clf', MultinomialNB())
        ])
        
    def train(self):
        """Treina classificador de categorias"""
        # Carregar dados
        response = requests.get(f"{self.api_url}/books", params={"size": 10000})
        df = pd.DataFrame(response.json())
        
        # Combinar título e descrição
        df['text'] = df['title'] + ' ' + df['description'].fillna('')
        
        # Preparar dados
        X = df['text']
        y = df['category']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Treinar
        self.pipeline.fit(X_train, y_train)
        
        # Avaliar
        accuracy = self.pipeline.score(X_test, y_test)
        print(f"Acurácia: {accuracy:.2%}")
        
        return self.pipeline
    
    def predict(self, title: str, description: str = ""):
        """Prediz categoria de um livro"""
        text = f"{title} {description}"
        prediction = self.pipeline.predict([text])[0]
        probas = self.pipeline.predict_proba([text])[0]
        
        # Top 3 categorias mais prováveis
        top_indices = np.argsort(probas)[-3:][::-1]
        top_categories = [
            (self.pipeline.classes_[i], probas[i]) 
            for i in top_indices
        ]
        
        return {
            'predicted_category': prediction,
            'top_3_categories': top_categories
        }

# Uso
classifier = CategoryClassifier("http://localhost:8000/api/v1")
classifier.train()

result = classifier.predict(
    title="The Great Adventure",
    description="A thrilling journey through unknown lands"
)
print(result)
```

### 6.3 Endpoint ML na API

**Proposta de implementação:**

```python
# api/routes/ml.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib

router = APIRouter(prefix="/api/v1/ml", tags=["🤖 Machine Learning"])

# Carregar modelos treinados na inicialização
recommender = joblib.load('models/recommender.pkl')
rating_predictor = joblib.load('models/rating_predictor.pkl')
category_classifier = joblib.load('models/category_classifier.pkl')

class RecommendationRequest(BaseModel):
    book_id: int
    n_recommendations: int = 5

class RatingPredictionRequest(BaseModel):
    price: float
    stock: int
    category: str

class CategoryPredictionRequest(BaseModel):
    title: str
    description: str = ""

@router.post("/recommend")
def get_recommendations(request: RecommendationRequest):
    """Recomenda livros similares"""
    try:
        recommendations = recommender.recommend(
            request.book_id,
            request.n_recommendations
        )
        return recommendations.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-rating")
def predict_rating(request: RatingPredictionRequest):
    """Prediz rating de um livro"""
    try:
        rating = rating_predictor.predict(request.dict())
        return {"predicted_rating": rating}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify-category")
def classify_category(request: CategoryPredictionRequest):
    """Classifica categoria de um livro"""
    try:
        result = category_classifier.predict(
            request.title,
            request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Adicionar ao main.py:
# app.include_router(ml.router)
```

### 6.4 Pipeline de Treinamento Contínuo

```python
# scripts/train_models.py

"""
Script para treinar todos os modelos de ML
Deve ser executado periodicamente para atualizar os modelos
"""

import joblib
from datetime import datetime
import os

def train_all_models(api_url: str):
    """Treina todos os modelos e salva"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)
    
    print("=" * 50)
    print("TREINAMENTO DE MODELOS ML")
    print("=" * 50)
    
    # 1. Sistema de Recomendação
    print("\n1. Treinando Sistema de Recomendação...")
    recommender = BookRecommender(api_url)
    recommender.fit()
    joblib.dump(recommender, f'{models_dir}/recommender.pkl')
    print("✓ Salvo: recommender.pkl")
    
    # 2. Preditor de Rating
    print("\n2. Treinando Preditor de Rating...")
    rating_predictor = RatingPredictor(api_url)
    rating_predictor.train()
    joblib.dump(rating_predictor, f'{models_dir}/rating_predictor.pkl')
    print("✓ Salvo: rating_predictor.pkl")
    
    # 3. Classificador de Categorias
    print("\n3. Treinando Classificador de Categorias...")
    category_classifier = CategoryClassifier(api_url)
    category_classifier.train()
    joblib.dump(category_classifier, f'{models_dir}/category_classifier.pkl')
    print("✓ Salvo: category_classifier.pkl")
    
    # Salvar metadados
    metadata = {
        'trained_at': timestamp,
        'api_url': api_url,
        'models': ['recommender', 'rating_predictor', 'category_classifier']
    }
    joblib.dump(metadata, f'{models_dir}/metadata.pkl')
    
    print("\n" + "=" * 50)
    print("TREINAMENTO CONCLUÍDO!")
    print("=" * 50)

if __name__ == "__main__":
    train_all_models("http://localhost:8000/api/v1")
```

### 6.5 Fluxo Completo: Dados → ML → Predição

```
┌────────────────────────────────────────────────────────┐
│  1. COLETA DE DADOS                                    │
│     • Scraper extrai dados do site                    │
│     • Dados salvos em CSV                              │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  2. PROCESSAMENTO                                      │
│     • Limpeza com process_data.py                      │
│     • Normalização de valores                          │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  3. API DISPONIBILIZA DADOS                            │
│     • FastAPI carrega CSV                              │
│     • Endpoints fornecem dados estruturados            │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  4. TREINAMENTO DE MODELOS                             │
│     • Scripts consomem API                             │
│     • Feature engineering aplicado                     │
│     • Modelos treinados e salvos                       │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  5. DEPLOY DE MODELOS                                  │
│     • Modelos carregados na API                        │
│     • Novos endpoints ML criados                       │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  6. INFERÊNCIA                                         │
│     • Clientes consomem endpoints ML                   │
│     • Predições em tempo real                          │
│     • Recomendações personalizadas                     │
└────────────────────────────────────────────────────────┘
```

---

## Conclusão

Este documento apresenta a arquitetura completa do projeto Books Web Scraping & API, desde a coleta de dados até as possibilidades de integração com modelos de Machine Learning.

### Pontos Fortes da Arquitetura Atual

✅ **Pipeline ETL Completo** - Ingestão, processamento e exposição de dados
✅ **API REST Robusta** - FastAPI com documentação automática
✅ **Modular e Organizado** - Separação clara de responsabilidades
✅ **Fácil Consumo** - Endpoints intuitivos e bem documentados
✅ **Pronto para ML** - Dados estruturados e acessíveis via API

### Próximos Passos Recomendados

1. **Curto Prazo**
   - Migração de CSV para PostgreSQL
   - Implementação de testes automatizados
   - CI/CD com GitHub Actions

2. **Médio Prazo**
   - Cache distribuído com Redis
   - Implementação dos modelos ML propostos
   - Monitoramento e observabilidade

3. **Longo Prazo**
   - Orquestração com Airflow
   - Arquitetura de microserviços
   - Escalabilidade horizontal com Kubernetes

---

**Documento criado por:** Vinícius Miranda
**Data:** 01/01/2025  
**Versão:** 1.0
