import pandas as pd
import io
from crewai_tools import BaseTool

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Fase 1: Valida si el email del remitente está en la lista de usuarios autorizados de Master_Control.xlsx."

    def _run(self, dispatcher_email: str) -> str:
        try:
            account = get_ms_account()
            drive = account.storage().get_default_drive()
            
            # Navegación compatible con OneDrive/MyFiles/
            folder = drive.get_item_by_path('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xlsx')
            
            content = file_item.download()
            # Accedemos a la pestaña de usuarios autorizados
            df_users = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users", engine='openpyxl')
            
            email_limpio = str(dispatcher_email).strip().lower()
            
            # Verificación estricta
            if email_limpio in df_users['Email'].astype(str).str.lower().values:
                user_data = df_users[df_users['Email'].astype(str).str.lower() == email_limpio].iloc[0]
                return f"AUTH_SUCCESS: El usuario {email_limpio} ({user_data['Name']}) está autorizado. PROCEDER A FASE 2."
            
            return f"AUTH_DENIED: El correo {email_limpio} no está registrado en el sistema de seguridad."

        except Exception as e:
            return f"ERROR_SISTEMA: No se pudo verificar la base de datos. Detalle: {str(e)}"