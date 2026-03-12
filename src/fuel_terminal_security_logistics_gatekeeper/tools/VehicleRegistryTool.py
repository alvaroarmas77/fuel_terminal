import os
import pandas as pd
import io
import sys
import O365
from typing import Optional
from crewai_tools import BaseTool

# --- BLINDAJE DE IMPORTACIÓN ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from utils.microsoft_graph import get_ms_account
    except ImportError:
        def get_ms_account(): return None

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida usuarios en 'Authorized_Users' y vehículos en 'Vehicle_Registry' usando Master_Control.xlsx."

    def _run(self, dispatcher_email: Optional[str] = None, plate_id: Optional[str] = None, driver_name: Optional[str] = None) -> str:
        # Validación de entorno
        if not os.getenv('AZURE_CLIENT_ID') and not os.getenv('OUTLOOK_CLIENT_ID'):
            return "ERROR_CRITICO: El sistema no detecta variables de entorno."

        try:
            account = get_ms_account()
        except Exception as e:
            return f"Error al invocar get_ms_account: {str(e)}"

        if not account:
            return "ERROR_CONEXIÓN: No se pudo obtener la cuenta de Microsoft."
        
        try:
            # Acceso al archivo en OneDrive
            drive = account.storage().get_default_drive()
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xlsx')
            content = file_item.download()
            
            # FASE 1: Authorized_Users (Solo valida el despachador)
            if dispatcher_email and (not plate_id or plate_id == "UNKNOWN"):
                df_auth = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users", engine='openpyxl')
                email_l = str(dispatcher_email).strip().lower()
                
                # Se asume que en Authorized_Users la columna es 'Email'
                if email_l in df_auth['Email'].astype(str).str.lower().values:
                    user = df_auth[df_auth['Email'].astype(str).str.lower() == email_l].iloc[0]
                    return f"PHASE_1_SUCCESS: {user['Nombre']} ({user['Empresa']}) autorizado."
                return f"RECHAZO_FASE_1: El email {email_l} no está registrado."

            # FASE 2: Vehicle_Registry (Validación estricta de encabezados)
            if plate_id and driver_name:
                df_veh = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
                
                # Limpieza de datos para comparación
                p_limpia = str(plate_id).strip().upper()
                d_limpio = str(driver_name).strip().lower()
                
                # VERIFICACIÓN ESTRICTA: Se buscan coincidencias solo en los encabezados permitidos
                # Los encabezados verificados son: 'Truck Plate' y 'Driver Name'
                # Nota: 'Driver Email' e 'ID_Interno' quedan disponibles en el dataframe si se requieren
                match = df_veh[
                    (df_veh['Truck Plate'].astype(str).str.upper() == p_limpia) & 
                    (df_veh['Driver Name'].astype(str).str.lower() == d_limpio)
                ]
                
                if not match.empty:
                    # Opcional: Extraer ID_Interno para el log si es necesario
                    id_interno = match['ID_Interno'].values[0]
                    return f"PHASE_2_SUCCESS: Camión {p_limpia} y conductor {driver_name} validados (ID: {id_interno})."
                
                return "RECHAZO_FASE_2: Activos no encontrados en el registro oficial (Truck Plate / Driver Name)."

            return "ERROR_PARAM: Faltan datos para la validación solicitada."
        except Exception as e:
            return f"ERROR_SISTEMA: {str(e)}"