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
            
            # 2. Localización del archivo maestro
            try:
                # Ruta relativa en OneDrive: Fuel_Terminal_System/Master_Control.xlsx
                file_item