import pandas as pd
import io
from crewai_tools import BaseTool
import logging

logger = logging.getLogger(__name__)

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
            if not account: return "ERROR: Autenticación MS Graph fallida."
            
            # Navegación robusta por objetos
            drive = account.storage().get_default_drive()
            items = drive.get_root().get_items()
            
            # Buscar carpeta
            target_folder = next((i for i in items if i.name == 'Fuel_Terminal_System' and i.is_folder), None)
            if not target_folder: return "ERROR_SISTEMA: Carpeta 'Fuel_Terminal_System' no hallada en la raíz."

            # Buscar archivo
            folder_items = target_folder.get_items()
            file_item = next((f for f in folder_items if f.name == 'Master_Control.xlsx'), None)
            if not file_item: return "ERROR_SISTEMA: Archivo 'Master_Control.xlsx' no hallado."

            # Procesamiento de datos
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
            
            plate = str(truck_plate).strip().upper()
            driver = str(driver_name).strip().upper()
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().upper()
            
            match = df[df['Truck Plate'] == plate]
            if not match.empty:
                return f"VALIDADO: Vehículo {plate} autorizado para {driver}."
            
            return f"DENEGADO: Placa {plate} no registrada en la flota."
        except Exception as e:
            return f"ERROR_REGISTRY: {str(e)}"