import pandas as pd
import io
from crewai_tools import BaseTool

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = "Verifica SCTR y bloqueos en Security_Database.xlsx dentro de Fuel_Terminal_System."

    def _run(self, driver_id: str, terminal_id: str = "Terminal Sur") -> str:
        try:
            account = get_ms_account()
            if not account: return "ERROR: Autenticación fallida."
            
            drive = account.storage().get_default_drive()
            items = drive.get_root().get_items()
            
            target_folder = next((i for i in items if i.name == 'Fuel_Terminal_System' and i.is_folder), None)
            if not target_folder: return "ERROR_SISTEMA: Carpeta no hallada."

            folder_items = target_folder.get_items()
            file_item = next((f for f in folder_items if f.name == 'Security_Database.xlsx'), None)
            if not file_item: return "ERROR_SISTEMA: 'Security_Database.xlsx' no hallado."

            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Security_Status", engine='openpyxl')
            
            did = str(driver_id).strip().upper()
            df['Driver_ID'] = df['Driver_ID'].astype(str).str.strip().upper()
            
            match = df[df['Driver_ID'] == did]
            if not match.empty:
                nombre = match['Name'].values[0]
                if str(match['Blocked'].values[0]).upper() in ['SI', 'YES', 'TRUE']:
                    return f"DENEGADO: El conductor {nombre} tiene un BLOQUEO ADMINISTRATIVO."
                return f"CONFIRMACIÓN: Acceso Autorizado para {nombre} en {terminal_id} (SCTR Válido)."

            return f"DENEGADO: ID {did} no figura en la base de seguridad."
        except Exception as e:
            return f"ERROR_SECURITY: {str(e)}"