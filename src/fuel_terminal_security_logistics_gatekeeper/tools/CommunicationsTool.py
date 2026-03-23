import os
import requests
from crewai.tools import BaseTool
from pydantic import Field # Añadido para compatibilidad con CrewAI/Pydantic

class CommunicationsTool(BaseTool):
    name: str = "communications_tool"
    description: str = "Envía correos electrónicos profesionales vía Microsoft Graph API (Outlook Business)."
    
    # Campo definido con Field para evitar errores de validación en la instancia de CrewAI
    target_user: str = Field(default="soportesap@frontera-virtual.com")

    def _get_token(self):
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        
        # Validación preventiva de variables de entorno
        if not all([client_id, client_secret, tenant_id]):
            return None

        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        try:
            # Se añade timeout=20 para evitar desconexiones prematuras en la nube
            res = requests.post(url, data=data, timeout=20)
            return res.json().get('access_token')
        except:
            return None

    def _run(self, recipient_email: str, subject: str, body: str) -> str:
        token = self._get_token()
        if not token: 
            return "ERROR_CONEXIÓN_MAIL_SERVER"
            
        url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/sendMail"
        
        # Manejo de múltiples destinatarios (soporta comas o puntos y coma)
        raw_emails = str(recipient_email).replace(';', ',')
        email_list = [e.strip() for e in raw_emails.split(',') if '@' in e]
        
        if not email_list:
            return "ERROR: No se encontraron destinatarios válidos."

        # Construcción del payload para Microsoft Graph
        # Se mantiene tu lógica de conversión a HTML para las tablas de la Fase 5
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
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            # Se añade timeout=30 debido a que el envío de mail en Graph puede tardar
            res = requests.post(url, headers=headers, json=email_data, timeout=30)
            
            # Código 202 (Accepted) es el éxito estándar de Graph para sendMail
            if res.status_code == 202:
                return f"ENVÍO_EXITOSO: Notificación enviada a {len(email_list)} contacto(s)."
            else:
                return f"ERROR_GRAPH_API: {res.status_code} - {res.text}"
        except Exception as e:
            return f"ERROR_CRITICO_COMUNICACION: {str(e)}"