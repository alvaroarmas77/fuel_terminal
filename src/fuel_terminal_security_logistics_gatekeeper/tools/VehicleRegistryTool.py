import os
import pandas as pd
import io
import sys
from typing import Optional
from crewai_tools import BaseTool

# --- BLINDAJE DE IMPORTACIÓN ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
    except ImportError:
        def get_ms_account(): return None

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida usuarios en 'Authorized_Users' y vehículos en 'Vehicle_Registry' desde Master_Control.xlsx."

    def _run(self, dispatcher_email: Optional[str] = None, plate_id: Optional[str] = None, driver_name: Optional[str] = None) -> str:
        import os  # <--- COLÓCALO AQUÍ, DENTRO DEL MÉTODO
        import sys

        # Opcional: Para debugear si realmente está viendo las variables
        if not os.getenv('AZURE_CLIENT_ID'):
            return "ERROR_CRITICO: El sistema no detecta variables de entorno."

        # Tu lógica de conexión aquí...
        try:
            # Asegúrate de que microsoft_graph también se importe aquí dentro
            from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
            account = get_ms_account()
            # ... resto de la lógica
        except Exception as e:
            return f"Error en la ejecución: {str(e)}"
        from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
        account = get_ms_account()
        if not account:
            return "ERROR_CONEXIÓN: No se pudo obtener la cuenta de Microsoft. Verifica credenciales de Azure."
        
        try:
            drive = account.storage().get_default_drive()
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xlsx')
            content = file_item.download()
            
            # FASE 1: Authorized_Users
            if dispatcher_email and (not plate_id or plate_id == "UNKNOWN"):
                df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users", engine='openpyxl')
                email_l = str(dispatcher_email).strip().lower()
                if email_l in df['Email'].astype(str).str.lower().values:
                    user = df[df['Email'].astype(str).str.lower() == email_l].iloc[0]
                    return f"PHASE_1_SUCCESS: {user['Nombre']} ({user['Empresa']}) autorizado."
                return f"RECHAZO_FASE_1: El email {email_l} no está registrado."

            # FASE 2: Vehicle_Registry
            if plate_id and driver_name:
                df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
                p_limpia = str(plate_id).strip().upper()
                d_limpio = str(driver_name).strip().lower()
                
                match = df[(df['Truck Plate'].astype(str).str.upper() == p_limpia) & 
                           (df['Driver Name'].astype(str).str.lower() == d_limpio)]
                
                if not match.empty:
                    return f"PHASE_2_SUCCESS: Camión {p_limpia} y conductor {driver_name} validados."
                return "RECHAZO_FASE_2: Activos no encontrados en el registro oficial."

            return "ERROR_PARAM: Faltan datos para la validación solicitada."
        except Exception as e:
            return f"ERROR_SISTEMA: {str(e)}"