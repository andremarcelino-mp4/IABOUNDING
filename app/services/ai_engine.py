# app/services/ai_engine.py
from groq import Groq
import os
from app.core.database import _get_connection, get_mongo_client, get_clima

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_contexto_ounce_ai():
    """Busca dados de todas as fontes para alimentar o cérebro da IA"""
    clima = get_clima("Embu das Artes") # Exemplo
    contexto = f"Clima atual: {clima}\n"
    
    # Busca SQL (Produtos e Vendas)
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT nome, estoque_sistema FROM produtos")
            for p in cur.fetchall():
                contexto += f"Estoque - {p[0]}: {p[1]} unidades\n"
                
    # Busca MongoDB (Logs de Marketing)
    m_client = get_mongo_client()
    db = m_client[os.getenv("MONGO_DB_NAME", "Oncinha")]
    col = db[os.getenv("MONGO_COLLECTION_NAME", "ofertas_ia")]
    for doc in col.find().limit(2):
        contexto += f"Última oferta gerada: {doc.get('frase_ia')}\n"
        
    return contexto

async def gerar_resposta_gepeteco(pergunta_usuario: str):
    contexto = get_contexto_ounce_ai()
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": f"Você é o analista OunceAI. Contexto atual: {contexto}"},
            {"role": "user", "content": pergunta_usuario}
        ]
    )
    return completion.choices[0].message.content