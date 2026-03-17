from datetime import datetime, timedelta
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account

try:
    from crewai_tools import BaseTool
except ImportError:
    from crewai.tools import BaseTool

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Reserva slots en los calendarios de las islas."

    def _run(self, requested_datetime: str, plate_id: str) -> str:
        account = get_ms_account()
        try:
            # CAMBIO: Especificar el recurso del calendario
            target_user = "logistica@tu-empresa.com"
            schedule = account.schedule(resource=target_user)
            
            start_dt = datetime.fromisoformat(requested_datetime)
            end_dt = start_dt + timedelta(minutes=30)
            
            islands = [f"Terminal_Isla_{i}" for i in range(1, 8)]
            
            for island_name in islands:
                try:
                    calendar = schedule.get_calendar(calendar_name=island_name)
                    events = calendar.get_events(query=f"start/dateTime ge '{start_dt.isoformat()}'")
                    
                    if not any(events):
                        new_event = calendar.new_event()
                        new_event.subject = f"Carga: {plate_id}"
                        new_event.start = start_dt
                        new_event.end = end_dt
                        new_event.save()
                        return f"SLOT_RESERVADO: Isla: {island_name}."
                except: continue
            
            return "SLOT_OCUPADO: Sin disponibilidad."
        except Exception as e:
            return f"ERROR_CALENDARIO: {str(e)}"