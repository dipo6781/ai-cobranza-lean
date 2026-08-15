import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, constr
import httpx
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from supabase import create_client

# Importar modelos y dependencias de la base de datos
from app.database import get_db, RegistroCobranza, MessageTemplate, OrganizationMember

# ==========================================
# CONFIGURACIÓN DE LOGGING ESTRUCTURADO
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 1. Cargar variables de entorno
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Validación de variables críticas al inicio
REQUIRED_ENV_VARS = ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY", "DATABASE_URL"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    logger.warning(f"⚠️ ADVERTENCIA: Variables de entorno faltantes: {', '.join(missing_vars)}")
    logger.warning("El sistema puede no funcionar correctamente sin estas variables.")
elif not os.getenv("GROQ_API_KEY"):
    logger.warning("⚠️ ADVERTENCIA: No se encontró GROQ_API_KEY en el archivo .env")

# 2. Inicializar FastAPI
app = FastAPI(
    title="Sistema de Cobranza IA - MVP Lean",
    description="API Multi-tenant con Caché de Templates y Persistencia.",
    version="3.1.0"
)

# 3. Configuración CORS - Mejorado para producción
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
# Filtrar origenes vacíos
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

logger.info(f"Configurando CORS con orígenes permitidos: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ==========================================
# CONFIGURACIÓN DE SUPABASE
# ==========================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    logger.error("ERROR: SUPABASE_URL o SUPABASE_ANON_KEY no configuradas")
    raise ValueError("Faltan credenciales de Supabase")

supabase_auth = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ==========================================
# CONFIGURACIÓN DE TIMEOUTS
# ==========================================
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
logger.info(f"Timeout de API configurado: {API_TIMEOUT} segundos")

# ==========================================
# MODELOS PYDANTIC CON VALIDACIÓN
# ==========================================
class CobranzaRequest(BaseModel):
    """Modelo de solicitud con validación estricta de datos."""
    cliente_id_interno: constr(min_length=1, max_length=100) = Field(
        ..., 
        description="ID interno del cliente (1-100 caracteres)",
        examples=["CLI-12345"]
    )
    monto_deuda: float = Field(
        ..., 
        gt=0, 
        le=1000000,
        description="Monto de deuda (0 < monto <= 1,000,000)",
        examples=[1500.50]
    )
    dias_mora: int = Field(
        ..., 
        ge=0, 
        le=3650,
        description="Días de mora (0-3650 días)",
        examples=[30]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "cliente_id_interno": "CLI-12345",
                "monto_deuda": 1500.50,
                "dias_mora": 30
            }
        }

# ==========================================
# DEPENDENCIA: AUTENTICACIÓN Y MULTI-TENANCY
# ==========================================
async def get_current_org_id(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Extrae el user_id del JWT y consulta el org_id en la BD."""
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Intento de acceso con token mal formado")
        raise HTTPException(status_code=401, detail="Formato de autorización inválido")
    
    token = authorization.replace("Bearer ", "")
    try:
        user = supabase_auth.auth.get_user(token)
        user_id = user.user.id
        logger.debug(f"Usuario autenticado: {user_id}")
    except Exception as e:
        logger.warning(f"Error de autenticación: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido, expirado o no autorizado")

    result = await db.execute(
        select(OrganizationMember.org_id).where(OrganizationMember.user_id == user_id)
    )
    org_id = result.scalar_one_or_none()

    if not org_id:
        logger.warning(f"Usuario {user_id} sin organización asignada")
        raise HTTPException(status_code=403, detail="Usuario sin organización asignada")
    
    logger.debug(f"Usuario {user_id} pertenece a organización {org_id}")
    return org_id

# ==========================================
# ENDPOINT DE SALUD
# ==========================================
@app.get("/")
def read_root():
    return {"status": "Sistema Activo", "version": "3.1.0-MultiTenant-Cache-Secure"}

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
    Genera mensaje de cobranza usando IA con caché de templates.
    
    - **cliente_id_interno**: ID único del cliente (máx 100 caracteres)
    - **monto_deuda**: Monto adeudado (0 < monto <= 1,000,000)
    - **dias_mora**: Días de retraso en el pago (0-3650 días)
    
    Retorna un mensaje profesional para WhatsApp con opciones de pago.
    Usa caché para evitar llamadas redundantes a la API de IA.
    """
    logger.info(f"Solicitud de generación para cliente {request.cliente_id_interno[:10]}... | Deuda: ${request.monto_deuda} | Mora: {request.dias_mora} días")
    
    # 1. PSEUDONIMIZACIÓN
    cliente_anonimo = f"CLIENTE_{abs(hash(request.cliente_id_interno)) % 10000}"
    
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
        logger.info(f"CACHE HIT: Template encontrado para hash {params_hash[:16]}...")
    else:
        # 4. LLAMADA A GROQ API (Solo si no hay caché)
        logger.info(f"CACHE MISS: Generando nuevo mensaje para hash {params_hash[:16]}...")
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                logger.error("GROQ_API_KEY no configurada")
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
                }, timeout=float(API_TIMEOUT))
                response.raise_for_status()
                respuesta_ia = response.json()["choices"][0]["message"]["content"].strip()
                logger.info(f"IA generó respuesta exitosamente ({len(respuesta_ia)} caracteres)")
                
        except httpx.TimeoutException as e:
            logger.error(f"Timeout en llamada a Groq API: {str(e)}")
            respuesta_ia = "Error: La solicitud tardó demasiado. Por favor intente nuevamente."
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP en Groq API ({e.response.status_code}): {str(e)}")
            respuesta_ia = f"Error de comunicación con el servicio de IA: {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error inesperado en Groq API: {str(e)}", exc_info=True)
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
            logger.info(f"Nuevo template guardado en caché con ID {template_id}")
        except Exception as e:
            logger.error(f"ERROR AL GUARDAR TEMPLATE: {e}", exc_info=True)

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
        logger.info(f"Registro de cobranza persistido con ID {nuevo_registro.id}")
    except Exception as e:
        await db.rollback()
        logger.error(f"ERROR AL GUARDAR REGISTRO: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al guardar el registro de cobranza")

    # 7. RESPUESTA FINAL
    return {
        "cliente_anonimo": cliente_anonimo,
        "mensaje_generado": respuesta_ia,
        "modo": modo, # "cache_hit" o "cache_miss_generated"
        "org_id": str(org_id),
        "template_id": template_id
    }
    