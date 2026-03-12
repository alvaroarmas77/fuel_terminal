import os
import pandas as pd
import io
import sys

# --- COMPATIBILIDAD DE LIBRERÍAS ---
try:
    from crewai_tools import BaseTool
except ImportError:
    try:
        from crewai.tools import BaseTool
    except ImportError:
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
                # Este error es el que viste en el log anterior (Falta de Token)
                return "ERROR_CONEXIÓN: No se pudo conectar con Microsoft Graph. Verifique el archivo o365_token.txt."

            # 1. Navegación al archivo maestro
            # get_default_drive() apunta al OneDrive de la cuenta o al sitio principal de SharePoint
            drive = account.storage().get_default_drive()
            
            # Buscamos la carpeta raíz. Si está en una subcarpeta, se puede encadenar .get_item()
            root = drive.get_root()
            folder = root.get_item('Fuel_Terminal_System')
            
            # Intentamos obtener el archivo. 
            # NOTA: Si el archivo se llama Master_Control.xlsx pero pusiste .xls, dará error.
            file_item = folder.get_item('Master_Control.xls')
            
            # 2. Descarga y detección de motor de Excel
            content = file_item.download()
            
            # Ajuste de robustez: Si es .xls usa 'xlrd', si es .xlsx usa 'openpyxl'
            # Usamos un try-except interno para la lectura
            try:
                df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users")
            except Exception:
                # Fallback manual si el motor automático falla
                df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users", engine='openpyxl')
            
            # 3. Limpieza de datos (Evitamos errores por espacios o mayúsculas)
            email_to_check = str(dispatcher_email).strip().lower()
            
            # Verificamos que la columna 'Email' exista
            if 'Email' not in df.columns:
                return f"ERROR_DATOS: No se encontró la columna 'Email' en la pestaña 'Authorized_Users'."

            df['Email'] = df['Email'].astype(str).str.strip().lower()
            
            # 4. Búsqueda de coincidencia
            match = df[df['Email'] == email_to_check]
            
            if not match.empty:
                # Usamos .iloc[0] para mayor seguridad en pandas moderno
                nombre = match['Nombre'].iloc[0]
                empresa = match['Empresa'].iloc[0]
                return f"PHASE_1_SUCCESS: ACCESO CONCEDIDO - Usuario: {nombre} - Empresa: {empresa}. Procediendo a validación de activos."

            # 5. Retorno de rechazo (Esto detiene el Crew según tus reglas de tasks.yaml)
            return f"RECHAZO_FASE_1: El usuario {dispatcher_email} no tiene permisos de acceso en 'Authorized_Users'."

        except Exception as e:
            # Captura errores de "Archivo no encontrado" o "Carpeta no existe"
            return f"ERROR_SISTEMA: Fallo en la herramienta de control de acceso. Detalle: {str(e)}"