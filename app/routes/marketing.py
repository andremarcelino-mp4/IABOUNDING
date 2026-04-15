from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.services.marketing_service import gerar_inteligencia_marketing

router = APIRouter()

@router.post("/refresh-ai")
async def atualizar_marketing():
    sucesso = gerar_inteligencia_marketing("Taboão da Serra")
    if sucesso:
        return RedirectResponse(url="/inventory/dashboard?status=ia_atualizada", status_code=303)
    return RedirectResponse(url="/inventory/dashboard?status=erro_ia", status_code=303)
