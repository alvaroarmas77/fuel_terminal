from O365 import Account, MsalAuthentication
import os

def get_ms_account():
    # 1. MAPE O DUAL: Busca prefijos AZURE_ o OUTLOOK_ para máxima compatibilidad
    client_id = os.getenv('AZURE_CLIENT_ID') or os.getenv('OUTLOOK_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET') or os.getenv('OUTLOOK_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID') or os.getenv('OUTLOOK_TENANT_ID')

    # Validación preventiva con log descriptivo
    if not all([client_id, client_secret, tenant_id]):
        print("ERROR: Faltan variables de entorno. Verifica que AZURE_CLIENT_ID, SECRET y TENANT_ID estén en los Secrets de GitHub.")
        return None

    credentials = (client_id, client_secret)
    
    # Scopes para Client Credentials (App-only)
    scopes = ['https://graph.microsoft.com/.default']

    try:
        # 2. CONFIGURACIÓN DE AUTENTICACIÓN MSAL
        auth = MsalAuthentication(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            scopes=scopes
        )
        
        # 3. INSTANCIA DE CUENTA: Inyectamos explícitamente el flujo de autenticación
        # Es vital pasar protocol_authentication=auth para que use el token de aplicación
        account = Account(
            credentials, 
            auth_flow_type='credentials', 
            tenant_id=tenant_id,
            protocol_authentication=auth
        )
        
        # Intento de autenticación con log de depuración
        if account.authenticate():
            return account
        else:
            print("ERROR_AUTH: Microsoft Graph rechazó las credenciales. Verifica que el 'Client Secret' no haya expirado y que sea el 'Value' y no el 'ID'.")
            return None
            
    except Exception as e:
        # Captura de errores técnicos (ej. errores de red, DNS o configuración de Azure)
        print(f"ERROR_CRÍTICO_GRAPH: {str(e)}")
        return None