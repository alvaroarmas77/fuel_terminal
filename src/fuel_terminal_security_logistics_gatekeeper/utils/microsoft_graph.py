import os
import requests
from O365 import Account, MSGraphProtocol

def get_ms_account():
    # Usamos strip() para limpiar cualquier residuo de caracteres invisibles de GitHub
    client_id = os.getenv('AZURE_CLIENT_ID', '').strip()
    client_secret = os.getenv('AZURE_CLIENT_SECRET', '').strip()
    tenant_id = os.getenv('AZURE_TENANT_ID', '').strip()
    
    if not all([client_id, client_secret, tenant_id]):
        print("DEBUG: Faltan variables de entorno de Azure.")
        return None

    # 1. Obtener Token Manualmente (Técnica comprobada en tu proyecto de referencia)
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    try:
        response = requests.post(token_url, data=token_data, timeout=10)
        if response.status_code != 200:
            print(f"DEBUG: Error de autenticación en Microsoft: {response.text}")
            return None
            
        token = response.json()
        
        # 2. Configurar O365 con el token obtenido
        protocol = MSGraphProtocol(tenant_id=tenant_id)
        account = Account((client_id, client_secret), protocol=protocol)
        
        # Inyectamos el token directamente para evitar que la librería intente re-autenticar
        account.con.token_backend.token = token
        
        return account
    except Exception as e:
        print(f"DEBUG: Excepción en get_ms_account: {str(e)}")
        return None