import os
import requests
import time
from crewai.tools import BaseTool
from pydantic import Field

class CommunicationsTool(BaseTool):
    name: str = "communications_tool"
    description: str = "Envía correos electrónicos profesionales vía Microsoft Graph API (Outlook Business)."
    
    target_user: str = Field(default="soportesap@frontera-virtual.com")

    def _get_token(self):
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        
        if not all([client_id, client_secret, tenant_id]):
            return None

        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        # Forzamos headers y aumentamos timeout para el runner de GitHub
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        for _ in range(2):
            try:
                res = requests.post(url, data=data, headers=headers, timeout=30)
                if res.status_code != 200:
                    print(f"DEBUG AZURE ERROR (Comm): {res.text}")
                    continue
                return res.json().get('access_token')
            except Exception as e:
                print(f"DEBUG EXCEPTION (Comm): {str(e)}")
                time.sleep(2)
                continue
        return None

    def _run(self, recipient_email: str, subject: str, body: str) -> str:
        token = self._get_token()
        if not token: 
            return "ERROR_CONEXIÓN_MAIL_SERVER"
            
        url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/sendMail"
        
        raw_emails = str(recipient_email).replace(';', ',')
        email_list = [e.strip() for e in raw_emails.split(',') if '@' in e]
        
        if not email_list:
            return "ERROR: Sin destinatarios válidos."

        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body.replace('\n', '<br>')
                },
                "toRecipients": [
                    {"emailAddress": {"address": email}} for email in email_list
                ]
            },
            "saveToSentItems": "true"
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            res = requests.post(url, headers=headers, json=email_data, timeout=40)
            if res.status_code == 202:
                return f"ENVÍO_EXITOSO: Notificación enviada correctamente."
            else:
                return f"ERROR_GRAPH_API: {res.status_code} - {res.text}"
        except Exception as e:
            return f"ERROR_CRITICO_COMUNICACION: {str(e)}"