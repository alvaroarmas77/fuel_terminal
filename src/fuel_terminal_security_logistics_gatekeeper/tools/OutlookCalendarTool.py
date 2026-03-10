import os
from datetime import datetime, timedelta
from typing import Type, Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

class OutlookCalendarInput(BaseModel):
    """Esquema para reserva de espacios de carga."""
    requested_datetime: str = Field(..., description="Fecha y hora en formato ISO (YYYY-MM-DDTHH:MM:SS).")
    truck_plate: str = Field(..., description="Placa del camión para la reserva.")

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Gestiona la disponibilidad y reserva de islas de carga en el calendario de Outlook."
    args_schema: Type[BaseModel] = OutlookCalendarInput

    def _run(self, requested_datetime: str, truck_plate: str) -> str:
        try:
            dt_str = requested_datetime.replace(" ", "T")
            start_dt = datetime.fromisoformat(dt_str)
            end_dt = start_dt + timedelta(minutes=30)
            isla = "Isla_Carga_01"
            
            return f"RESERVA_CONFIRMADA|isla:{isla}|inicio:{start_dt.strftime('%H:%M')}|fin:{end_dt.strftime('%H:%M')}"
        except Exception as e:
            return f"ERROR_CALENDARIO: {str(e)}"