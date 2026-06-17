import time
import httpx
from supabase import create_client, Client

# ==========================================
# CONFIGURACIÓN
# ==========================================
SUPABASE_URL = "https://ixpxaphdhunfkpmlvcid.supabase.co"
# ⚠️ REEMPLAZA CON TU ANON KEY REAL DE SUPABASE
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4cHhhcGhkaHVuZmtwbWx2Y2lkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEzMTEwMDAsImV4cCI6MjA5Njg4NzAwMH0.EDv87IQ5DV5IrB4SUGgbdOmy3YI0-VTiWlDc4lzWCuU"

BACKEND_URL = "http://127.0.0.1:8000/api/v1/generar-mensaje"

# Credenciales del usuario de prueba
TEST_EMAIL = "admin@prueba-cobranza.com"
TEST_PASSWORD = "Password123!"

# Datos de prueba para la cobranza
TEST_PAYLOAD = {
    "cliente_id_interno": "CLI-001",
    "monto_deuda": 1500.50,
    "dias_mora": 30
}

# ==========================================
# FUNCIONES
# ==========================================
def get_jwt_token():
    """Obtiene un token JWT fresco de Supabase."""
    print("🔐 Obteniendo token JWT...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        token = response.session.access_token
        print("✅ Token obtenido correctamente\n")
        return token
    except Exception as e:
        print(f"❌ Error al obtener token: {e}")
        return None

def test_endpoint(token, request_number):
    """Hace una petición POST al endpoint y mide el tiempo."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"--- PETICIÓN #{request_number} ---")
    start_time = time.time()
    
    try:
        with httpx.Client() as client:
            response = client.post(BACKEND_URL, headers=headers, json=TEST_PAYLOAD, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        
        print(f"⏱️  Tiempo: {elapsed_ms:.2f} ms")
        print(f"🎯 Modo: {result.get('modo', 'N/A')}")
        print(f"💬 Mensaje: {result.get('mensaje_generado', 'N/A')[:100]}...")
        print()
        
        return result, elapsed_ms
        
    except Exception as e:
        print(f"❌ Error en petición: {e}\n")
        return None, 0

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
def main():
    print("=" * 70)
    print("🚀 PRUEBA DE CACHÉ DE TEMPLATES - DEMOSTRACIÓN DE ROI")
    print("=" * 70)
    print()
    
    # 1. Obtener token
    token = get_jwt_token()
    if not token:
        return
    
    # 2. Primera petición (esperamos cache_miss)
    result1, time1 = test_endpoint(token, 1)
    if not result1:
        return
    
    # 3. Segunda petición (esperamos cache_hit)
    result2, time2 = test_endpoint(token, 2)
    if not result2:
        return
    
    # 4. Análisis de resultados
    print("=" * 70)
    print("📊 ANÁLISIS DE RENDIMIENTO")
    print("=" * 70)
    print(f"Petición #1 (cache_miss): {time1:.2f} ms - Modo: {result1.get('modo')}")
    print(f"Petición #2 (cache_hit):  {time2:.2f} ms - Modo: {result2.get('modo')}")
    print()
    
    if time1 > 0:
        speedup = time1 / time2 if time2 > 0 else 0
        print(f"⚡ Mejora de velocidad: {speedup:.1f}x más rápido")
        print(f"💰 Ahorro de tokens de IA: {'SÍ' if result2.get('modo') == 'cache_hit' else 'NO'}")
    
    print()
    print("✅ PRUEBA COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    main()