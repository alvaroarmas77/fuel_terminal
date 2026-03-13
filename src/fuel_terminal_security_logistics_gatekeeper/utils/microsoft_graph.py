import os
import sys
import msal
import os
from O365 import Account, FileSystemTokenBackend

def get_ms_account():
    """
    Establece la conexión con Microsoft Graph utilizando el archivo de token.
    Mantiene la compatibilidad con las herramientas existentes.
    """
    # 1. Datos de identificación de la App (Tu ID real)
    client_id = '5666a19b-c616-43a9-8126-1eb9e31dbd67'
    
    # 2. SECO Y DIRECTO: Al existir el archivo de token, el Secret no se valida.
    # Usamos un valor fijo para evitar que la librería intente buscar contraseñas reales.
    credentials = (client_id, 'TOKEN_AUTH_ACTIVE')

    # 3. Configuración del Backend (Busca el archivo en la raíz del proyecto)
    token_backend = FileSystemTokenBackend(
        token_path='.', 
        token_filename='o365_token.txt'
    )

    try:
        # Inicializamos la cuenta con el backend del archivo
        account = Account(credentials, token_backend=token_backend)
        
        # El método authenticate() devolverá True si el token es válido
        # SIN intentar una nueva autenticación con secret si el archivo existe.
        if account.authenticate():
            return account
        else:
            # Si llega aquí, es que el archivo no existe o el token caducó totalmente
            print("ERROR_AUTH: No se encontró el archivo o365_token.txt o el token expiró.")
            return None
            
    except Exception as e:
        print(f"ERROR_SISTEMA_GRAPH: {str(e)}")
        return None