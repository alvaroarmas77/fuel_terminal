import os
from O365 import Account, FileSystemTokenBackend

def get_ms_account():
    # 1. DEFINICIÓN DE LA RUTA (Esto es lo que faltaba)
    # Asumiendo que este archivo está en: src/fuel_terminal_security_logistics_gatekeeper/utils/
    # Subimos dos niveles para llegar a la raíz donde está 'o365_token.txt'
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    client_id = '5666a19b-c616-43a9-8126-1eb9e31dbd67'
    credentials = (client_id, 'TOKEN_AUTH_ACTIVE') 

    scopes = [
        'https://graph.microsoft.com/Mail.Send',
        'https://graph.microsoft.com/Files.ReadWrite.All',
        'https://graph.microsoft.com/Calendars.ReadWrite',
        'https://graph.microsoft.com/Sites.ReadWrite.All',
        'https://graph.microsoft.com/User.Read.All'
    ]

    # 2. USO DE LA VARIABLE YA DEFINIDA
    token_backend = FileSystemTokenBackend(
        token_path=project_root, 
        token_filename='o365_token.txt'
    )

    try:
        account = Account(
            credentials, 
            token_backend=token_backend, 
            main_resource='https://graph.microsoft.com/v1.0'
        )
        
        # Intentar autenticar de forma silenciosa (usando el token)
        if account.authenticate(scopes=scopes):
            return account
        else:
            print("ERROR_AUTH: El token no es válido o ha expirado.")
            return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None