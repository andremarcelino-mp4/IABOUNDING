from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from decimal import Decimal
from app.core.database import _get_connection

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
async def listar_produtos_view(request: Request):
    produtos = []
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, preco, estoque_sistema, categoria, codigo_de_barras FROM produtos ORDER BY id ASC")
            for r in cur.fetchall():
                produtos.append({"id": r[0], "nome": r[1], "preco": r[2], "estoque": r[3], "categoria": r[4], "codigo": r[5]})

    status_key = request.query_params.get("status")
    mensagens = {
        "ia_atualizada": "IA atualizada com sucesso!",
        "erro_ia": "Erro ao atualizar a IA. Verifique as credenciais e tente novamente."
    }
    mensagem = mensagens.get(status_key)
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "produtos": produtos, "mensagem": mensagem})

@router.post("/criar")
async def criar_produto_api(
    codigo: str = Form(...), nome: str = Form(...), categoria: str = Form(...),
    preco: str = Form(...), peso: int = Form(...), estoque: int = Form(...)
):

    preco_decimal = Decimal(preco.replace(',', '.'))
    
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO produtos (codigo_de_barras, nome, categoria, preco, peso_unitario_gramas, estoque_sistema) VALUES (%s, %s, %s, %s, %s, %s)",
                (codigo, nome, categoria, preco_decimal, peso, estoque)
            )
            conn.commit()
    return RedirectResponse(url="/inventory/dashboard", status_code=303)

@router.get("/deletar/{id_prod}")
async def deletar_produto_api(id_prod: int):
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM produtos WHERE id = %s", (id_prod,))
            conn.commit()
    return RedirectResponse(url="/inventory/dashboard", status_code=303)