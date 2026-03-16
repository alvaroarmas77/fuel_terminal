import os
from O365 import Account, FileSystemTokenBackend

def get_ms_account():
    # 1. Definimos la ruta absoluta (Evita el error NameError: project_root)
    project_root = os.getcwd() 

    # 2. Sincronización con tus nombres en GitHub
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    
    # Verificación de seguridad y longitud corregida
    if client_secret:
        print(f"DEBUG: Longitud del secreto detectada: {len(client_secret)}") 
    else:
        print("DEBUG: ERROR - El secreto AZURE_CLIENT_SECRET no se detectó (es None)")

    # Definición de credenciales final utilizando las variables capturadas
    credentials = (client_id, client_secret)

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