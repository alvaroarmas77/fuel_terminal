import os
from O365 import Account, FileSystemTokenBackend

def get_ms_account():
    client_id = '5666a19b-c616-43a9-8126-1eb9e31dbd67'
    # El secreto no se valida si el token es correcto, pero la librería pide el parámetro
    credentials = (client_id, 'TOKEN_AUTH_ACTIVE') 

    # Definimos los permisos exactos que requieren tus herramientas
    # Estos deben coincidir con los que aceptaste al generar el token en tu PC
    scopes = [
        'https://graph.microsoft.com/Mail.Send',
        'https://graph.microsoft.com/Files.ReadWrite.All',
        'https://graph.microsoft.com/Calendars.ReadWrite',
        'https://graph.microsoft.com/Sites.ReadWrite.All'
    ]

    token_backend = FileSystemTokenBackend(
        token_path='.', 
        token_filename='o365_token.txt'
    )

    try:
        # Añadimos 'main_resource' para asegurar que apunte a Graph y pasamos los scopes
        account = Account(
            credentials, 
            token_backend=token_backend, 
            main_resource='https://graph.microsoft.com/v1.0'
        )
        
        # Intentamos autenticar. Si el token existe, usará los scopes definidos arriba
        if account.authenticate(scopes=scopes):
            return account
        else:
            print("ERROR_AUTH: El token no es válido para los scopes solicitados.")
            return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None