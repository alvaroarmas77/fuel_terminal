import os
from O365 import Account, MSGraphProtocol

def get_ms_account():
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    if not all([client_id, client_secret, tenant_id]):
        return None

    credentials = (client_id, client_secret)
    
    # CRÍTICO: El protocolo debe conocer el Tenant antes de autenticar
    protocol = MSGraphProtocol(tenant_id=tenant_id)
    
    try:
        account = Account(
            credentials, 
            auth_flow_type='credentials',
            tenant_id=tenant_id,
            protocol=protocol
        )
        
        # El scope /.default es obligatorio para Application Permissions
        if account.authenticate(scope=['https://graph.microsoft.com/.default']):
            return account
        return None
    except Exception:
        return None