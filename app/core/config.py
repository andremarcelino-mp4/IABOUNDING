from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # --- APP SETTINGS ---
    APP_NAME: str = "OunceAI Dashboard"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # --- POSTGRES (SUPABASE) ---
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SSLMODE: str = "require"

    # --- MONGODB ---
    MONGO_URL: str
    MONGO_DB_NAME: str = "Oncinha"
    MONGO_COLLECTION_NAME: str = "ofertas_ia"

    # --- SUPABASE API ---
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # --- AI & EXTERNAL APIS ---
    GROQ_API_KEY: str
    WEATHER_KEY: str = ""

    # Configuração para ler o arquivo .env automaticamente
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instância global para ser importada no projeto todo
settings = Settings()