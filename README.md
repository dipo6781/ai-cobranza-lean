# 🤖 AI-Cobranza Lean SaaS

Sistema de cobranza inteligente que utiliza IA (Groq/Llama-3) para generar mensajes de negociación personalizados. Diseñado como un SaaS bootstrapped con arquitectura multi-tenant y optimización de costos mediante caché de templates.

## 📋 Características Principales

- **IA para Generación de Mensajes**: Utiliza Groq API con modelo Llama-3 para crear mensajes de cobranza profesionales y empáticos
- **Caché de Templates (3NF)**: Reduce costos de API en ~80% reutilizando mensajes para escenarios recurrentes
- **Multi-Tenancy**: Aislamiento estricto de datos por organización mediante JWT y Supabase
- **Pseudonimización**: Nunca se envían datos reales de clientes a la IA
- **Persistencia Completa**: Todos los registros se guardan en PostgreSQL vía Supabase

## 🏗️ Arquitectura

El sistema sigue una arquitectura en 3 fases:

1. **Fase 1**: Setup & Normalización de Datos (3NF)
   - Tablas: `organizations`, `organization_members`, `message_templates`, `registros_cobranza`
   
2. **Fase 2**: Autenticación JWT y Multi-Tenancy
   - Validación de tokens JWT de Supabase
   - Inyección de `org_id` en cada request
   
3. **Fase 3**: Optimización de ROI (Caché de Templates)
   - Hash SHA256 de parámetros para caché
   - Fallback a Groq solo cuando no hay caché

## 🚀 Quick Start

### Prerrequisitos

- Python 3.9+
- Node.js 18+
- Docker y Docker Compose
- Cuenta en [Supabase](https://supabase.com)
- API Key de [Groq](https://groq.com)

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd ai-cobranza
```

### 2. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key

# Groq API
GROQ_API_KEY=tu-groq-api-key

# Base de datos (opcional, si usas conexión directa)
DATABASE_URL=postgresql://usuario:password@localhost:5432/cobranza_db
```

### 3. Instalar dependencias

#### Backend (Python)

```bash
pip install -r requirements.txt
```

#### Frontend (Node.js)

```bash
cd frontend
npm install
```

### 4. Levantar servicios con Docker

```bash
docker-compose up -d
```

Esto iniciará:
- PostgreSQL (puerto 5432)
- ChromaDB (puerto 8000)

### 5. Ejecutar migraciones de Supabase

Las migraciones se encuentran en `supabase/migrations/`. Aplícalas desde tu dashboard de Supabase o usando la CLI:

```bash
supabase db push
```

### 6. Iniciar el backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El API estará disponible en `http://localhost:8000`

### 7. Iniciar el frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## 📡 Endpoints de la API

### `GET /`
Verifica el estado del sistema.

**Respuesta:**
```json
{
  "status": "Sistema Activo",
  "version": "3.0.0-MultiTenant-Cache"
}
```

### `POST /api/v1/generar-mensaje`
Genera un mensaje de cobranza usando IA o caché.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Body:**
```json
{
  "cliente_id_interno": "CLI-12345",
  "monto_deuda": 1500.50,
  "dias_mora": 30
}
```

**Respuesta:**
```json
{
  "cliente_anonimo": "CLIENTE_8472",
  "mensaje_generado": "Estimado cliente, le recordamos su deuda pendiente de $1500.50. Ofrecemos plan de pago en 2 cuotas sin interés...",
  "modo": "cache_hit",
  "org_id": "uuid-de-la-organizacion"
}
```

## 🔐 Autenticación

El sistema utiliza JWT de Supabase para autenticación. Para obtener un token:

```bash
python get_token.py
```

Este script usa las credenciales de prueba (`admin@prueba-cobranza.com`) y retorna un token válido.

## 🧪 Scripts de Utilidad

- `get_token.py`: Obtiene token JWT para testing
- `seed.py`: Carga datos iniciales en la base de datos
- `test_cache.py`: Pruebas de la caché de templates

## 📁 Estructura del Proyecto

```
ai-cobranza/
├── app/                    # Backend FastAPI
│   ├── main.py            # Punto de entrada y endpoints
│   ├── database.py        # Modelos y configuración DB
│   └── check_env.py       # Verificación de entorno
├── frontend/              # Frontend React + TypeScript + Vite
│   ├── src/
│   ├── public/
│   └── package.json
├── supabase/              # Migraciones de base de datos
│   └── migrations/
├── scripts/               # Scripts de deployment y utilidades
│   ├── create-pr.sh
│   ├── deploy-to-prod.sh
│   └── new-feature.sh
├── docs/                  # Documentación técnica
│   ├── MASTER_ARCHITECTURE.md
│   └── DEV_COMMAND_LOG.md
├── docker-compose.yml     # Servicios Docker
├── requirements.txt       # Dependencias Python
└── .env                   # Variables de entorno (no commitear)
```

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web asíncrono
- **SQLAlchemy (async)** - ORM para base de datos
- **Supabase** - Backend as a Service (PostgreSQL + Auth)
- **Groq API** - Inferencia de IA con Llama-3
- **ChromaDB** - Base de datos vectorial (opcional)

### Frontend
- **React 18** - Librería UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **@supabase/supabase-js** - Cliente de Supabase

### Infraestructura
- **Docker** - Contenerización
- **PostgreSQL 15** - Base de datos relacional
- **Nginx** - Proxy reverso (producción)

## 🔒 Seguridad

1. **Pseudonimización**: Los datos de clientes se anonimizan antes de enviar a IA
2. **Aislamiento Multi-Tenant**: Cada organización solo accede a sus datos
3. **JWT Validation**: Todos los endpoints protegidos validan tokens
4. **Environment Variables**: Credenciales sensibles en `.env` (no commitear)

## 📄 Licencia

[Indicar licencia del proyecto]

## 🤝 Contribuir

1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Commit cambios: `git commit -m 'Add nueva funcionalidad'`
3. Push a la rama: `git push origin feature/nueva-funcionalidad`
4. Abrir Pull Request

Usar los scripts en `scripts/` para seguir el flujo de desarrollo establecido.

## 📞 Soporte

Para issues técnicos, abrir un issue en el repositorio o contactar al equipo de desarrollo.

---

**Versión**: 3.0.0-MultiTenant-Cache  
**Estado**: MVP Lean
