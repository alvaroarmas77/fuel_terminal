import os
import requests
from O365 import Account, MSGraphProtocol

def get_ms_account():
    # 1. Recuperación limpia (usando strip para evitar saltos de línea invisibles)
    client_id = os.getenv('AZURE_CLIENT_ID', '').strip()
    client_secret = os.getenv('AZURE_CLIENT_SECRET', '').strip()
    tenant_id = os.getenv('AZURE_TENANT_ID', '').strip()
    
    if not all([client_id, client_secret, tenant_id]):
        return None

    # 2. Obtención del Token (Copia exacta de la lógica funcional)
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    # IMPORTANTE: Estos campos deben ir en el cuerpo como x-www-form-urlencoded
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    try:
        # Usamos 'data=' para asegurar el formato de formulario que Azure requiere
        response = requests.post(token_url, data=token_data, timeout=10)
        
        if response.status_code != 200:
            # Esto te permitirá ver en el log de GitHub qué campo exacto rechaza Azure
            print(f"DEBUG: Error de Azure: {response.text}")
            return None
            
        token_response = response.json()
        
        # 3. Configuración de O365 inyectando el token
        protocol = MSGraphProtocol(tenant_id=tenant_id)
        account = Account(
            (client_id, client_secret), 
            protocol=protocol,
            tenant_id=tenant_id
        )
        
        # Forzamos el token obtenido manualmente en el backend de la librería
        account.con.token_backend.token = token_response
        
        return account
        
    except Exception as e:
        print(f"DEBUG: Error en flujo de autenticación: {str(e)}")
        return None