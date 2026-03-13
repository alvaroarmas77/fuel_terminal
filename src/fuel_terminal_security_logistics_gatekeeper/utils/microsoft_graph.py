import os
from O365 import Account, FileSystemTokenBackend #

def get_ms_account():
    client_id = '5666a19b-c616-43a9-8126-1eb9e31dbd67'
    credentials = (client_id, 'TOKEN_AUTH_ACTIVE') 

    scopes = [
        'https://graph.microsoft.com/Mail.Send',
        'https://graph.microsoft.com/Files.ReadWrite.All',
        'https://graph.microsoft.com/Calendars.ReadWrite',
        'https://graph.microsoft.com/Sites.ReadWrite.All',
        'https://graph.microsoft.com/User.Read.All' # Se añade User.Read.All para compatibilidad
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
        
        if account.authenticate(scopes=scopes):
            return account
        else:
            print("ERROR_AUTH: El token no es válido para los scopes solicitados.")
            return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None