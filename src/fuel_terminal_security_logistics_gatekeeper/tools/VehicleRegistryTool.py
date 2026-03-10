import pandas as pd
import io
from crewai_tools import BaseTool

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida placa y conductor contra Master_Control.xlsx en la carpeta Fuel_Terminal_System."

    def _run(self, truck_plate: str, driver_name: str) -> str:
        try:
            account = get_ms_account()
            drive = account.storage().get_default_drive()
            
            file_item = drive.get_item_by_path('Fuel_Terminal_System/Master_Control.xlsx')
            
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
            
            plate = str(truck_plate).strip().upper()
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().upper()
            
            match = df[df['Truck Plate'] == plate]
            if not match.empty:
                return f"VALIDADO: Vehículo {plate} autorizado para la operación."
            
            return f"DENEGADO: Placa {plate} no registrada en la flota oficial."
        except Exception as e:
            return f"ERROR_REGISTRY: {str(e)}"