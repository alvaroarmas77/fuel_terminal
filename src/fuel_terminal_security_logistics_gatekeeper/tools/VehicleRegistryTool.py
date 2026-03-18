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
    description: str = "Valida placa y conductor en Vehicle_registry"

    def _run(self, plate_id: str, driver_name: str) -> str:
        account = get_ms_account()
        target_user = "soportesap@frontera-virtual.com"
        try:
            drive = account.storage().get_drive_by_endpoint(target_user)
            file_item = drive.get_root().get_item('Fuel_Terminal_System').get_item('Master_Control.xlsx')
            
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_registry")
            
            p_limpia = str(plate_id).strip().upper()
            d_limpio = str(driver_name).strip().lower()
            
            match = df[(df['Truck Plate'].astype(str).str.upper() == p_limpia) & 
                       (df['Driver Name'].astype(str).str.lower() == d_limpio)]
            
            if not match.empty:
                return f"PHASE_2_SUCCESS: ACTIVOS VALIDADOS para {p_limpia}"
            return f"RECHAZO_FASE_2: Datos no encontrados."
        except Exception as e:
            return f"ERROR: {str(e)}"