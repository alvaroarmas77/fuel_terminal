import pandas as pd
import io
import os
import warnings
from datetime import datetime
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# Silenciar advertencias de openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from utils.microsoft_graph import get_ms_account
    except ImportError:
        def get_ms_account(): return None

class OrderManagementInput(BaseModel):
    """Esquema para el registro final de la orden de carga."""
    dispatcher_email: str = Field(..., description="Email del despachador.")
    truck_plate: str = Field(..., description="Placa del camión.")
    driver_name: str = Field(..., description="Nombre del conductor.")
    fuel_volume: str = Field(..., description="Volumen (ej. 5000 Gal).")
    assigned_island: str = Field(..., description="Isla asignada.")
    start_time: str = Field(..., description="Hora inicio.")
    end_time: str = Field(..., description="Hora fin.")

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = "Registra órdenes en Master_Control_Orders.xlsx en OneDrive."
    args_schema: Type[BaseModel] = OrderManagementInput

    def _run(self, dispatcher_email: str, truck_plate: str, driver_name: str, 
             fuel_volume: str, assigned_island: str, start_time: str, end_time: str) -> str:
        try:
            account = get_ms_account()
            if not account: return "ERROR: No hay conexión con MS Graph."
            
            drive = account.storage().get_default_drive()
            full_path = 'Fuel_Terminal_System/Master_Control_Orders.xlsx'
            
            try:
                file_item = drive.get_item_by_path(full_path)
                content = file_item.download()
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            except Exception:
                df = pd.DataFrame(columns=["OrderID", "Date", "Dispatcher", "Plate", "Driver", "Volume", "Island", "Start", "End"])

            # Generar ID
            new_id = f"FL-2026-{len(df) + 1:04d}"
            
            # Crear nueva entrada (Cierre exacto de diccionario)
            new_entry = {
                "OrderID": new_id,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Dispatcher": dispatcher_email,
                "Plate": truck_plate,
                "Driver": driver_name,
                "Volume": fuel_volume,
                "Island": assigned_island,
                "Start": start_time,
                "End": end_time
            }

            # Concatenación corregida (Cierre exacto de listas y funciones)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

            # Buffer de salida
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            # Subida
            target_folder = drive.get_item_by_path('Fuel_Terminal_System')
            target_folder.upload(output.getvalue(), name='Master_Control_Orders.xlsx')
            
            return f"EXITO: Orden {new_id} registrada."

        except Exception as e:
            return f"ERROR_CRITICO: {str(e)}"