import os
from O365 import Account, MSGraphProtocol

def get_ms_account():
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    if not all([client_id, client_secret, tenant_id]):
        return None

    credentials = (client_id, client_secret)
    
    # El protocolo DEBE tener el tenant_id para que el Secret sea reconocido
    protocol = MSGraphProtocol(tenant_id=tenant_id)
    
    try:
        account = Account(
            credentials, 
            auth_flow_type='credentials',
            tenant_id=tenant_id,
            protocol=protocol
        )
        
        # En modo aplicación, el scope SIEMPRE debe ser /.default
        if account.authenticate(scope=['https://graph.microsoft.com/.default']):
            return account
        return None
    except Exception:
        return None