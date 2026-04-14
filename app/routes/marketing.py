from fastapi import APIRouter
from app.services.marketing_service import gerar_inteligencia_marketing

router = APIRouter()

@router.post("/refresh-ai")
async def atualizar_marketing():
    sucesso = gerar_inteligencia_marketing("Taboão da Serra")
    if sucesso:
        return {"status": "IA atualizada com sucesso no MongoDB"}
    return {"status": "Erro ao atualizar IA"}
