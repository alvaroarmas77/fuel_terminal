import os
from O365 import Account, FileSystemTokenBackend

def get_ms_account():
    # 1. SOLUCIÓN AL NameError: Definimos project_root dinámicamente
    # Esto busca la carpeta raíz donde GitHub Actions pone el archivo o365_token.txt
    project_root = os.getcwd() 

    client_id = '5666a19b-c616-43a9-8126-1eb9e31dbd67'
    # Con el token físico, la contraseña no es necesaria, pero la estructura sí
    credentials = (client_id, 'TOKEN_AUTH_ACTIVE') 

    scopes = [
        'https://graph.microsoft.com/Mail.Send',
        'https://graph.microsoft.com/Files.ReadWrite.All',
        'https://graph.microsoft.com/Calendars.ReadWrite',
        'https://graph.microsoft.com/Sites.ReadWrite.All',
        'https://graph.microsoft.com/User.Read.All'
    ]

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
        
        # 2. SOLUCIÓN AL BLOQUEO DE URL: refresh_token() primero
        # Esto intenta usar la "llave de refresco" del archivo sin pedir interacción humana
        if account.connection.refresh_token():
            return account
        
        # 3. ÚLTIMO RECURSO: authenticate silencioso
        # Si esto falla, devuelve None en lugar de colgar el sistema pidiendo una URL
        if account.authenticate(scopes=scopes):
            return account
        else:
            print("ERROR_AUTH: El token no es válido o los scopes no coinciden.")
            return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None