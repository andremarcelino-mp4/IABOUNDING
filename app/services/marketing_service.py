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
        prompt = f"""       # PERSONA
        Você é um Redator Publicitário Especialista em Neurovendas da OunceIA, focado em varejo de conveniência.
        # AÇÃO
        Sua tarefa é criar 3 frases de marketing altamente persuasivas e curtas para o produto selecionado. As frases devem alternar entre o apelo ao clima, a praticidade do momento ou o prazer do consumo imediato.
        # CONTEXTO
        - Produto: {p_nome} (Categoria: {p_cat})
        - Localização: {cidade}
        - Clima Atual: {clima_atual}
        O cenário é um mini-mercado autônomo SmartShelf. O objetivo é conectar o produto ao desejo atual do cliente, seja por causa do tempo lá fora, ou apenas pela vontade de um mimo ou lanche rápido.
         # INSTRUÇÃO
        1. Não se prenda apenas ao clima: use-o se fizer sentido, mas também explore gatilhos como "você merece", "praticidade para o seu dia" ou "energia rápida".
        2. Mantenha as frases curtas e diretas (máximo 12 a 15 palavras).
        3. Seja criativo: evite frases genéricas demais como "compre já". Tente algo que gere identificação.
        4. IMPORTANTE: Não use aspas e não numere a lista.
        # FORMATO
        Entregue as 5 frases em uma única linha, separadas exclusivamente por ponto e vírgula (;). 
        Exemplo: Frase um; Frase dois; Frase três"""
        
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
