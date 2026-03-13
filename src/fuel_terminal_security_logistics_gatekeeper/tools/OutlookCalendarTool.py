import sys
import os
from datetime import datetime, timedelta
try:
    from crewai_tools import BaseTool
except ImportError:
    try:
        from crewai.tools import BaseTool
    except ImportError:
        from crewai.tools.base_tool import BaseTool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
    except ImportError:
        def get_ms_account(): return None

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Verifica disponibilidad en las 7 islas (Terminal_Isla_1 a 7) y reserva slots de 30 min."

    def _run(self, requested_datetime: str, plate_id: str) -> str:
        account = get_ms_account()
        if not account:
            return "ERROR_CONEXIÓN: No se pudo acceder a la cuenta para verificar calendarios."

        try:
            schedule = account.schedule()
            start_dt = datetime.fromisoformat(requested_datetime)
            end_dt = start_dt + timedelta(minutes=30)
            islands = [f"Terminal_Isla_{i}" for i in range(1, 8)]
            
            for island_name in islands:
                try:
                    calendar = schedule.get_calendar(calendar_name=island_name)
                    events = calendar.get_events(query=f"start/dateTime ge '{start_dt.isoformat()}' and end/dateTime le '{end_dt.isoformat()}'")
                    
                    if not any(events):
                        new_event = calendar.new_event()
                        new_event.subject = f"Carga Combustible: {plate_id}"
                        new_event.start = start_dt
                        new_event.end = end_dt
                        new_event.save()
                        return f"SLOT_RESERVADO: Isla: {island_name}, Inicio: {start_dt.strftime('%H:%M')}, Fin: {end_dt.strftime('%H:%M')}"
                except Exception:
                    continue
            
            return "SLOT_OCUPADO: No se encontraron espacios disponibles en ninguna de las 7 islas para ese horario."
        except Exception as e:
            return f"ERROR_CALENDARIO: {str(e)}"