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
            drive = account.storage().get_default_drive()
            
            # Buscamos el archivo directamente por su ruta relativa al root
            # En la librería O365, get_item_by_path es la forma más estable
            file_item = drive.get_item_by_path('Fuel_Terminal_System/Security_Database.xlsx')
            
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
            return f"ERROR_SECURITY: No se pudo acceder al archivo. Verifique la carpeta Fuel_Terminal_System. Detalle: {str(e)}"