import os
from supabase import create_client, Client

# Configuración (Obtenida de Supabase Dashboard > Project Settings > API)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ixpxaphdhunfkpmlvcid.supabase.co")
# ⚠️ REEMPLAZA ESTO CON TU CLAVE service_role REAL (empieza con 'ey...')
SUPABASE_SERVICE_KEY=("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4cHhhcGhkaHVuZmtwbWx2Y2lkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTMxMTAwMCwiZXhwIjoyMDk2ODg3MDAwfQ.EaMcEmXFH3iPbZWJ-GEXxxkWHLHSyqqttc_9buIw_0o")
# Inicializar cliente con privilegios de administrador
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def seed_initial_data():
    print("🌱 Iniciando proceso de seed multi-tenant...")
    
    user_email = "admin@prueba-cobranza.com"
    user_password = "Password123!"
    print(f"→ Creando usuario: {user_email}")
    
    try:
        # Crear usuario y confirmar email automáticamente (gracias a la service_role key)
        auth_response = supabase.auth.admin.create_user({
            "email": user_email,
            "password": user_password,
            "email_confirm": True 
        })
        user_id = auth_response.user.id
        print(f"✅ Usuario creado con ID: {user_id}")
    except Exception as e:
        print(f"⚠️ Nota: {e}")
        print("→ Es posible que el usuario ya exista. Bórralo del Dashboard > Authentication > Users y vuelve a ejecutar.")
        return

    # Crear Organización
    org_name = "Cobranzas Demo S.A."
    print(f"→ Creando organización: {org_name}")
    org_response = supabase.table("organizations").insert({
        "name": org_name
    }).execute()
    org_id = org_response.data[0]["id"]
    print(f"✅ Organización creada con ID: {org_id}")

    # Vincular Usuario a la Organización como Admin
    print("→ Vinculando usuario a la organización como 'admin'...")
    supabase.table("organization_members").insert({
        "org_id": org_id,
        "user_id": user_id,
        "role": "admin"
    }).execute()
    print("✅ Vinculación completada.")

    print("\n🎉 ¡SEED COMPLETADO CON ÉXITO!")
    print(f"📧 Email de prueba: {user_email}")
    print(f"🔑 Password de prueba: {user_password}")
    print(f"🏢 Org ID generado: {org_id}")
    print("\n⚠️ IMPORTANTE: Guarda este Org ID para las pruebas.")

if __name__ == "__main__":
    seed_initial_data()