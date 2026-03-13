import os
import pandas as pd
import io
import sys
from O365 import Account, FileSystemTokenBackend
# Si también usas la conexión de tu utilidad:
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
# --- COMPATIBILIDAD DE LIBRERÍAS ---
try:
    from crewai_tools import BaseTool
except ImportError:
    try:
        from crewai.tools import BaseTool
    except ImportError:
        from crewai.tools.base_tool import BaseTool

# --- BLINDAJE DE IMPORTACIÓN MODIFICADO ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
    except ImportError:
        def get_ms_account(): return None

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = (
        "Valida la identidad del despachador consultando 'Master_Control.xls' "
        "en la pestaña 'Authorized_Users'. Es la primera línea de defensa."
    )

    def _run(self, dispatcher_email: str) -> str:
        """
        Verifica si el remitente tiene permisos de acceso al sistema.
        """
        try:
            # CAMBIO: Usamos la función que lee el o365_token.txt sin validar secret
            account = get_ms_account()
            if not account:
                return "ERROR_CONEXIÓN: No se pudo conectar con Microsoft Graph. Verifique el archivo o365_token.txt."

            # 1. Acceso a SharePoint/OneDrive (Ruta original)
            drive = account.storage().get_default_drive()
            root = drive.get_root()
            folder = root.get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xls')
            
            # 2. Descarga y lectura
            content = file_item.download()
            
            try:
                df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users")
            except Exception:
                # Motor opcional si el motor automático falla
                df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users", engine='openpyxl')
            
            # 3. Limpieza de datos (Tu lógica original)
            email_to_check = str(dispatcher_email).strip().lower()
            
            if 'Email' not in df.columns:
                return f"ERROR_DATOS: No se encontró la columna 'Email' en la pestaña 'Authorized_Users'."

            df['Email'] = df['Email'].astype(str).str.strip().lower()
            
            # 4. Búsqueda de coincidencia
            match = df[df['Email'] == email_to_check]
            
            if not match.empty:
                nombre = match['Nombre'].iloc[0]
                empresa = match['Empresa'].iloc[0]
                return f"PHASE_1_SUCCESS: ACCESO CONCEDIDO - Usuario: {nombre} - Empresa: {empresa}. Procediendo a validación de activos."

            return f"RECHAZO_FASE_1: El usuario {dispatcher_email} no tiene permisos de acceso en 'Authorized_Users'."

        except Exception as e:
            return f"ERROR_SISTEMA: Fallo en la herramienta de control de acceso. Detalle: {str(e)}"