from datetime import datetime, timedelta
import os
import requests
from crewai.tools import BaseTool

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Reserva slots en calendarios de islas."

    def _get_token(self):
        token_url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': os.getenv('AZURE_CLIENT_ID'),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
            'scope': 'https://graph.microsoft.com/.default'
        }
        return requests.post(token_url, data=data).json().get('access_token')

    def _run(self, requested_datetime: str, plate_id: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_CONEXIÓN"
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        target_user = "soportesap@frontera-virtual.com"
        start_dt = datetime.fromisoformat(requested_datetime)
        end_dt = start_dt + timedelta(minutes=30)

        for i in range(1, 8):
            island_name = f"Terminal_Isla_{i}"
            # Lógica simplificada: En un entorno real buscaríamos el ID del calendario por nombre
            # Aquí intentamos crear el evento directamente en el calendario principal por brevedad técnica
            url = f"https://graph.microsoft.com/v1.0/users/{target_user}/calendar/events"
            event_data = {
                "subject": f"Carga: {plate_id} - {island_name}",
                "start": {"dateTime": start_dt.isoformat(), "timeZone": "SA Pacific Standard Time"},
                "end": {"dateTime": end_dt.isoformat(), "timeZone": "SA Pacific Standard Time"}
            }
            res = requests.post(url, headers=headers, json=event_data)
            if res.status_code == 201:
                return f"SLOT_RESERVADO: {island_name}"
        
        return "SLOT_OCUPADO"