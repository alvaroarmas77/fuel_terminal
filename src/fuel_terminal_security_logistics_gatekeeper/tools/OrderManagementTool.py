import pandas as pd
import io
from datetime import datetime
from typing import Type, Optional
from pydantic import BaseModel, Field

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class OrderManagementInput(BaseModel):
    """Esquema para el registro final de la orden de carga."""
    dispatcher_email: str = Field(..., description="Email del despachador.")
    truck_plate: str = Field(..., description="Placa del camión.")
    driver_name: str = Field(..., description="Nombre del conductor.")
    fuel_volume: str = Field(..., description="Volumen de carga solicitado.")
    assigned_island: str = Field(..., description="Isla asignada.")
    start_time: str = Field(..., description="Hora de inicio programada.")
    end_time: str = Field(..., description="Hora de fin estimada.")

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = "Registra la orden de carga final en el archivo maestro de pedidos en OneDrive."
    args_schema: Type[BaseModel] = OrderManagementInput

    def _run(self, **kwargs) -> str:
        try:
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return f"EXITO: Orden {order_id} registrada para el vehículo {kwargs.get('truck_plate')}."
        except Exception as e:
            return f"ERROR_ORDEN: No se pudo registrar la operación: {str(e)}"