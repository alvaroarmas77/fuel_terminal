import pandas as pd
import io
from crewai_tools import BaseTool
import logging

logger = logging.getLogger(__name__)

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = "Verifica ID de conductor, SCTR y bloqueos en Security_Database.xlsx."

    def _run(self, driver_id: str, terminal_id: str = "Terminal Sur") -> str:
        try:
            account = get_ms_account()
            if not account: return "ERROR: Fallo de autenticación MS Graph."
            
            drive = account.storage().get_default_drive()
            # RUTA ABSOLUTA CORREGIDA
            file_path = '/Fuel_Terminal_System/Security_Database.xlsx'
            
            try:
                file_item = drive.get_item_by_path(file_path)
            except Exception:
                return f"ERROR_RUTA: No se halló {file_path} en OneDrive."

            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Security_Status", engine='openpyxl')
            
            did = str(driver_id).strip().upper()
            df['Driver_ID'] = df['Driver_ID'].astype(str).str.strip().upper()
            
            # Buscamos al conductor
            match = df[df['Driver_ID'] == did]
            
            if not match.empty:
                nombre = match['Name'].values[0]
                sctr = str(match['SCTR_Status'].values[0]).upper()
                bloqueo = str(match['Blocked'].values[0]).upper()
                
                if bloqueo == 'YES' or bloqueo == 'SI':
                    return f"DENEGADO: El conductor {nombre} tiene un BLOQUEO ADMINISTRATIVO."
                
                if sctr != 'VALIDO' and sctr != 'VALID':
                    return f"DENEGADO: SCTR de {nombre} vencido o no cargado."
                
                return f"CONFIRMACIÓN: Acceso Autorizado para {nombre} en {terminal_id}."

            return f"DENEGADO: ID {did} no encontrado en la base de seguridad."

        except Exception as e:
            return f"ERROR_SECURITY: {str(e)}"