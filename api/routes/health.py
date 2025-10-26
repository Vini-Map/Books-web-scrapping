from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/health",
    tags=["health"]
)

@router.get("/", description="Verifica se a API está funcionando corretamente.")
def health():
    return {"status": "ok", "message": "API está rodando"}
