import pandas as pd
import io
from typing import Optional
from crewai_tools import BaseTool

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida usuarios en 'Authorized_Users' y vehículos en 'Vehicle_Registry'."

    def _run(self, dispatcher_email: Optional[str] = None, plate_id: Optional[str] = None, driver_name: Optional[str] = None) -> str:
        try:
            account = get_ms_account()
            drive = account.storage().get_default_drive()
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xlsx')
            content = file_item.download()
            
            # FASE 1: Authorized_Users (Email, Nombre, Empresa)
            if dispatcher_email and not plate_id:
                df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users", engine='openpyxl')
                email_l = str(dispatcher_email).strip().lower()
                if email_l in df['Email'].astype(str).str.lower().values:
                    user = df[df['Email'].astype(str).str.lower() == email_l].iloc[0]
                    return f"PHASE_1_SUCCESS: {user['Nombre']} de {user['Empresa']} autorizado."
                return f"RECHAZO_FASE_1: El email {email_l} no está en la lista autorizada."

            # FASE 2: Vehicle_Registry (Truck Plate, Driver Name, Driver Email, ID_Interno)
            if plate_id and driver_name:
                df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
                p_limpia = str(plate_id).strip().upper()
                d_limpio = str(driver_name).strip().lower()
                
                match = df[(df['Truck Plate'].astype(str).str.upper() == p_limpia) & 
                           (df['Driver Name'].astype(str).str.lower() == d_limpio)]
                
                if not match.empty:
                    return f"PHASE_2_SUCCESS: Vehículo {p_limpia} y conductor {driver_name} (ID: {match.iloc[0]['ID_Interno']}) validados."
                return f"RECHAZO_FASE_2: El camión o el conductor no figuran en el registro oficial."

            return "ERROR_PARAM: Faltan datos para validación."
        except Exception as e:
            return f"ERROR_SISTEMA: {str(e)}"