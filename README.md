# 📚 Books API — FIAP Data Engineering Project

API pública e pipeline de dados que realiza **Web Scraping** do site [Books to Scrape](https://books.toscrape.com/) e disponibiliza informações completas sobre livros em uma **API REST com FastAPI**.

---

## 🧠 Visão Geral do Projeto

O objetivo deste projeto é construir um **pipeline completo de dados**, desde a **extração (web scraping)** até a **exposição via API**, com endpoints que permitem explorar, buscar e gerar estatísticas sobre livros.

O sistema segue a seguinte arquitetura:

```
[ Scraper ] → [ Processamento / Limpeza ] → [ Dataset CSV ] → [ API REST (FastAPI) ]
```

---

## 📂 Estrutura do Repositório

```
books-api/
├── api/
│   ├── main.py                # Ponto de entrada da API FastAPI
│   ├── routers/
│   │   ├── books.py           # Endpoints principais de livros
│   │   ├── categories.py      # Endpoints de categorias
│   │   ├── health.py          # Healthcheck
│   │   └── stats.py           # Endpoints de estatísticas e insights
│   ├── schemas.py             # Modelos Pydantic
│   └── utils.py               # Funções auxiliares
│
├── scripts/
│   ├── scraper.py             # Script de web scraping (Books to Scrape)
│   ├── process_data.py        # Limpeza e normalização dos dados
│
├── data/
│   ├── raw/                   # Dados brutos coletados
│   ├── processed/             # Dados limpos e prontos para API
│   └── books.csv              # Base principal usada pela API
│
├── requirements.txt           # Dependências do projeto
└── README.md                  # Este arquivo
```

---

## ⚙️ Instalação e Execução Local

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/seu-usuario/books-api.git
cd books-api
```

### 2️⃣ Criar ambiente virtual e instalar dependências

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3️⃣ Executar o Web Scraper

```bash
python scripts/scraper.py
```

> O script extrai automaticamente **todos os livros** do site e salva em `data/books.csv`.

### 4️⃣ Executar a API FastAPI

```bash
uvicorn api.main:app --reload
```

> Acesse a documentação interativa:
> - **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
> - **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🌐 Endpoints da API

### 🔹 Core Endpoints

| Método | Rota | Descrição |
|--------|------|------------|
| **GET** | `/api/v1/books` | Lista todos os livros da base (com paginação e filtros). |
| **GET** | `/api/v1/books/{id}` | Retorna os detalhes de um livro específico. |
| **GET** | `/api/v1/books/search?title=&category=` | Busca por título e/ou categoria. |
| **GET** | `/api/v1/categories` | Lista todas as categorias disponíveis. |
| **GET** | `/api/v1/health` | Verifica o status da API e conexão com o dataset. |

---

### 🔹 Endpoints Opcionais (Insights)

| Método | Rota | Descrição |
|--------|------|------------|
| **GET** | `/api/v1/stats/overview` | Mostra estatísticas gerais: total de livros, preço médio, distribuição de ratings. |
| **GET** | `/api/v1/stats/categories` | Mostra estatísticas por categoria. |
| **GET** | `/api/v1/books/top-rated` | Lista os livros com melhor avaliação. |
| **GET** | `/api/v1/books/price-range?min=&max=` | Filtra livros dentro de uma faixa de preço. |

---

## 📘 Exemplos de Uso

### 📖 Listar livros

```bash
GET /api/v1/books?page=1&size=3
```

**Resposta**
```json
[
  {
    "id": 1,
    "title": "A Light in the Attic",
    "price": 51.77,
    "stock": 22,
    "rating": 3,
    "category": "Poetry",
    "product_page_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
  }
]
```

---

### 🔍 Buscar por título

```bash
GET /api/v1/books/search?title=love
```

---

### 🏷️ Listar categorias

```bash
GET /api/v1/categories
```

**Resposta**
```json
{
  "Travel": 11,
  "Mystery": 30,
  "Fiction": 40,
  "Science": 28
}
```

---

### 📊 Estatísticas gerais

```bash
GET /api/v1/stats/overview
```

**Resposta**
```json
{
  "total_books": 1000,
  "average_price": 35.74,
  "average_rating": 3.8
}
```

---

## 🧩 Personalização do Swagger

O Swagger da API foi personalizado com:
- Tema escuro no título (“Books API — FIAP Data Engineering”)
- Descrição em português
- Rotas agrupadas por categoria (“📚 Livros”, “📊 Estatísticas”, “🩺 Saúde”)

---

## 🚀 Deploy

Para deploy em plataformas como **Render**, **Railway**, ou **Vercel (Serverless Python)**:

1. Suba este repositório para o GitHub.
2. Aponte seu serviço para o repositório.
3. Configure o comando de execução:
   ```
   uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```
4. Teste acessando:
   ```
   https://seuapp.onrender.com/docs
   ```

---

## 🧱 Tecnologias Utilizadas

- 🐍 **Python 3.11+**
- ⚡ **FastAPI** (backend REST)
- 🌐 **Requests + BeautifulSoup4** (web scraping)
- 📊 **Pandas** (processamento e análise)
- 🧰 **Uvicorn** (servidor ASGI)
- 🗖️ **CSV** como base de dados leve

---

## 📈 Próximos Passos

- Migrar de CSV para banco de dados relacional (PostgreSQL ou SQLite).
- Adicionar cache (Redis) para requisições frequentes.
- Criar agendamento automático para atualização de dados (GitHub Actions / Cron).
- Adicionar autenticação e limites de uso.

---

## 👨‍💻 Autor

**Vinícius Miranda**  
📍 Projeto acadêmico — FIAP Data Engineering  
💡 Contato: [LinkedIn]((https://www.linkedin.com/in/vinipiovesan))

---

## 📜 Licença

MIT License — Livre para uso e modificação, com créditos ao autor original.
