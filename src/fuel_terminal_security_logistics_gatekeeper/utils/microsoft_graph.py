import os
from O365 import Account, MSGraphProtocol

def get_ms_account():
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    if not all([client_id, client_secret, tenant_id]):
        return None

    credentials = (client_id, client_secret)

    try:
        # Forzamos el protocolo al Tenant específico para validar el secreto empresarial
        protocol = MSGraphProtocol(tenant_id=tenant_id)
        
        account = Account(
            credentials, 
            auth_flow_type='credentials',
            tenant_id=tenant_id,
            protocol=protocol
        )
        
        if account.authenticate():
            return account
        return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA: {str(e)}")
        return None