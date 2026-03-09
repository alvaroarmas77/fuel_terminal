import pandas as pd
import io
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# Importación del helper de autenticación
try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    from utils.microsoft_graph import get_ms_account

class AccessControlInput(BaseModel):
    """Esquema de entrada para la validación de acceso de usuarios."""
    sender_email: str = Field(..., description="El correo electrónico del remitente que solicita la carga.")

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = (
        "Consulta la pestaña 'Authorized_Users' en 'Master_Control.xlsx' en OneDrive. "
        "Verifica si el email del remitente está en la lista blanca de la terminal "
        "antes de permitir cualquier operación logística."
    )
    args_schema: Type[BaseModel] = AccessControlInput

    def _run(self, sender_email: str) -> str:
        try:
            # 1. Obtener la cuenta y acceso a OneDrive
            account = get_ms_account()
            if not account:
                return "ERROR_AUTENTICACION: No se pudo conectar con Microsoft Graph."
                
            drive = account.storage().get_default_drive()
            
            # 2. Localizar el archivo en la ruta específica de OneDrive
            # Ruta: Fuel_Terminal_System/Master_Control.xlsx
            file = drive.get_item_by_path('Fuel_Terminal_System/Master_Control.xlsx')
            
            # 3. Descargar el contenido en memoria para que Pandas lo lea sin guardar archivos locales
            content = file.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users")
            
            # 4. Lógica de validación (Case insensitive)
            match = df[df['Email'].str.lower() == sender_email.lower()]
            
            if not match.empty:
                nombre = match.iloc[0]['Nombre']
                empresa = match.iloc[0]['Empresa']
                return f"ACCESO_CONCEDIDO: {nombre} ({empresa})"
            
            return "ACCESO_DENEGADO: El usuario no está en la lista de personal autorizado."

        except Exception as e:
            return f"ERROR_SISTEMA: Fallo al leer la base de datos de seguridad en la nube: {str(e)}"