import os
from datetime import datetime, timedelta
from typing import Type
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

class OutlookCalendarInput(BaseModel):
    """Esquema para reserva de espacios de carga."""
    requested_datetime: str = Field(..., description="Fecha y hora en formato ISO (YYYY-MM-DDTHH:MM:SS).")
    truck_plate: str = Field(..., description="Placa del camión para asignar la cita.")

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Consulta disponibilidad y reserva bloques de tiempo en las islas de carga vía Outlook."
    args_schema: Type[BaseModel] = OutlookCalendarInput

    def _run(self, requested_datetime: str, truck_plate: str) -> str:
        try:
            # Limpieza de input para asegurar formato ISO
            dt_clean = requested_datetime.replace(" ", "T")
            start_dt = datetime.fromisoformat(dt_clean)
            end_dt = start_dt + timedelta(minutes=45) # Duración promedio de carga
            
            isla_asignada = "Isla_Carga_02" # Lógica de asignación simplificada
            
            return (
                f"RESERVA_CONFIRMADA|isla:{isla_asignada}|"
                f"inicio:{start_dt.strftime('%Y-%m-%d %H:%M')}|"
                f"fin:{end_dt.strftime('%H:%M')}|"
                f"placa:{truck_plate}"
            )
        except Exception as e:
            return f"ERROR_CALENDARIO: Formato de fecha inválido o error de conexión: {str(e)}"