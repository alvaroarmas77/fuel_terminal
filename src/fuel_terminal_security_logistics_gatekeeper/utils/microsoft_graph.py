import os
import requests
from O365 import Account, MSGraphProtocol

def get_ms_account():
    # Obtenemos las variables directamente del entorno inyectado por GitHub Actions
    # Usamos strip() solo para prevenir errores de pegado, pero priorizamos la lectura directa
    client_id = os.getenv('AZURE_CLIENT_ID', '').strip()
    client_secret = os.getenv('AZURE_CLIENT_SECRET', '').strip()
    tenant_id = os.getenv('AZURE_TENANT_ID', '').strip()
    
    if not all([client_id, client_secret, tenant_id]):
        print("DEBUG: Faltan variables de entorno de Azure. Verifica los Secrets de GitHub.")
        return None

    # 1. Obtener Token Manualmente (Técnica del proyecto que SI funciona)
    # Esto evita que la librería O365 falle por problemas de formato en el secreto
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    try:
        # Petición directa a Microsoft
        response = requests.post(token_url, data=token_data, timeout=10)
        
        if response.status_code != 200:
            print(f"DEBUG: Error de autenticación en Microsoft: {response.text}")
            return None
            
        token = response.json()
        
        # 2. Configurar O365 con el token ya obtenido
        # Usamos el protocolo MSGraph ya que es una aplicación de Azure
        protocol = MSGraphProtocol(tenant_id=tenant_id)
        account = Account((client_id, client_secret), protocol=protocol)
        
        # Inyectamos el token directamente en el backend de la conexión
        # Esto 'engaña' a la librería para que crea que ya se autenticó con éxito
        account.con.token_backend.token = token
        
        return account
        
    except Exception as e:
        print(f"DEBUG: Excepción en get_ms_account: {str(e)}")
        return None