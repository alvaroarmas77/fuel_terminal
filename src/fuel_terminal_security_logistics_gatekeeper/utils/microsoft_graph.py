from O365 import Account, MsalAuthentication
import os

def get_ms_account():
    # Recuperar variables de entorno de GitHub Secrets o .env
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')

    if not all([client_id, client_secret, tenant_id]):
        print("ERROR: Faltan variables de entorno de Azure (ID, Secret o Tenant).")
        return None

    credentials = (client_id, client_secret)
    
    # Definimos los permisos necesarios para leer y escribir en OneDrive/SharePoint
    # Files.ReadWrite.All es vital para que OrderManagementTool pueda guardar el Excel
    scopes = ['https://graph.microsoft.com/.default']

    try:
        # Usamos MsalAuthentication para un flujo de credenciales de cliente (App-only)
        # Esto es lo ideal para procesos automáticos como CrewAI en GitHub Actions
        auth = MsalAuthentication(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            scopes=scopes
        )
        
        account = Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)
        
        # En flujos de credenciales de cliente, authenticate() verifica la validez del token
        if account.authenticate():
            return account
        else:
            print("ERROR: La autenticación con Microsoft Graph falló.")
            return None
            
    except Exception as e:
        print(f"ERROR_AUTH_GRAPH: {str(e)}")
        return None