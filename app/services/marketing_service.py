import os
import datetime
import random
import google.generativeai as genai
from app.core.config import settings
from app.core.database import _get_connection, get_mongo_client, get_clima

# Inicializa o Gemini usando as configurações centralizadas
if settings.GROQ_API_KEY: 
    genai.configure(api_key=os.getenv("GEMINI_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash') # Versão mais estável

def gerar_inteligencia_marketing(cidade: str):
    """Gera frases de neurovendas e salva no MongoDB"""
    clima_atual = get_clima(cidade)
    pacote_ofertas = []

    # 1. Busca produtos no SQL
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, categoria FROM produtos")
            produtos = cur.fetchall()

    # 2. Gera frases para cada produto
    for p_id, p_nome, p_cat in produtos:
        prompt = f"""
        Você é um Redator de Neurovendas da OunceIA. 
        Crie 3 frases curtas (máximo 15 palavras) para o produto {p_nome} ({p_cat}).
        Contexto: Cidade {cidade}, Clima {clima_atual}.
        Separe as frases por ponto e vírgula (;).
        """
        try:
            response = model.generate_content(prompt)
            frases = [f.strip() for f in response.text.split(";") if f.strip()]
            
            doc = {
                "produto_id": p_id,
                "nome": p_nome,
                "contexto": {"clima": clima_atual, "cidade": cidade},
                "frases": frases,
                "timestamp": datetime.datetime.now()
            }
            pacote_ofertas.append(doc)
        except Exception as e:
            print(f"Erro no produto {p_nome}: {e}")

    # 3. Salva no MongoDB
    if pacote_ofertas:
        m_client = get_mongo_client()
        db = m_client[settings.MONGO_DB_NAME]
        col = db[settings.MONGO_COLLECTION_NAME]
        col.delete_many({"contexto.cidade": cidade})
        col.insert_many(pacote_ofertas)
        return True
    return False