import pandas as pd
import io
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
from crewai.tools import BaseTool

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida placa y conductor en la pestaña Vehicle_registry de Master_Control.xlsx"

    def _run(self, plate_id: str, driver_name: str) -> str:
        account = get_ms_account()
        if not account: return "ERROR_CONEXIÓN"
        
        target_user = "soportesap@frontera-virtual.com"
        try:
            drive = account.storage().get_drive_by_endpoint(target_user)
            # Acceso a la carpeta y archivo
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xlsx')
            
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_registry")
            
            # Normalización para búsqueda exacta
            p_limpia = str(plate_id).strip().upper()
            d_limpio = str(driver_name).strip().lower()
            
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().upper()
            df['Driver Name'] = df['Driver Name'].astype(str).str.strip().lower()
            
            match = df[(df['Truck Plate'] == p_limpia) & (df['Driver Name'] == d_limpio)]
            
            if not match.empty:
                return "PHASE_2_SUCCESS"
            return f"RECHAZO_FASE_2: El vehículo {p_limpia} o el conductor {d_limpio} no están vinculados o vigentes."
        except Exception as e:
            return f"ERROR_OPERATIVO_VEHICULO: {str(e)}"