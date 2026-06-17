import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).parent / ".env"
print(f"📁 Buscando .env en: {env_path}")
print(f" ¿Existe el archivo?: {env_path.exists()}")
print()

load_dotenv(dotenv_path=env_path)

print(" Variables cargadas en Python:")
print(f"   GROQ_API_KEY = {os.getenv('GROQ_API_KEY', '❌ NO ENCONTRADA')}")
print(f"   SUPABASE_URL = {os.getenv('SUPABASE_URL', '❌ NO ENCONTRADA')}")
print(f"   SUPABASE_ANON_KEY = {os.getenv('SUPABASE_ANON_KEY', '❌ NO ENCONTRADA')[:20]}...")