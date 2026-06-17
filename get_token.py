from supabase import create_client, Client

# ⚠️ REEMPLAZA ESTA CLAVE CON TU ANON KEY REAL DE SUPABASE
# Debe ser la MISMA que usaste en main.py
SUPABASE_URL = "https://ixpxaphdhunfkpmlvcid.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4cHhhcGhkaHVuZmtwbWx2Y2lkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEzMTEwMDAsImV4cCI6MjA5Njg4NzAwMH0.EDv87IQ5DV5IrB4SUGgbdOmy3YI0-VTiWlDc4lzWCuU"

# Inicializar cliente
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_jwt_token():
    print("🔐 Obteniendo token JWT para admin@prueba-cobranza.com...")
    
    try:
        # Hacer login con las credenciales del usuario de prueba
        response = supabase.auth.sign_in_with_password({
            "email": "admin@prueba-cobranza.com",
            "password": "Password123!"
        })
        
        # Extraer el access_token
        access_token = response.session.access_token
        
        print("\n✅ ¡TOKEN OBTENIDO CON ÉXITO!")
        print("\n📋 COPIA ESTE TOKEN COMPLETO (empieza con 'eyJ...'):")
        print("-" * 80)
        print(access_token)
        print("-" * 80)
        
        return access_token
        
    except Exception as e:
        print(f"\n❌ Error al obtener el token: {e}")
        print("\n💡 Posibles causas:")
        print("   1. La clave anon es incorrecta o tiene espacios")
        print("   2. El usuario admin@prueba-cobranza.com no existe")
        print("   3. La contraseña es incorrecta")
        return None

if __name__ == "__main__":
    get_jwt_token()