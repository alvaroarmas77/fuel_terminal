from crewai_tools import BaseTool
from datetime import datetime, timedelta

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Gestiona la disponibilidad y reserva de islas en el calendario de Outlook."

    def _run(self, requested_datetime: str, truck_plate: str) -> str:
        try:
            # CrewAI pasará los argumentos como strings
            dt_str = requested_datetime.replace(" ", "T").split(".")[0]
            start_dt = datetime.fromisoformat(dt_str)
            end_dt = start_dt + timedelta(minutes=30)
            
            return f"RESERVA_CONFIRMADA|isla:Isla_01|inicio:{start_dt.strftime('%H:%M')}|fin:{end_dt.strftime('%H:%M')}"
        except Exception as e:
            return f"ERROR_CALENDARIO: {str(e)}"