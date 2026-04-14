from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import inventory # Importando o arquivo acima

app = FastAPI(title="OunceAI System")

# CSS e Imagens
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Inclui as rotas do inventário
app.include_router(inventory.router, prefix="/inventory", tags=["Gestão de Estoque"])

@app.get("/")
async def root():
    return {"status": "Oncinha Online", "check_dashboard": "/inventory/dashboard"}