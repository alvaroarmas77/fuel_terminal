import os
import requests
from crewai.tools import BaseTool

class CommunicationsTool(BaseTool):
    name: str = "communications_tool"
    description: str = "Envía correos electrónicos profesionales vía Microsoft Graph API (Outlook Business)."

    def _get_token(self):
        url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': os.getenv('AZURE_CLIENT_ID'),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
            'scope': 'https://graph.microsoft.com/.default'
        }
        res = requests.post(url, data=data)
        return res.json().get('access_token')

    def _run(self, recipient_email: str, subject: str, body: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_CONEXIÓN_MAIL_SERVER"
            
        target_user = "soportesap@frontera-virtual.com"
        url = f"https://graph.microsoft.com/v1.0/users/{target_user}/sendMail"
        
        # Manejo de múltiples destinatarios si vienen separados por coma
        raw_emails = str(recipient_email).replace(';', ',')
        email_list = [e.strip() for e in raw_emails.split(',') if '@' in e]
        
        if not email_list:
            return "ERROR: No se encontraron destinatarios válidos."

        # Construcción del payload para Microsoft Graph
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML", # Cambiado a HTML para soportar las tablas de la Fase 5
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
            res = requests.post(url, headers=headers, json=email_data)
            # 202 es el código de éxito para envío de correo en Graph API
            if res.status_code == 202:
                return f"ENVÍO_EXITOSO: Notificación enviada a {len(email_list)} contacto(s)."
            else:
                return f"ERROR_GRAPH_API: {res.status_code} - {res.text}"
        except Exception as e:
            return f"ERROR_CRITICO_COMUNICACION: {str(e)}"