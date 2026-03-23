import os
import requests
from crewai.tools import BaseTool

class CommunicationsTool(BaseTool):
    name: str = "communications_tool"
    description: str = "Envía correos de confirmación o rechazo vía Outlook Business."

    def _get_token(self):
        url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': os.getenv('AZURE_CLIENT_ID'),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
            'scope': 'https://graph.microsoft.com/.default'
        }
        return requests.post(url, data=data).json().get('access_token')

    def _run(self, recipient_email: str, subject: str, body: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_CONEXIÓN"
            
        target_user = "soportesap@frontera-virtual.com"
        url = f"https://graph.microsoft.com/v1.0/users/{target_user}/sendMail"
        
        emails = [e.strip() for e in str(recipient_email).split(',')]
        
        email_data = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": email}} for email in emails]
            }
        }
        
        res = requests.post(url, headers={'Authorization': f'Bearer {token}'}, json=email_data)
        if res.status_code == 202:
            return f"ENVÍO_EXITOSO: Notificación enviada a {recipient_email}."
        return f"ERROR_COMUNICACION: {res.text}"