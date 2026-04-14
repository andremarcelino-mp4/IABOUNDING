# app/core/database.py
import os
import psycopg2
import requests
from typing import Optional
from pymongo import MongoClient
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# --- HELPERS ---
def get_clima(cidade: str = "São Paulo"):
    weather_key = os.getenv("WEATHER_KEY")
    if not weather_key: return "agradável"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={weather_key}&units=metric&lang=pt_br"
    try:
        response = requests.get(url).json()
        if response.get("cod") != 200: return "agradável"
        return f"{response['weather'][0]['description']}, {response['main']['temp']}°C"
    except: return "agradável"

# --- POSTGRESQL (SUPABASE/LOCAL) ---
def _get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require")
    )

# --- MONGODB (AUDITORIA) ---
def get_mongo_client():
    return MongoClient(os.getenv("MONGO_URL"))

# --- SUPABASE CLIENT ---
def iniciar_supabase() -> Optional[Client]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key: return None
    return create_client(url, key)

supabase = iniciar_supabase()