# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.core.config import settings

# Importando todas as rotas que criamos
from app.routes import inventory, chatbot, marketing, camera

# Inicializa o FastAPI usando as configurações do seu config.py
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend completo do ecossistema OunceAI (SmartShelf)"
)

# Monta a pasta de arquivos estáticos (CSS, JS, Imagens da Oncinha)

try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except RuntimeError:
    print("⚠️ Pasta 'app/static' não encontrada. Crie-a para servir imagens e CSS.")

# --- REGISTRO DOS MÓDULOS (ROTEADORES) ---
app.include_router(inventory.router, prefix="/inventory", tags=["Gestão de Estoque"])
app.include_router(chatbot.router, prefix="/chat", tags=["Inteligência Artificial - Groq"])
app.include_router(marketing.router, prefix="/marketing", tags=["Automação de Vendas - Gemini"])
app.include_router(camera.router, prefix="/vision", tags=["Visão Computacional - YOLO"])

# --- ROTA RAIZ ---
@app.get("/", tags=["Sistema"])
async def root():
    """Redireciona a página principal direto para o Dashboard de Inventário"""
    return RedirectResponse(url="/inventory/dashboard")

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Endpoint para monitoramento de infraestrutura (útil para cloud)"""
    return {"status": "online", "system": settings.APP_NAME, "version": settings.APP_VERSION}