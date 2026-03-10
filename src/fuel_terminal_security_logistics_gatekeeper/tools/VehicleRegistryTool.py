import pandas as pd
import io
import os
from typing import Type
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class VehicleRegistryInput(BaseModel):
    """Esquema de entrada para la validación de flota."""
    truck_plate: str = Field(..., description="La placa del camión (ej. ABC-1234).")
    driver_name: str = Field(..., description="Nombre completo del conductor para cruce de datos.")

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida placa y conductor contra el archivo Master_Control.xlsx en OneDrive."
    args_schema: Type[BaseModel] = VehicleRegistryInput

    def _run(self, truck_plate: str, driver_name: str) -> str:
        try:
            account = get_ms_account()
            if not account:
                return "ERROR_AUTH: No se pudo obtener acceso a Microsoft Graph (revisar ClientID/Secret)."
            
            drive = account.storage().get_default_drive()
            file_item = drive.get_item_by_path('Fuel_Terminal_System/Master_Control.xlsx')
            content = file_item.download()
            
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().str.upper()
            
            target_plate = truck_plate.strip().upper()
            if target_plate in df['Truck Plate'].values:
                return f"VALIDADO: El vehículo con placa {target_plate} está registrado y autorizado para operar."
            
            return f"DENEGADO: La placa {target_plate} no existe en el registro maestro de la flota."
        except Exception as e:
            return f"ERROR_VEHICLE_REGISTRY: {str(e)}"