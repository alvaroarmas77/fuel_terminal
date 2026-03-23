from datetime import datetime, timedelta
import os
import requests
from crewai.tools import BaseTool
from pydantic import Field # Añadido para compatibilidad con CrewAI

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Busca y reserva slots de 30 min en los calendarios de las islas 1 a 7."
    
    # Definido como Field para evitar errores de validación en la instancia de CrewAI
    target_user: str = Field(default="soportesap@frontera-virtual.com")

    def _get_token(self):
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        
        if not all([client_id, client_secret, tenant_id]):
            return None

        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        try:
            # Se añade timeout=20 para evitar el error de "Server disconnected" en GitHub
            res = requests.post(token_url, data=data, timeout=20)
            return res.json().get('access_token')
        except:
            return None

    def _run(self, requested_datetime: str, truck_plate: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_CALENDAR_AUTH"
        
        headers = {
            'Authorization': f'Bearer {token}', 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            # Normalización de la fecha solicitada
            start_dt = datetime.fromisoformat(requested_datetime.replace('Z', ''))
            end_dt = start_dt + timedelta(minutes=30)
            
            # Itera sobre las 7 islas (mantenemos tu flujo original)
            for i in range(1, 8):
                island = f"Terminal_Isla_{i}"
                url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/calendar/events"
                
                event_data = {
                    "subject": f"Carga Autorizada: {truck_plate}",
                    "body": {
                        "contentType": "HTML", 
                        "content": f"Carga de combustible para placa {truck_plate}. Registrado por Gatekeeper System."
                    },
                    "start": {"dateTime": start_dt.isoformat(), "timeZone": "SA Pacific Standard Time"},
                    "end": {"dateTime": end_dt.isoformat(), "timeZone": "SA Pacific Standard Time"},
                    "location": {"displayName": island}
                }
                
                # Se añade timeout=30 para dar margen a la API de Microsoft en la nube
                res = requests.post(url, headers=headers, json=event_data, timeout=30)
                
                # 201 es el código de éxito de creación en Graph API
                if res.status_code == 201:
                    return f"SLOT_CONFIRMADO|Isla:{island}|Inicio:{start_dt.isoformat()}|Fin:{end_dt.isoformat()}"
            
            return "SLOT_NO_DISPONIBLE"
        except Exception as e:
            return f"ERROR_CALENDARIO: {str(e)}"