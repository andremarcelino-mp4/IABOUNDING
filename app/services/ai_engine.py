# app/services/ai_engine.py
from groq import Groq
import os
from app.core.database import _get_connection, get_mongo_client, get_clima

# Recomendado: use o settings que criamos no core/config.py se possível
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_contexto_ounce_ai():
    """Busca dados de todas as fontes para alimentar o cérebro da IA"""
    clima = get_clima("Embu das Artes") 
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
        # Usando .get() para evitar erro se a chave não existir
        contexto += f"Última oferta gerada: {doc.get('frase_ia', 'Sem frases recentes')}\n"
        
    return contexto

async def gerar_resposta_gepeteco(pergunta_usuario: str):
    contexto = get_contexto_ounce_ai()
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system", 
                "content": f"""# PERSONA
Você é o Analista Especialista de Dados do Ecossistema OunceIA, focado em inteligência de varejo autônomo e monitoramento de inventário inteligente.

# AÇÃO
Sua tarefa é analisar o contexto integrado proveniente de fontes SQL e NoSQL para fornecer respostas precisas, insights de vendas e status técnico dos sensores aos usuários ou gestores do sistema.

# CONTEXTO
Você está operando dentro de um sistema de mini-mercado autônomo (SmartShelf), onde os dados de estoque, vendas recentes e logs de marketing via IA estão consolidados abaixo:
---
CONTEXTO INTEGRADO: {contexto}

# INSTRUÇÃO
1. Baseie suas respostas estritamente nos dados fornecidos no CONTEXTO.
2. Se o usuário perguntar sobre temperatura ou sensores, priorize os dados disponíveis no contexto.
3. Caso identifique estoque baixo ou algum valor discrepante, inclua um alerta breve.
4. Se a informação não estiver presente no contexto, informe educadamente que não possui esses dados no momento.

# FORMATO
Responda em português de forma profissional, direta e organizada. Use **negrito** para destacar valores ou nomes de produtos e utilize bullet points para listas."""
            },            
            {"role": "user", "content": pergunta_usuario}
        ]
    )
    return completion.choices[0].message.content
