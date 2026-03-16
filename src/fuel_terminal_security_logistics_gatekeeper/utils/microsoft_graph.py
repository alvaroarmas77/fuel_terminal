import os
from O365 import Account

def get_ms_account():
    # 1. Captura de variables de entorno
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID') # Vital para permisos de aplicación
    
    if client_secret:
        print(f"DEBUG: Autenticando como Aplicación. Longitud del secreto: {len(client_secret)}") 
    else:
        print("DEBUG: ERROR - No se detectó AZURE_CLIENT_SECRET")

    # Credenciales para flujo de aplicación
    credentials = (client_id, client_secret)

    try:
        # CAMBIO CRÍTICO: Usamos auth_flow_type='credentials'
        # Esto no requiere token_backend ni interacción humana (ignora MFA)
        account = Account(
            credentials, 
            auth_flow_type='credentials',
            tenant_id=tenant_id,
            main_resource='https://graph.microsoft.com/v1.0'
        )
        
        # Intentamos autenticar la aplicación
        if account.authenticate():
            print("DEBUG: [OK] Autenticación de Aplicación exitosa.")
            return account
        
        print("ERROR_AUTH: Microsoft rechazó las credenciales de la aplicación.")
        return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None