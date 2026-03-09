import os
from datetime import datetime, timedelta
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class OutlookCalendarInput(BaseModel):
    """Esquema para la búsqueda de disponibilidad en las islas de carga."""
    requested_datetime: str = Field(..., description="Fecha y hora deseada en formato ISO (YYYY-MM-DDTHH:MM:SS).")
    truck_plate: str = Field(..., description="Placa del camión para el asunto del evento de calendario.")

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = (
        "Gestiona el agendamiento en los 7 calendarios de islas de la terminal (Terminal_Isla_1 a 7). "
        "Busca slots de 30 minutos y confirma la primera isla disponible."
    )
    args_schema: Type[BaseModel] = OutlookCalendarInput

    def _run(self, requested_datetime: str, truck_plate: str) -> str:
        # 1. Normalización de tiempo
        try:
            # Intentar parsear el string a objeto datetime
            start_dt = datetime.fromisoformat(requested_datetime)
        except ValueError:
            return "ERROR: Formato de fecha inválido. Por favor use el formato ISO: YYYY-MM-DDTHH:MM:SS."
        
        # Definir el fin del slot (estrictamente 30 minutos después)
        end_dt = start_dt + timedelta(minutes=30)
        
        # Lista dinámica de las 7 islas de carga
        islas = [f"Terminal_Isla_{i}" for i in range(1, 8)]
        
        # 2. Lógica de verificación de disponibilidad
        # NOTA: En producción, aquí se integra el cliente de Microsoft Graph
        for isla in islas:
            # Simulamos que la lógica de negocio encuentra la primera isla libre
            # is_free = graph_service.check(isla, start_dt, end_dt)
            is_free = True 
            
            if is_free:
                # Simulamos la creación del evento
                # graph_service.create_event(isla, f"Carga: {truck_plate}", start_dt, end_dt)
                
                return (
                    f"CONFIRMADO: Slot de 30 min encontrado y reservado en {isla}. "
                    f"Horario: {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}. "
                    f"Referencia: {truck_plate}."
                )

        # 3. Respuesta en caso de saturación de todas las islas
        return (
            f"NO_DISPONIBLE: Todas las islas están ocupadas para las {start_dt.strftime('%H:%M')}. "
            "Sugerencia: Intente solicitar un bloque 30 minutos después o consulte disponibilidad general."
        )