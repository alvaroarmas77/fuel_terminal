import pandas as pd
import io
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
from crewai_tools import BaseTool

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = "Valida la identidad del despachador en Master_Control.xls"

    def _run(self, dispatcher_email: str) -> str:
        account = get_ms_account()
        if not account: return "ERROR_CONEXIÓN"
        
        target_user = "soportesap@frontera-virtual.com"
        try:
            drive = account.storage().get_drive_by_endpoint(target_user)
            # Nota: Asegurar que el nombre del archivo sea exacto (xls vs xlsx)
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xls') 
            
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users")
            
            email_check = str(dispatcher_email).strip().lower()
            df['Email'] = df['Email'].astype(str).str.strip().lower()
            
            match = df[df['Email'] == email_check]
            if not match.empty:
                return "PHASE_1_SUCCESS"
            return f"RECHAZO_FASE_1: {dispatcher_email} no autorizado."
        except Exception as e:
            return f"ERROR_OPERATIVO: {str(e)}"