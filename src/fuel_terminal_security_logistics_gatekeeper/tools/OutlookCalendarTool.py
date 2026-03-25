from datetime import datetime, timedelta
import os
import requests
import urllib.parse
import time
from crewai.tools import BaseTool
from pydantic import Field

class OutlookCalendarTool(BaseTool):
    name: str = "outlook_calendar_tool"
    description: str = "Busca y reserva slots de 30 min en los calendarios de las islas 1 a 7."
    
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
        for _ in range(2):
            try:
                res = requests.post(token_url, data=data, timeout=25)
                return res.json().get('access_token')
            except:
                time.sleep(2)
                continue
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
            start_dt = datetime.fromisoformat(requested_datetime.replace('Z', ''))
            end_dt = start_dt + timedelta(minutes=30)
            
            start_search = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_search = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            for i in range(1, 8):
                island = f"Terminal_Isla_{i}"
                
                check_url = (
                    f"https://graph.microsoft.com/v1.0/users/{self.target_user}/calendar/events"
                    f"?$filter=start/dateTime ge '{start_search}' and end/dateTime le '{end_search}'"
                )
                
                res_check = requests.get(check_url, headers=headers, timeout=30)
                
                if res_check.status_code == 200:
                    eventos = res_check.json().get('value', [])
                    isla_ocupada = any(
                        ev.get('location', {}).get('displayName') == island 
                        for ev in eventos
                    )
                    if isla_ocupada: continue
                
                # RESERVA
                url_post = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/calendar/events"
                
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
                
                res_post = requests.post(url_post, headers=headers, json=event_data, timeout=35)
                
                if res_post.status_code == 201:
                    return f"SLOT_CONFIRMADO|Isla:{island}|Inicio:{start_dt.isoformat()}|Fin:{end_dt.isoformat()}"
            
            return "SLOT_NO_DISPONIBLE: Todas las islas están ocupadas en el horario solicitado."
            
        except Exception as e:
            return f"ERROR_CALENDARIO: {str(e)}"