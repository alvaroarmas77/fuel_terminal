import os
import pandas as pd
import io
from O365 import Account
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account

try:
    from crewai_tools import BaseTool
except ImportError:
    from crewai.tools import BaseTool

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = "Valida la identidad del despachador consultando el archivo maestro."

    def _run(self, dispatcher_email: str) -> str:
        try:
            account = get_ms_account()
            if not account:
                return "ERROR_CONEXIÓN: No se pudo conectar con Microsoft Graph."

            # CAMBIO: Especificar el dueño del archivo
            target_user = "logistica@tu-empresa.com" 
            drive = account.storage().get_drive_by_endpoint(target_user)
            
            root = drive.get_root()
            folder = root.get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xls')
            
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users")
            
            email_to_check = str(dispatcher_email).strip().lower()
            df['Email'] = df['Email'].astype(str).str.strip().lower()
            
            match = df[df['Email'] == email_to_check]
            
            if not match.empty:
                nombre = match['Nombre'].iloc[0]
                return f"PHASE_1_SUCCESS: ACCESO CONCEDIDO - Usuario: {nombre}."

            return f"RECHAZO_FASE_1: El usuario {dispatcher_email} no tiene permisos."
        except Exception as e:
            return f"ERROR_TOOL: {str(e)}"