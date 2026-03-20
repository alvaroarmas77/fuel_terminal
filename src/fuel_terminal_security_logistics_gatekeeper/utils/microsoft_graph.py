import os
import requests
from O365 import Account, MSGraphProtocol

def get_ms_account():
    # Obtenemos las variables directamente del entorno inyectado por GitHub Actions
    client_id = os.getenv('AZURE_CLIENT_ID', '').strip()
    client_secret = os.getenv('AZURE_CLIENT_SECRET', '').strip()
    tenant_id = os.getenv('AZURE_TENANT_ID', '').strip()
    
    if not all([client_id, client_secret, tenant_id]):
        print("DEBUG: Faltan variables de entorno de Azure. Verifica los Secrets de GitHub.")
        return None

    # 1. Obtener Token Manualmente
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
            
        token_data_json = response.json()
        
        # 2. Configurar O365 con el modo 'credentials' explícito
        protocol = MSGraphProtocol(tenant_id=tenant_id)
        
        # CORRECCIÓN CRÍTICA: Añadimos auth_flow_type='credentials'
        # Sin esto, la cuenta asume que hay un usuario físico y fallará en las Tools.
        account = Account(
            (client_id, client_secret), 
            protocol=protocol, 
            auth_flow_type='credentials',
            tenant_id=tenant_id
        )
        
        # Inyectamos el token en el backend
        # O365 espera un diccionario con 'access_token' y otros campos que ya vienen en el JSON
        account.con.token_backend.token = token_data_json
        
        return account
        
    except Exception as e:
        print(f"DEBUG: Excepción en get_ms_account: {str(e)}")
        return None