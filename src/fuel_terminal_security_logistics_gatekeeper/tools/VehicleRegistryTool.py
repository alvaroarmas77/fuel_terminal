import pandas as pd
import io
from crewai_tools import BaseTool

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida placa y conductor contra el archivo Master_Control.xlsx en OneDrive."

    def _run(self, truck_plate: str, driver_name: str) -> str:
        try:
            account = get_ms_account()
            if not account: return "ERROR: Fallo de autenticación MS Graph."
            
            drive = account.storage().get_default_drive()
            file_item = drive.get_item_by_path('Fuel_Terminal_System/Master_Control.xlsx')
            content = file_item.download()
            
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
            target_plate = truck_plate.strip().upper()
            
            if target_plate in df['Truck Plate'].astype(str).str.upper().values:
                return f"VALIDADO: Vehículo {target_plate} autorizado."
            return f"DENEGADO: Placa {target_plate} no registrada."
        except Exception as e:
            return f"ERROR_REGISTRY: {str(e)}"