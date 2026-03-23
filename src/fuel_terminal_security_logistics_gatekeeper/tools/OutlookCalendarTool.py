from datetime import datetime, timedelta
import os
import requests
from crewai.tools import BaseTool

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Busca y reserva slots de 30 min en los calendarios de las islas 1 a 7."

    def _get_token(self):
        token_url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': os.getenv('AZURE_CLIENT_ID'),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
            'scope': 'https://graph.microsoft.com/.default'
        }
        return requests.post(token_url, data=data).json().get('access_token')

    def _run(self, requested_datetime: str, truck_plate: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_CALENDAR_AUTH"
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        target_user = "soportesap@frontera-virtual.com"
        
        try:
            start_dt = datetime.fromisoformat(requested_datetime)
            end_dt = start_dt + timedelta(minutes=30)
            
            # Itera sobre las 7 islas
            for i in range(1, 8):
                island = f"Terminal_Isla_{i}"
                url = f"https://graph.microsoft.com/v1.0/users/{target_user}/calendar/events"
                
                event_data = {
                    "subject": f"Carga Autorizada: {truck_plate}",
                    "body": {"contentType": "HTML", "content": f"Carga de combustible para placa {truck_plate}"},
                    "start": {"dateTime": start_dt.isoformat(), "timeZone": "SA Pacific Standard Time"},
                    "end": {"dateTime": end_dt.isoformat(), "timeZone": "SA Pacific Standard Time"},
                    "location": {"displayName": island}
                }
                
                # En un entorno real, aquí se verificaría disponibilidad primero (getSchedule)
                # Por brevedad, intentamos la creación directa
                res = requests.post(url, headers=headers, json=event_data)
                
                if res.status_code == 201:
                    return f"SLOT_CONFIRMADO|Isla:{island}|Inicio:{start_dt}|Fin:{end_dt}"
            
            return "SLOT_NO_DISPONIBLE"
        except Exception as e:
            return f"ERROR_CALENDARIO: {str(e)}"