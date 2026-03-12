import os
import pandas as pd
import io
import O365
from crewai_tools import BaseTool

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from utils.microsoft_graph import get_ms_account
    except ImportError:
        def get_ms_account(): return None

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = "Verifica SCTR y bloqueos en Security_Database.xlsx dentro de Fuel_Terminal_System."

    def _run(self, driver_id: str, terminal_id: str = "Terminal Sur") -> str:
        try:
            account = get_ms_account()
            if not account:
                return "ERROR_CONEXIÓN: No se pudo conectar con la cuenta de Microsoft."

            # Navegación directa
            drive = account.storage().get_default_drive()
            root = drive.get_root()
            folder = root.get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Security_Database.xlsx')
            
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Security_Status", engine='openpyxl')
            
            did = str(driver_id).strip().upper()
            df['Driver_ID'] = df['Driver_ID'].astype(str).str.strip().upper()
            
            match = df[df['Driver_ID'] == did]
            if not match.empty:
                nombre = match['Name'].values[0]
                blocked_val = str(match['Blocked'].values[0]).upper()
                if blocked_val in ['SI', 'YES', 'TRUE']:
                    return f"DENEGADO: El conductor {nombre} tiene un BLOQUEO ADMINISTRATIVO."
                return f"CONFIRMACIÓN: Acceso Autorizado para {nombre} en {terminal_id} (SCTR Válido)."

            return f"DENEGADO: ID {did} no figura en la base de seguridad."
        except Exception as e:
            return f"ERROR_SISTEMA: Fallo en la localización o lectura del archivo. Detalle: {str(e)}"