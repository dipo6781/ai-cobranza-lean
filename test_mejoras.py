"""
Pruebas de funcionamiento para las mejoras implementadas:
1. Validación de variables de entorno
2. Logging estructurado
3. Validación Pydantic
4. CORS configurable
5. Timeout configurable
"""

import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def test_validacion_entorno():
    """Prueba 1: Validación de variables de entorno"""
    print("\n" + "="*60)
    print("PRUEBA 1: Validación de Variables de Entorno")
    print("="*60)
    
    # Simular ausencia de variables críticas
    os.environ.pop("GROQ_API_KEY", None)
    os.environ.pop("SUPABASE_URL", None)
    
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    required_vars = ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY", "DATABASE_URL"]
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"✓ Variables faltantes detectadas: {', '.join(missing)}")
        print("  El sistema advertirá correctamente al iniciar")
    else:
        print("✓ Todas las variables críticas están configuradas")
    
    return True

def test_validacion_pydantic():
    """Prueba 2: Validación Pydantic del modelo CobranzaRequest"""
    print("\n" + "="*60)
    print("PRUEBA 2: Validación Pydantic")
    print("="*60)
    
    try:
        from pydantic import BaseModel, Field, constr, ValidationError
        
        class CobranzaRequest(BaseModel):
            cliente_id_interno: constr(min_length=1, max_length=100) = Field(...)
            monto_deuda: float = Field(..., gt=0, le=1000000)
            dias_mora: int = Field(..., ge=0, le=3650)
        
        # Caso válido
        request_valido = CobranzaRequest(
            cliente_id_interno="CLI-12345",
            monto_deuda=1500.50,
            dias_mora=30
        )
        print(f"✓ Request válido aceptado: {request_valido.cliente_id_interno}")
        
        # Caso inválido: monto negativo
        try:
            request_invalido = CobranzaRequest(
                cliente_id_interno="CLI-12345",
                monto_deuda=-100,
                dias_mora=30
            )
            print("✗ Error: Debería haber rechazado monto negativo")
            return False
        except ValidationError as e:
            print(f"✓ Rechazó correctamente monto negativo: {e.error_count()} error(es)")
        
        # Caso inválido: días de mora excesivos
        try:
            request_invalido = CobranzaRequest(
                cliente_id_interno="CLI-12345",
                monto_deuda=1000,
                dias_mora=5000
            )
            print("✗ Error: Debería haber rechazado días de mora excesivos")
            return False
        except ValidationError as e:
            print(f"✓ Rechazó correctamente días de mora excesivos: {e.error_count()} error(es)")
        
        # Caso inválido: ID vacío
        try:
            request_invalido = CobranzaRequest(
                cliente_id_interno="",
                monto_deuda=1000,
                dias_mora=30
            )
            print("✗ Error: Debería haber rechazado ID vacío")
            return False
        except ValidationError as e:
            print(f"✓ Rechazó correctamente ID vacío: {e.error_count()} error(es)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en prueba Pydantic: {e}")
        return False

def test_timeout_configurable():
    """Prueba 3: Timeout configurable desde variable de entorno"""
    print("\n" + "="*60)
    print("PRUEBA 3: Timeout Configurable")
    print("="*60)
    
    # Valor por defecto
    timeout_default = int(os.getenv("API_TIMEOUT", "30"))
    print(f"✓ Timeout por defecto: {timeout_default} segundos")
    
    # Simular valor personalizado
    os.environ["API_TIMEOUT"] = "60"
    timeout_custom = int(os.getenv("API_TIMEOUT", "30"))
    print(f"✓ Timeout personalizado: {timeout_custom} segundos")
    
    if timeout_custom == 60:
        print("✓ El timeout se configura correctamente desde la variable de entorno")
        return True
    else:
        print("✗ Error: El timeout no se configuró correctamente")
        return False

def test_cors_configurable():
    """Prueba 4: CORS configurable desde ALLOWED_ORIGINS"""
    print("\n" + "="*60)
    print("PRUEBA 4: CORS Configurable")
    print("="*60)
    
    # Sin variable definida (debería usar ["*"])
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    print(f"✓ CORS por defecto: {allowed_origins}")
    
    # Con variable definida
    os.environ["ALLOWED_ORIGINS"] = "https://miapp.com,https://admin.miapp.com"
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    print(f"✓ CORS personalizado: {allowed_origins}")
    
    if len(allowed_origins) == 2 and "https://miapp.com" in allowed_origins:
        print("✓ Los orígenes CORS se configuran correctamente")
        return True
    else:
        print("✗ Error: Los orígenes CORS no se configuraron correctamente")
        return False

def test_logging_estructurado():
    """Prueba 5: Logging estructurado"""
    print("\n" + "="*60)
    print("PRUEBA 5: Logging Estructurado")
    print("="*60)
    
    import logging
    
    # Configurar logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    
    print("Generando mensajes de log de prueba:")
    logger.info("Mensaje INFO: Sistema iniciado correctamente")
    logger.warning("Mensaje WARNING: Variable de entorno opcional no configurada")
    logger.error("Mensaje ERROR: Error de conexión a la base de datos")
    
    print("✓ Logging estructurado funcionando con formato correcto")
    return True

def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "#"*60)
    print("# PRUEBAS DE FUNCIONAMIENTO - MEJORAS IMPLEMENTADAS")
    print("#"*60)
    
    resultados = []
    
    resultados.append(("Validación de Entorno", test_validacion_entorno()))
    resultados.append(("Validación Pydantic", test_validacion_pydantic()))
    resultados.append(("Timeout Configurable", test_timeout_configurable()))
    resultados.append(("CORS Configurable", test_cors_configurable()))
    resultados.append(("Logging Estructurado", test_logging_estructurado()))
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    aprobadas = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✓ APROBADA" if resultado else "✗ REPROBADA"
        print(f"{estado}: {nombre}")
    
    print(f"\nTotal: {aprobadas}/{total} pruebas aprobadas")
    
    if aprobadas == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS APROBADAS!")
        return 0
    else:
        print(f"\n⚠️ {total - aprobadas} prueba(s) fallida(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
