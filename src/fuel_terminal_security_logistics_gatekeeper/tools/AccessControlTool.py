import os
import pandas as pd
import io
import sys
try:
    from crewai_tools import BaseTool
except ImportError:
    try:
        from crewai.tools import BaseTool
    except ImportError:
        # Si ambas fallan, intentamos la ruta directa de las utilidades de crewai
        from crewai.tools.base_tool import BaseTool

# --- BLINDAJE DE IMPORTACIÓN ---
try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from utils.microsoft_graph import get_ms_account
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
            account = get_ms_account()
            if not account:
                return "ERROR_CONEXIÓN: No se pudo conectar con Microsoft Graph."

            # 1. Navegación al archivo maestro definido en tu lógica
            drive = account.storage().get_default_drive()
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            
            # Cambiado a Master_Control.xls según tu especificación
            file_item = folder.get_item('Master_Control.xls')
            
            # 2. Lectura de la pestaña específica 'Authorized_Users'
            content = file_item.download()
            df = pd.read_excel(
                io.BytesIO(content), 
                sheet_name="Authorized_Users", 
                engine='openpyxl' # O 'xlrd' si es un .xls antiguo real
            )
            
            # 3. Limpieza de datos para comparación
            email_to_check = str(dispatcher_email).strip().lower()
            df['Email'] = df['Email'].astype(str).str.strip().lower()
            
            # 4. Búsqueda de coincidencia
            match = df[df['Email'] == email_to_check]
            
            if not match.empty:
                nombre = match['Nombre'].values[0]
                empresa = match['Empresa'].values[0]
                # Retorna el formato de ÉXITO que espera el flujo
                return f"PHASE_1_SUCCESS: ACCESO CONCEDIDO - Usuario: {nombre} - Empresa: {empresa}. Procediendo a validación de activos."

            # 5. Retorna el formato de RECHAZO que aborta el flujo
            return f"RECHAZO_FASE_1: El usuario {dispatcher_email} no tiene permisos de acceso en 'Authorized_Users'."

        except Exception as e:
            return f"ERROR_SISTEMA: Fallo en la validación de seguridad. Detalle: {str(e)}"