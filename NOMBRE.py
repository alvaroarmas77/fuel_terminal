import socket
import ssl
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def rastro_de_sangre():
    target = "login.microsoftonline.com"
    tenant_id = os.getenv('AZURE_TENANT_ID')
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    
    print(f"--- DIAGNÓSTICO DE CONEXIÓN ÚNICO ---")
    
    # TEST 1: Conexión TCP pura (¿Llegamos a Microsoft?)
    print(f"1. Verificando alcance físico a {target}...")
    try:
        socket.create_connection((target, 443), timeout=5)
        print("   ✅ Puerto 443 abierto y alcanzable.")
    except Exception as e:
        print(f"   ❌ ERROR DE RED: No hay salida al puerto 443. Detalle: {e}")
        return

    # TEST 2: Negociación SSL/TLS (¿El entorno es compatible?)
    print("2. Verificando apretón de manos SSL/TLS...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((target, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                print(f"   ✅ TLS establecido. Versión: {ssock.version()}")
    except Exception as e:
        print(f"   ❌ ERROR DE SSL: Tu Python no puede negociar seguridad con Microsoft. Detalle: {e}")
        return

    # TEST 3: El veredicto de Microsoft (¿Qué dice el servidor realmente?)
    print("3. Solicitando respuesta oficial a Azure AD...")
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    try:
        res = requests.post(url, data=data, timeout=10)
        if res.status_code == 200:
            print("   ✅ ¡ÉXITO TOTAL! El problema no es la conexión, es la lógica interna de tu Crew.")
        else:
            print(f"   ❌ MICROSOFT RESPONDIÓ ERROR {res.status_code}:")
            print(f"   CÓDIGO INTERNO: {res.json().get('error')}")
            print(f"   DESCRIPCIÓN: {res.json().get('error_description')}")
    except Exception as e:
        print(f"   ❌ ERROR EN HTTP: {e}")

if __name__ == "__main__":
    rastro_de_sangre()