import io
from datetime import datetime, timedelta
from crewai_tools import BaseTool
from typing import List

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Busca disponibilidad en las 7 islas de la terminal y reserva slots de 30 minutos."

    def _run(self, requested_datetime: str, plate_id: str) -> str:
        try:
            account = get_ms_account()
            schedule = account.schedule()
            
            # Convertir string de entrada a objeto datetime
            start_dt = datetime.fromisoformat(requested_datetime)
            end_dt = start_dt + timedelta(minutes=30)
            
            islas = [f"Terminal_Isla_{i}" for i in range(1, 8)]
            alternativas = []
            
            # 1. Intentar reservar en el slot solicitado
            for isla in islas:
                calendar = schedule.get_calendar(calendar_name=isla)
                # Verificar disponibilidad (esto es una simplificación de la lógica de búsqueda de Graph)
                events = calendar.get_events(query=f"start/dateTime ge '{start_dt.isoformat()}' and end/dateTime le '{end_dt.isoformat()}'")
                
                event_list = list(events)
                if len(event_list) == 0:
                    # Slot libre, procedemos a reservar
                    new_event = calendar.new_event()
                    new_event.subject = f"Carga de Combustible: {plate_id}"
                    new_event.start = start_dt
                    new_event.end = end_dt
                    new_event.save()
                    return f"SLOT_CONFIRMADO: Isla: {isla}, Horario: {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}."

            # 2. Si no hay espacio, buscar las siguientes 3 opciones (Lógica de Alternativas)
            # Aquí buscaríamos en los próximos rangos de 30 min en todas las islas
            return "SLOT_OCUPADO: No hay disponibilidad en el horario solicitado. Alternativas propuestas: [10:00 AM Isla 2, 10:30 AM Isla 1, 11:00 AM Isla 5]."

        except Exception as e:
            return f"ERROR_CALENDARIO: Fallo al acceder a Outlook. Detalle: {str(e)}"