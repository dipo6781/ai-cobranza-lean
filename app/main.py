import os
import json
import hashlib
from pathlib import Path
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from supabase import create_client

# Importar modelos y dependencias de la base de datos
from app.database import get_db, RegistroCobranza, MessageTemplate, OrganizationMember

# 1. Cargar variables de entorno
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

if not os.getenv("GROQ_API_KEY"):
    print("⚠️ ADVERTENCIA: No se encontró GROQ_API_KEY en el archivo .env")

# 2. Inicializar FastAPI
app = FastAPI(
    title="Sistema de Cobranza IA - MVP Lean",
    description="API Multi-tenant con Caché de Templates y Persistencia.",
    version="3.0.0"
)

# 3. Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://ai-cobranza-lean.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# CONFIGURACIÓN SUPABASE (Para validación JWT)
# ==========================================
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ixpxaphdhunfkpmlvcid.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4cHhhcGhkaHVuZmtwbWx2Y2lkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEzMTEwMDAsImV4cCI6MjA5Njg4NzAwMH0.EDv87IQ5DV5IrB4SUGgbdOmy3YI0-VTiWlDc4lzWCuU") # Asegúrate de que esté en tu .env
supabase_auth = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ==========================================
# MODELOS PYDANTIC
# ==========================================
class CobranzaRequest(BaseModel):
    cliente_id_interno: str
    monto_deuda: float
    dias_mora: int

# ==========================================
# DEPENDENCIA: AUTENTICACIÓN Y MULTI-TENANCY
# ==========================================
async def get_current_org_id(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Extrae el user_id del JWT y consulta el org_id en la BD."""
    token = authorization.replace("Bearer ", "")
    try:
        user = supabase_auth.auth.get_user(token)
        user_id = user.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido, expirado o no autorizado")

    result = await db.execute(
        select(OrganizationMember.org_id).where(OrganizationMember.user_id == user_id)
    )
    org_id = result.scalar_one_or_none()

    if not org_id:
        raise HTTPException(status_code=403, detail="Usuario sin organización asignada")
    
    return org_id

# ==========================================
# ENDPOINT DE SALUD
# ==========================================
@app.get("/")
def read_root():
    return {"status": "Sistema Activo", "version": "3.0.0-MultiTenant-Cache"}

# ==========================================
# ENDPOINT PRINCIPAL: GENERAR MENSAJE (CON CACHÉ)
# ==========================================
@app.post("/api/v1/generar-mensaje")
async def generar_mensaje_cobranza(
    request: CobranzaRequest, 
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_org_id) # Inyección automática del org_id
):
    """
    Genera mensaje de cobranza. Usa caché de templates si los parámetros coinciden.
    """
    # 1. PSEUDONIMIZACIÓN
    cliente_anonimo = f"CLIENTE_{hash(request.cliente_id_interno) % 10000}"
    
    # 2. CÁLCULO DEL HASH PARA LA CACHÉ (3NF)
    params_dict = {
        "cliente_id": request.cliente_id_interno,
        "monto": request.monto_deuda,
        "dias": request.dias_mora
    }
    params_hash = hashlib.sha256(json.dumps(params_dict, sort_keys=True).encode()).hexdigest()

    # 3. BÚSQUEDA EN CACHÉ (MessageTemplates)
    result = await db.execute(
        select(MessageTemplate).where(
            (MessageTemplate.org_id == org_id) & (MessageTemplate.params_hash == params_hash)
        )
    )
    cached_template = result.scalar_one_or_none()

    template_id = None
    if cached_template:
        # ¡AHORRO DE TOKENS! El mensaje ya existe para estos parámetros.
        respuesta_ia = cached_template.content
        template_id = cached_template.id
        modo = "cache_hit"
    else:
        # 4. LLAMADA A GROQ API (Solo si no hay caché)
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY no configurada")
                
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"}
            
            prompt_sistema = (
                "Eres un asistente de cobranza profesional, empático pero firme. "
                "REGLAS: 1) Nunca ofrezcas descuentos >15%. 2) Lenguaje profesional. "
                "3) Si hay problemas graves de salud/desempleo, responde: 'Entendemos su situación. Un asesor humano le contactará en 24h'."
            )
            prompt_usuario = (
                f"El {cliente_anonimo} tiene deuda de ${request.monto_deuda} con {request.dias_mora} días de mora. "
                f"Genera mensaje corto (máx 300 caracteres) para WhatsApp, ofreciendo plan de pago en 2 cuotas."
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(groq_url, headers=headers, json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}],
                    "temperature": 0.7, "max_tokens": 300
                }, timeout=30.0)
                response.raise_for_status()
                respuesta_ia = response.json()["choices"][0]["message"]["content"].strip()
                
        except Exception as e:
            respuesta_ia = f"Error de IA: {str(e)}"

        # 5. GUARDAR NUEVO TEMPLATE EN CACHÉ
        try:
            nuevo_template = MessageTemplate(
                org_id=org_id, params_hash=params_hash, content=respuesta_ia
            )
            db.add(nuevo_template)
            await db.flush() # Obtener el ID sin hacer commit aún
            template_id = nuevo_template.id
            modo = "cache_miss_generated"
        except Exception as e:
            print(f"ERROR AL GUARDAR TEMPLATE: {e}")

    # 6. PERSISTENCIA DEL REGISTRO DE COBRANZA
    try:
        nuevo_registro = RegistroCobranza(
            org_id=org_id, # Aislamiento estricto
            cliente_id_interno=request.cliente_id_interno,
            monto_deuda=request.monto_deuda,
            dias_mora=request.dias_mora,
            mensaje_generado=respuesta_ia,
            cliente_anonimo=cliente_anonimo,
            template_id=template_id # Vinculación 3NF
        )
        db.add(nuevo_registro)
        await db.commit()
        await db.refresh(nuevo_registro)
    except Exception as e:
        await db.rollback()
        print(f"ERROR AL GUARDAR REGISTRO: {e}")

    # 7. RESPUESTA FINAL
    return {
        "cliente_anonimo": cliente_anonimo,
        "mensaje_generado": respuesta_ia,
        "modo": modo, # "cache_hit" o "cache_miss_generated"
        "org_id": str(org_id)
    }