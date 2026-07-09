# AI-Cobranza MVP

Sistema de cobranza inteligente con IA multi-tenant.

## Requisitos previos

- Docker y Docker Compose
- Node.js 20+ (para desarrollo local)
- Python 3.11+ (para desarrollo local)
- Cuenta en Supabase
- API Key de Groq

## Configuración de variables de entorno

### Backend (.env)

```bash
cp .env.example .env
```

Edita `.env` y configura:
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `GROQ_API_KEY`: Tu API key de Groq
- `SUPABASE_URL`: URL de tu proyecto Supabase
- `SUPABASE_ANON_KEY`: Clave anónima de Supabase
- `ALLOWED_ORIGINS`: Orígenes permitidos para CORS (separados por coma)

### Frontend (frontend/.env)

```bash
cp frontend/.env.example frontend/.env
```

Edita `frontend/.env` y configura:
- `VITE_SUPABASE_URL`: URL de tu proyecto Supabase
- `VITE_SUPABASE_ANON_KEY`: Clave anónima de Supabase
- `VITE_BACKEND_URL`: URL del backend (por defecto: http://localhost:8000/api/v1)

## Ejecución con Docker (Recomendado)

```bash
# Construir y levantar todos los servicios
docker-compose up --build

# Acceder al frontend: http://localhost:5173
# Acceder al backend: http://localhost:8000
# Base de datos: localhost:5432
```

## Ejecución en desarrollo local

### Backend

```bash
cd /workspace
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Estructura del proyecto

```
/workspace
├── app/                    # Backend FastAPI
│   ├── main.py            # Punto de entrada
│   └── database.py        # Modelos y configuración DB
├── frontend/              # Frontend React + Vite
│   ├── src/
│   │   └── App.tsx       # Componente principal
│   └── .env.example      # Variables de entorno frontend
├── docker-compose.yml     # Configuración Docker
├── Dockerfile.backend     # Dockerfile backend
├── Dockerfile.frontend    # Dockerfile frontend
├── .env.example          # Variables de entorno backend
└── requirements.txt       # Dependencias Python
```

## Características

- ✅ Autenticación con Supabase
- ✅ Multi-tenancy con aislamiento de datos por organización
- ✅ Caché de templates para ahorrar tokens de IA
- ✅ CORS configurable para producción
- ✅ Dockerizado para fácil despliegue

## Solución de problemas

### Error de CORS en producción

Asegúrate de configurar `ALLOWED_ORIGINS` en el `.env` del backend con la URL de tu frontend en producción.

Ejemplo: `ALLOWED_ORIGINS=https://mi-app.vercel.app,http://localhost:5173`

### Error de conexión a la base de datos

Verifica que:
1. El servicio de PostgreSQL esté corriendo
2. La `DATABASE_URL` sea correcta
3. Los puertos no estén siendo usados por otros servicios

### Error de autenticación

Verifica que las credenciales de Supabase sean correctas y que el usuario exista en la tabla `organization_members`.
