import os
import requests
from O365 import Account, MSGraphProtocol

def get_ms_account():
    # 1. Recuperación y limpieza de variables
    client_id = os.getenv('AZURE_CLIENT_ID', '').strip()
    client_secret = os.getenv('AZURE_CLIENT_SECRET', '').strip()
    tenant_id = os.getenv('AZURE_TENANT_ID', '').strip()
    
    if not all([client_id, client_secret, tenant_id]):
        return None

    # 2. Obtener Token Manualmente (Igual que en tu proyecto funcional)
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
        
        # 3. Configurar O365 inyectando el token obtenido
        protocol = MSGraphProtocol(tenant_id=tenant_id)
        # Usamos una estructura que no pida login interactivo
        account = Account(
            (client_id, client_secret), 
            protocol=protocol,
            tenant_id=tenant_id
        )
        
        # Inyectamos el token manualmente en el backend de la cuenta
        # Esto evita que la librería intente usar su propio flujo fallido
        account.con.token_backend.token = token
        
        return account
        
    except Exception as e:
        print(f"DEBUG: Excepción en microsoft_graph: {str(e)}")
        return None