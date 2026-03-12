import os
import sys
import msal
import O365
from O365 import Account
print(f"DEBUG: Versión de O365: {getattr(O365, '__version__', 'Desconocida')}")
print(f"DEBUG: Directorio de O365: {dir(O365)}")
# --- BLOQUE DE IMPORTACIÓN UNIVERSAL ---
# Probamos todas las rutas posibles en un solo push para evitar fallos de versión
AuthClass = None
try:
    from O365 import MSALAuthentication as AuthClass
except ImportError:
    try:
        from O365 import MsalAuthentication as AuthClass
    except ImportError:
        try:
            from O365.connection import MSALAuthentication as AuthClass
        except ImportError:
            try:
                from O365.connection import MsalAuthentication as AuthClass
            except ImportError:
                print("ERROR CRÍTICO: No se pudo encontrar la clase de autenticación en O365.")

# --- FUNCIÓN DE CONEXIÓN ---
def get_ms_account():
    # Priorizamos variables AZURE, usamos OUTLOOK como backup
    client_id = os.getenv('AZURE_CLIENT_ID') or os.getenv('OUTLOOK_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET') or os.getenv('OUTLOOK_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID') or os.getenv('OUTLOOK_TENANT_ID')

    if not all([client_id, client_secret, tenant_id]):
        print("ERROR_CONFIG: Faltan variables de entorno (Client ID, Secret o Tenant ID).")
        return None

    if AuthClass is None:
        print("ERROR_IMPORT: La librería O365 no pudo cargar el módulo de autenticación.")
        return None

    credentials = (client_id, client_secret)
    scopes = ['https://graph.microsoft.com/.default']

    try:
        # Usamos la clase que logramos importar exitosamente
        auth = AuthClass(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            scopes=scopes
        )
        
        # Configuramos la cuenta con el flujo de credenciales (App-only)
        account = Account(
            credentials, 
            auth_flow_type='credentials', 
            tenant_id=tenant_id,
            protocol_authentication=auth,
            main_resource='logistics@terminal-sur.com' # Dueño de los archivos Excel y Calendario
        )
        
        # Intentamos obtener el token para validar que los permisos de Azure estén OK
        if auth.get_token():
            print(f"CONEXIÓN EXITOSA: Autenticado con {AuthClass.__name__}")
            return account
        else:
            print("ERROR_TOKEN: Credenciales válidas pero Azure rechazó la generación del token.")
            return None
            
    except Exception as e:
        # Captura errores de nombre de argumentos o fallos de red
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None