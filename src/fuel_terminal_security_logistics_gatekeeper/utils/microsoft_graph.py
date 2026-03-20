import os
from O365 import Account, MSGraphProtocol

def get_ms_account():
    # 1. Recuperación y limpieza de variables de entorno
    client_id = os.getenv('AZURE_CLIENT_ID', '').strip()
    client_secret = os.getenv('AZURE_CLIENT_SECRET', '').strip()
    tenant_id = os.getenv('AZURE_TENANT_ID', '').strip()
    
    if not all([client_id, client_secret, tenant_id]):
        print("DEBUG: Faltan variables de entorno de Azure. Verifica los Secrets de GitHub.")
        return None

    try:
        # 2. Configuración del Protocolo con el Tenant específico
        protocol = MSGraphProtocol(tenant_id=tenant_id)
        
        # 3. Configuración de la cuenta con flujo de 'credentials'
        # Se pasan las credenciales como una tupla (client_id, client_secret)
        credentials = (client_id, client_secret)
        
        account = Account(
            credentials, 
            protocol=protocol, 
            auth_flow_type='credentials', # CRÍTICO para GitHub Actions
            tenant_id=tenant_id
        )
        
        # 4. Autenticación automática
        # La librería gestiona internamente la obtención y refresco del token
        if account.authenticate():
            return account
        
        return None
        
    except Exception as e:
        print(f"DEBUG: Excepción en get_ms_account: {str(e)}")
        return None