# 📜 DEV COMMAND LOG: Bitácora de Desarrollo y Decisiones

| Fecha/Hora (Ref) | Comando / Acción | Archivo Impactado | Resultado / Lección Aprendida |
| :--- | :--- | :--- | :--- |
| **Setup Inicial** | `python seed.py` | `seed.py` | **Error**: `NameError` por falta de comillas en la Service Key. **Solución**: Corregir sintaxis de string en Python. |
| **Config BD** | `python -m uvicorn app.main:app --reload` | `app/database.py` | **Error**: `DuplicatePreparedStatementError` de asyncpg. **Solución**: Agregar `connect_args={"statement_cache_size": 0}` para compatibilidad con PgBouncer de Supabase. |
| **Prueba Auth** | `python get_token.py` | `get_token.py`, `app/main.py` | **Error**: `Invalid API key`. **Causa**: Archivo duplicado en carpeta `app/` y uso de clave dummy. **Solución**: Unificar script en la raíz y usar la `anon` key real del Dashboard. |
| **Prueba Auth** | `curl.exe -X GET ... /test-auth` | `app/main.py` | **Éxito**: Endpoint temporal validó la extracción correcta de `user_id` y `org_id` desde el JWT. |
| **Optimización** | `python test_cache.py` | `app/main.py`, `.env` | **Error**: Advertencia `GROQ_API_KEY` no encontrada y modo `anonimizado_seguro...` (código viejo). **Causa**: Typo en `.env` (`ROQ_API_KEY` en lugar de `GROQ_API_KEY`) y caché de Python (`__pycache__`). **Solución**: Corregir `.env`, limpiar `__pycache__` y reiniciar servidor. |
| **Validación Final**| `python test_cache.py` | `app/main.py` | **ÉXITO ROTUNDO**: <br>• Petición 1 (Cache Miss): ~11.5s (Generó y guardó).<br>• Petición 2 (Cache Hit): ~3.9s (Leyó de BD).<br>• **ROI**: Ahorro de tokens de IA confirmado. |