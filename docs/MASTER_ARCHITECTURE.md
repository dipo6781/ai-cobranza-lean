# 🏛️ MASTER ARCHITECTURE: AI-Cobranza-Lean SaaS

## 1. Visión General
SaaS bootstrapped de cobranza inteligente que utiliza IA (Groq/Llama-3) para generar mensajes de negociación. La arquitectura está diseñada para **maximizar el ROI** mediante una caché de templates (Normalización 3NF) que reduce los costos de API en ~80% para escenarios recurrentes, garantizando al mismo tiempo un aislamiento estricto de datos multi-tenant.

## 2. Fases del Proyecto
### Fase 1: Setup & Normalización de Datos (3NF)
- **Objetivo**: Estructura de base de datos escalable y segura.
- **Componentes**: Tablas `organizations`, `organization_members`, `message_templates`, `registros_cobranza`.
- **Impacto**: Permite el aislamiento de datos por cliente (multi-tenancy) y la reutilización de mensajes.

### Fase 2: Autenticación JWT y Multi-Tenancy en Backend
- **Objetivo**: Seguridad y aislamiento a nivel de API.
- **Componentes**: Dependencia `get_current_org_id` en FastAPI. Valida el token JWT de Supabase, extrae el `user_id` y consulta el `org_id` asociado.
- **Impacto Legal**: Garantiza que un usuario de la Empresa A nunca pueda acceder o generar datos de la Empresa B (Cumplimiento GDPR/Privacidad).

### Fase 3: Optimización de ROI (Caché de Templates)
- **Objetivo**: Minimizar costos de inferencia de IA y latencia.
- **Componentes**: Cálculo de hash SHA256 de los parámetros (`cliente_id` + `monto` + `dias_mora`). Búsqueda previa en `message_templates`.
- **Impacto Negocio**: Si el hash existe, devuelve el mensaje en ~50-100ms sin llamar a Groq. Si no, llama a Groq, guarda el nuevo template y lo devuelve.

## 3. Funciones Clave del Backend (`app/main.py`)
- `get_current_org_id`: Dependency injection que intercepta cada request protegido, valida el JWT y retorna el `org_id` o lanza un HTTP 401/403.
- `generar_mensaje_cobranza`: Endpoint principal. Ejecuta la lógica de pseudonimización, verificación de caché, fallback a Groq API y persistencia en Supabase.

## 4. Reglas de Seguridad y Legalidad
1. **Pseudonimización**: Nunca se envía el nombre real del cliente a la IA. Se usa `CLIENTE_{hash}`.
2. **Variables de Entorno**: `GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY` y `DATABASE_URL` deben residir exclusivamente en `.env`.
3. **PgBouncer Compatibility**: La conexión a Supabase requiere `statement_cache_size: 0` en SQLAlchemy para evitar errores de prepared statements.