import os
import sys
import msal
import O365
from O365 import Account, MSGraphProtocol

# --- BLOQUE DE IMPORTACIÓN DEFINITIVO ---
# En O365 2.0.36+, la autenticación se maneja preferentemente a través de la conexión base
try:
    from O365.connection import MSALAuthentication
except ImportError:
    # Fallback para algunas distribuciones específicas de entorno
    MSALAuthentication = getattr(O365.connection, 'MSALAuthentication', None)

def get_ms_account():
    """
    Configura la conexión con Microsoft Graph usando Client Credentials Flow.
    """
    # 1. Recuperación de variables (Prioridad Azure)
    client_id = os.getenv('AZURE_CLIENT_ID') or os.getenv('OUTLOOK_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET') or os.getenv('OUTLOOK_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID') or os.getenv('OUTLOOK_TENANT_ID')

    if not all([client_id, client_secret, tenant_id]):
        print("ERROR_CONFIG: Faltan variables críticas (Client ID, Secret o Tenant).")
        return None

    credentials = (client_id, client_secret)
    
    # 2. Configuración del Protocolo
    # Usamos MSGraphProtocol explícitamente para asegurar compatibilidad con gemini-3.1
    protocol = MSGraphProtocol(default_resource='logistics@terminal-sur.com')

    try:
        # 3. Inicialización de la Cuenta
        # En la versión 2.0.36, para Client Credentials, pasamos auth_flow_type
        account = Account(
            credentials, 
            auth_flow_type='credentials',
            tenant_id=tenant_id,
            protocol=protocol
        )

        # 4. Validación de Conexión
        # Esto fuerza a O365 a pedir el token inmediatamente para verificar permisos
        if account.connection.refresh_token():
            print(f"DEBUG: Conexión establecida con Microsoft Graph para {protocol.default_resource}")
            return account
        else:
            print("ERROR_AUTH: No se pudo obtener el token de acceso desde Azure.")
            return None

    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None