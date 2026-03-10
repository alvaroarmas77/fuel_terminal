import pandas as pd
import io
from crewai_tools import BaseTool
import logging

# Configuración de logs para ver detalles en GitHub Actions
logger = logging.getLogger(__name__)

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida placa y conductor contra el archivo Master_Control.xlsx en la carpeta Fuel_Terminal_System de OneDrive."

    def _run(self, truck_plate: str, driver_name: str) -> str:
        try:
            account = get_ms_account()
            if not account: 
                return "ERROR: Fallo de autenticación MS Graph."
            
            # 1. Acceder al almacenamiento de OneDrive
            storage = account.storage()
            drive = account.storage().get_default_drive()

            # 2. Corrección de Ruta: Usamos la ruta absoluta desde el root del drive.
            # Nota: Agregamos el '/' inicial para asegurar que busque desde la raíz.
            file_path = '/Fuel_Terminal_System/Master_Control.xlsx'
            
            try:
                # Intentamos obtener el archivo por ruta
                file_item = drive.get_item_by_path(file_path)
            except Exception as path_err:
                return f"ERROR_RUTA: No se encontró el archivo en {file_path}. Verifique que la carpeta 'Fuel_Terminal_System' esté en la raíz de su OneDrive."

            # 3. Descarga y procesamiento
            content = file_item.download()
            if not content:
                return "ERROR: El archivo Master_Control.xlsx está vacío o no se pudo descargar."

            # Leemos el Excel usando openpyxl
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
            
            # Limpieza de datos para comparación exacta
            target_plate = str(truck_plate).strip().upper()
            target_driver = str(driver_name).strip().upper()
            
            # Normalizamos las columnas del DataFrame
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().upper()
            df['Driver Name'] = df['Driver Name'].astype(str).str.strip().upper()

            # 4. Lógica de validación holística
            match = df[df['Truck Plate'] == target_plate]

            if not match.empty:
                # Opcional: Validar también que el nombre coincida en la misma fila
                is_driver_valid = target_driver in match['Driver Name'].values
                
                status_msg = f"VALIDADO: Vehículo {target_plate} autorizado."
                if is_driver_valid:
                    status_msg += f" Conductor {target_driver} verificado en registro."
                else:
                    status_msg += f" ADVERTENCIA: Conductor {target_driver} no coincide con el registro de esta placa."
                
                return status_msg

            return f"DENEGADO: La placa {target_plate} no se encuentra en el registro oficial de la flota."

        except Exception as e:
            # Capturamos el error detallado para el log de GitHub
            return f"ERROR_REGISTRY: {str(e)}"