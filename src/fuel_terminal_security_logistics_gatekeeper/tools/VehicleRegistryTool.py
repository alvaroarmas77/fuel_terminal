import os
import pandas as pd
import io
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account

try:
    from crewai_tools import BaseTool
except ImportError:
    from crewai.tools import BaseTool

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida la placa y conductor en el registro de vehículos."

    def _run(self, plate_id: str, driver_name: str) -> str:
        try:
            account = get_ms_account()
            target_user = "soportesap@frontera-virtual.com"
            drive = account.storage().get_drive_by_endpoint(target_user)
            
            root = drive.get_root()
            folder = root.get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xlsx')
                
            content = file_item.download()
            df_veh = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_registry")
            
            p_limpia = str(plate_id).strip().upper()
            d_limpio = str(driver_name).strip().lower()
            
            match = df_veh[
                (df_veh['Truck Plate'].astype(str).str.strip().upper() == p_limpia) & 
                (df_veh['Driver Name'].astype(str).str.strip().lower() == d_limpio)
            ]
            
            if not match.empty:
                id_int = match['ID_Interno'].iloc[0]
                return f"PHASE_2_SUCCESS: ACTIVOS VALIDADOS - ID: {id_int}."
            
            return f"RECHAZO_FASE_2: Validación fallida para placa {p_limpia}."
        except Exception as e:
            return f"ERROR_VEHICULOS: {str(e)}"