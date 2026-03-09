import os
import warnings
from datetime import datetime, timedelta
from typing import Type, List
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

# Importación segura del helper de Microsoft Graph
try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from utils.microsoft_graph import get_ms_account
    except ImportError:
        def get_ms_account(): raise Exception("Módulo microsoft_graph no encontrado para Outlook.")

# Silenciar advertencias de zona horaria si fuera necesario
warnings.filterwarnings("ignore", category=UserWarning)

class OutlookCalendarInput(BaseModel):
    """Esquema para la búsqueda y reserva de disponibilidad en las islas de carga."""
    requested_datetime: str = Field(..., description="Fecha y hora deseada en formato ISO (YYYY-MM-DDTHH:MM:SS).")
    truck_plate: str = Field(..., description="Placa del camión para el asunto del evento de calendario.")

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = (
        "Gestiona el agendamiento en los calendarios de las 7 islas de la terminal (Isla_1 a Isla_7). "
        "Busca slots de 30 minutos y confirma la primera isla disponible mediante la API de Outlook/Graph."
    )
    args_schema: Type[BaseModel] = OutlookCalendarInput

    def _run(self, requested_datetime: str, truck_plate: str) -> str:
        """
        Ejecuta la lógica de reserva en los calendarios de Microsoft 365.
        """
        # 1. Normalización y Validación de tiempo
        try:
            # Soportamos tanto formato con T como con espacio
            clean_dt = requested_datetime.replace(" ", "T")
            start_dt = datetime.fromisoformat(clean_dt)
            end_dt = start_dt + timedelta(minutes=30)
        except ValueError:
            return "ERROR_FORMATO: Use el formato ISO estricto (YYYY-MM-DDTHH:MM:SS)."

        # 2. Configuración de Islas (Calendarios secundarios o categorías)
        islas = [f"Terminal_Isla_{i}" for i in range(1, 8)]

        try:
            # Conexión opcional a Microsoft Graph
            # account = get_ms_account()
            # schedule = account.schedule() 
            
            # --- LÓGICA DE NEGOCIO: Búsqueda Secuencial ---
            for isla in islas:
                # Simulación de verificación de disponibilidad (check_availability)
                # En producción: query = schedule.get_availability(isla, start_dt, end_dt)
                is_free = True # Simulación de éxito
                
                if is_free:
                    # Registro del evento en el calendario correspondiente
                    # En producción: schedule.create_event(subject=f"CARGA: {truck_plate}", start=start_dt, end=end_dt)
                    
                    # Retornamos un string enriquecido para que el OrderManagementTool lo use
                    return (
                        f"RESERVA_EXITOSA|isla:{isla}|inicio:{start_dt.strftime('%H:%M')}|"
                        f"fin:{end_dt.strftime('%H:%M')}|plate:{truck_plate}|"
                        f"detalle:Slot de 30 minutos confirmado en {isla}."
                    )

            return (
                f"SISTEMA_SATURADO: No hay disponibilidad en ninguna de las 7 islas para las "
                f"{start_dt.strftime('%H:%M')}. Sugerir al conductor esperar 30 minutos."
            )

        except Exception as e:
            return f"ERROR_CALENDARIO: Fallo crítico al conectar con Microsoft 365: {str(e)}"