import pandas as pd
import io
import os
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# Importación del helper de autenticación
try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    from utils.microsoft_graph import get_ms_account

class VehicleRegistryInput(BaseModel):
    """Esquema de entrada para la validación de flota y conductores."""
    truck_plate: str = Field(..., description="La placa del camión (ej. ABC-1234).")
    driver_name: str = Field(..., description="Nombre completo del conductor del vehículo.")

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = (
        "Consulta la pestaña 'Vehicle_Registry' en 'Master_Control.xlsx' en OneDrive. "
        "Valida si la placa y el conductor están registrados y autorizados para operar."
    )
    args_schema: Type[BaseModel] = VehicleRegistryInput

    def _run(self, truck_plate: str, driver_name: str) -> str:
        try:
            account = get_ms_account()
            if not account:
                return "ERROR_AUTENTICACION: No se pudo conectar con Microsoft Graph."
                
            drive = account.storage().get_default_drive()
            file = drive.get_item_by_path('Fuel_Terminal_System/Master_Control.xlsx')
            
            # Descarga y lectura
            content = file.download()
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry")
            
            # Limpieza de espacios y normalización de texto
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().str.upper()
            df['Driver Name'] = df['Driver Name'].astype(str).str.strip().str.lower()
            
            # Búsqueda exacta
            match = df[(df['Truck Plate'] == truck_plate.strip().upper()) & 
                       (df['Driver Name'] == driver_name.strip().lower())]
            
            if not match.empty:
                id_interno = match.iloc[0]['ID_Interno']
                return f"VALIDADO: Vehículo y conductor autorizados. ID Interno de Flota: {id_interno}."
            
            return "RECHAZADO: La combinación de placa y conductor no coincide con los registros oficiales."

        except Exception as e:
            return f"ERROR_SISTEMA: Fallo al validar el registro de flota en OneDrive: {str(e)}"