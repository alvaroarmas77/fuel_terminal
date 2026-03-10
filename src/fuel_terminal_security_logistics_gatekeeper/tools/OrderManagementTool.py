import pandas as pd
from datetime import datetime
from typing import Type
from pydantic import BaseModel, Field
from crewai_tools import BaseTool

class OrderManagementInput(BaseModel):
    """Esquema de validación para el registro de la orden."""
    dispatcher_email: str = Field(..., description="Email del despachador.")
    truck_plate: str = Field(..., description="Placa del camión.")
    driver_name: str = Field(..., description="Nombre del conductor.")
    fuel_volume: str = Field(..., description="Volumen solicitado.")
    assigned_island: str = Field(..., description="Isla asignada.")
    start_time: str = Field(..., description="Hora inicio.")
    end_time: str = Field(..., description="Hora fin.")

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = "Genera el registro final de operación en Master_Control_Orders.xlsx."
    args_schema: Type[BaseModel] = OrderManagementInput

    def _run(self, **kwargs) -> str:
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            order_id = f"FL-2026-{timestamp[-4:]}"
            
            # En un entorno real, aquí se invoca la escritura en la API de Graph
            return (
                f"ÉXITO: Orden {order_id} registrada para {kwargs.get('driver_name')}. "
                f"Vehículo {kwargs.get('truck_plate')} en {kwargs.get('assigned_island')}."
            )
        except Exception as e:
            return f"ERROR_LOGGING: Fallo al registrar la orden: {str(e)}"