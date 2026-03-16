import os
from O365 import Account, FileSystemTokenBackend

def get_ms_account():
    # 1. Definimos la ruta absoluta (Evita el error NameError: project_root)
    project_root = os.getcwd() 

    # 2. Sincronización con tus nombres en GitHub
    # El segundo parámetro es el respaldo (ID referencial)
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    
    # El Secret NUNCA debe tener un respaldo hardcoded por seguridad
    client_secret = os.getenv('AZURE_CLIENT_SECRET') 

    if not client_secret or not client_secret:
        print("ERROR: Las variables de entorno de Azure no están cargadas correctamente.")
        return None

    credentials = (client_id, os.getenv('AZURE_CLIENT_SECRET'))

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
        
        # 3. Intentamos refrescar el token de forma silenciosa
        # Esto es lo que evita que el bot pida una URL en la consola de GitHub
        if account.connection.refresh_token():
            return account
        
        # 4. Intento final de autenticación con los scopes correctos
        scopes = [
            'https://graph.microsoft.com/Mail.Send',
            'https://graph.microsoft.com/Files.ReadWrite.All',
            'https://graph.microsoft.com/Calendars.ReadWrite',
            'https://graph.microsoft.com/Sites.ReadWrite.All',
            'https://graph.microsoft.com/User.Read.All'
        ]

        if account.authenticate(scopes=scopes):
            return account
        
        print("ERROR_AUTH: No se pudo validar el token ni refrescarlo.")
        return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None