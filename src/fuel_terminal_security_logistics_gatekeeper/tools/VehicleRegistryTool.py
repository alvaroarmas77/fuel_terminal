import pandas as pd
import io
import os
import warnings
from typing import Type
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

# Importación del helper de autenticación con manejo de rutas para entornos CI/CD
try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from utils.microsoft_graph import get_ms_account
    except ImportError:
        def get_ms_account(): return None

# Silenciar advertencias de motores de Excel (openpyxl)
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

class VehicleRegistryInput(BaseModel):
    """Esquema de entrada para la validación de flota y conductores autorizados."""
    truck_plate: str = Field(..., description="La placa del camión a validar (ej. ABC-1234).")
    driver_name: str = Field(..., description="Nombre completo del conductor para cruce de datos.")

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = (
        "Consulta la pestaña 'Vehicle_Registry' en el archivo 'Master_Control.xlsx' en OneDrive. "
        "Valida si la placa y el conductor están registrados y autorizados para operar en la terminal."
    )
    args_schema: Type[BaseModel] = VehicleRegistryInput

    def _run(self, truck_plate: str, driver_name: str) -> str:
        """
        Ejecuta la búsqueda en el maestro de flota alojado en la nube de Microsoft.
        """
        try:
            # 1. Conexión y Autenticación
            account = get_ms_account()
            if not account:
                return "ERROR_AUTENTICACION: No se pudo establecer conexión con Microsoft Graph API."
                
            storage = account.storage()
            drive = storage.get_default_drive()
            
            # 2. Localización y Descarga del archivo maestro
            try:
                file_item = drive.get_item_by_path('Fuel_Terminal_System/Master_Control.xlsx')
                content = file_item.download()
            except Exception as e:
                return f"ERROR_ARCHIVO: No se encontró 'Master_Control.xlsx' o error de descarga: {str(e)}"

            # 3. Lectura y Normalización de Datos
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
            
            # Limpieza: quitamos espacios extra y estandarizamos a mayúsculas/minúsculas
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().str.upper()
            df['Driver Name'] = df['Driver Name'].astype(str).str.strip().str.lower()
            
            target_plate = truck_plate.strip().upper()
            target_driver = driver_name.strip().lower()

            # 4. Lógica de Validación (Búsqueda Exacta)
            match = df[(df['Truck Plate'] == target_plate) & 
                       (df['Driver Name'] == target_driver)]
            
            if not match.empty:
                id_interno = match.iloc[0].get('ID_Interno', 'N/A')
                status_permit = match.iloc[0].get('Status_Permit', 'Activo')
                
                if str(status_permit).upper() != "ACTIVO":
                    return f"RECHAZADO: El vehículo {target_plate} tiene el permiso inactivo/vencido."

                return (
                    f"VALIDADO|ID:{id_interno}|Placa:{target_plate}|Conductor:{target_driver.title()}|"
                    f"INFO: Registro encontrado y autorización confirmada para carga."
                )
            
            return f"DENEGADO: La placa {target_plate} con el conductor {target_driver.title()} no figuran en el registro autorizado."

        except Exception as e:
            return f"ERROR_CRITICO_REGISTRO: Fallo inesperado en la validación de flota: {str(e)}"