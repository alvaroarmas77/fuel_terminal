import pandas as pd
import io
import os
import warnings
from datetime import datetime
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# Silenciamos advertencias de openpyxl que ensucian el log de GitHub
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# Importación del helper de autenticación con manejo de rutas
try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from utils.microsoft_graph import get_ms_account
    except ImportError:
        # Fallback para entornos de test locales
        def get_ms_account(): raise Exception("Módulo microsoft_graph no encontrado.")

class OrderManagementInput(BaseModel):
    """Esquema detallado para el registro final de la orden de carga en el ERP/OneDrive."""
    dispatcher_email: str = Field(..., description="Email del despachador que solicitó la carga.")
    truck_plate: str = Field(..., description="Placa del camión validada (ej. ABC-123).")
    driver_name: str = Field(..., description="Nombre completo del conductor validado.")
    fuel_volume: str = Field(..., description="Volumen de combustible (ej. 5000 Gal).")
    assigned_island: str = Field(..., description="La isla o bahía asignada (ej. Isla_3).")
    start_time: str = Field(..., description="Hora de inicio del slot (HH:MM).")
    end_time: str = Field(..., description="Hora de fin del slot (HH:MM).")

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = (
        "Crea el registro oficial en 'Master_Control_Orders.xlsx' en OneDrive. "
        "Genera un ID único correlativo (FL-2026-NNNN) para cada operación exitosa "
        "y asegura la persistencia de los datos logísticos."
    )
    args_schema: Type[BaseModel] = OrderManagementInput

    def _run(
        self, 
        dispatcher_email: str, 
        truck_plate: str, 
        driver_name: str, 
        fuel_volume: str, 
        assigned_island: str, 
        start_time: str, 
        end_time: str
    ) -> str:
        """Ejecuta el registro de la orden mediante la API de Microsoft Graph."""
        try:
            # Conexión con Microsoft 365
            account = get_ms_account()
            storage = account.storage()
            drive = storage.get_default_drive()
            
            folder_path = 'Fuel_Terminal_System'
            file_name = 'Master_Control_Orders.xlsx'
            full_path = f"{folder_path}/{file_name}"
            
            # 1. Obtener o inicializar el historial de órdenes
            try:
                file_item = drive.get_item_by_path(full_path)
                content = file_item.download()
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            except Exception:
                # Si el archivo no existe o está vacío, definimos la estructura base
                df = pd.DataFrame(columns=[
                    "OrderID", "Date", "Dispatcher", "Plate", "Driver", "Volume", "Island", "Start", "End"