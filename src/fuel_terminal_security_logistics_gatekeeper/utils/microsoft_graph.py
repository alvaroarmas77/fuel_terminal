import os
from O365 import Account
# Aquí está el cambio clave:
from O365.connection import MsalAuthentication 
# Nota: A veces es con mayúsculas 'MSALAuthentication', revisa tu versión.
# Si falla, intenta: from O365 import MSALAuthentication
def get_ms_account():
    client_id = os.getenv('AZURE_CLIENT_ID') or os.getenv('OUTLOOK_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET') or os.getenv('OUTLOOK_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID') or os.getenv('OUTLOOK_TENANT_ID')

    if not all([client_id, client_secret, tenant_id]):
        return None

    credentials = (client_id, client_secret)
    scopes = ['https://graph.microsoft.com/.default']

    try:
        auth = MsalAuthentication(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            scopes=scopes
        )
        
        # CAMBIO CLAVE: Especificar el recurso principal
        # Esto ayuda a la App a saber en qué buzón buscar el Excel y el Calendario
        account = Account(
            credentials, 
            auth_flow_type='credentials', 
            tenant_id=tenant_id,
            protocol_authentication=auth,
            main_resource='logistics@terminal-sur.com' # <--- Asegúrate que este sea el email dueño de los archivos
        )
        
        # Forzamos la obtención del token para validar la conexión antes de entregar la cuenta
        if auth.get_token():
            return account
        else:
            print("ERROR_TOKEN: Las credenciales son válidas pero no se pudo generar un token de acceso.")
            return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None