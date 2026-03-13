def get_ms_account():
    client_id = '5666a19b-c616-43a9-8126-1eb9e31dbd67'
    credentials = (client_id, 'TOKEN_AUTH_ACTIVE') 

    # Agregamos User.Read.All a la lista
    scopes = [
        'https://graph.microsoft.com/User.Read.All',
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
        account = Account(
            credentials, 
            token_backend=token_backend, 
            main_resource='https://graph.microsoft.com/v1.0'
        )
        
        # IMPORTANTE: Usamos solo authenticate() sin parámetros extra 
        # para que use el backend de forma estricta.
        if account.is_authenticated:
            return account
        
        # Si no está autenticado, intentamos refrescar el token silenciosamente
        if account.authenticate(scopes=scopes):
            return account
        
        return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None