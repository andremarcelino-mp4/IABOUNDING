# app/routes/chatbot.py
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from app.services.ai_engine import gerar_resposta_gepeteco

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/gepeteco")
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@router.post("/perguntar")
async def responder(prompt: str = Form(...)):
    resposta = await gerar_resposta_gepeteco(prompt)
    return {"resposta": resposta}