import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

# 1. Cargar el .env desde la raíz del proyecto
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en el archivo .env")

# 2. Configuración del motor asíncrono (OPTIMIZADO PARA PGBOUNCER DE SUPABASE)
# CRÍTICO: statement_cache_size=0 y prepared_statement_cache_size=0
# Esto evita el error "DuplicatePreparedStatementError" con PgBouncer en modo transaction
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# ==========================================
# 3. MODELOS DE DATOS (Multi-tenancy + Normalización 3NF)
# ==========================================

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrganizationMember(Base):
    __tablename__ = "organization_members"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, default="member")
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('org_id', 'user_id', name='uq_org_user'),)

class MessageTemplate(Base):
    __tablename__ = "message_templates"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    params_hash = Column(String, nullable=False) # Hash de: cliente_id + monto + dias_mora
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('org_id', 'params_hash', name='uq_org_template'),)

class RegistroCobranza(Base):
    __tablename__ = "registros_cobranza"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True) # Nullable para migración suave
    cliente_id_interno = Column(String, index=True)
    monto_deuda = Column(Float)
    dias_mora = Column(Integer)
    mensaje_generado = Column(String) # Se mantiene por compatibilidad, pero usaremos template_id
    cliente_anonimo = Column(String)
    template_id = Column(Integer, ForeignKey("message_templates.id", ondelete="SET NULL"), nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

# 4. Dependencia para obtener la sesión en FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session