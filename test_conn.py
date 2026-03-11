import os
from dotenv import load_dotenv
from utils.microsoft_graph import get_ms_account

# 1. Cargar el entorno
load_dotenv()

def diagnostic():
    print("--- 🔍 DIAGNÓSTICO DE CONEXIÓN MICROSOFT ---")
    
    # 2. Verificar lectura de variables
    # Probamos ambos nombres por si acaso
    cid = os.getenv('AZURE_CLIENT_ID') or os.getenv('OUTLOOK_CLIENT_ID')
    sec = os.getenv('AZURE_CLIENT_SECRET') or os.getenv('OUTLOOK_CLIENT_SECRET')
    ten = os.getenv('AZURE_TENANT_ID') or os.getenv('OUTLOOK_TENANT_ID')

    print(f"ID del Cliente encontrado: {'✅ SÍ' if cid else '❌ NO'}")
    print(f"Secreto encontrado: {'✅ SÍ' if sec else '❌ NO'}")
    print(f"Tenant ID encontrado: {'✅ SÍ' if ten else '❌ NO'}")

    if not cid or not sec or not ten:
        print("\n⚠️ ERROR: El script no puede leer tus variables. Revisa el archivo .env")
        return

    # 3. Intentar el "Apretón de Manos"
    print("\n⏳ Intentando autenticación con Microsoft Graph...")
    account = get_ms_account()

    if account:
        try:
            # Prueba de fuego: ¿Podemos ver el OneDrive?
            drive = account.storage().get_default_drive()
            print(f"✅ CONEXIÓN EXITOSA. Drive encontrado: {drive.name}")
        except Exception as e:
            print(f"❌ ERROR DE PERMISOS: Conectó, pero no puede leer archivos. Detalle: {e}")
    else:
        print("❌ FALLO TOTAL: Las credenciales son incorrectas o no tienen permiso de aplicación.")

if __name__ == "__main__":
    diagnostic()