import os
import sys
from O365 import Account, FileSystemTokenBackend
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account #

try:
    from crewai_tools import BaseTool
except ImportError:
    from crewai.tools import BaseTool

class CommunicationsTool(BaseTool):
    name: str = "communications_tool"
    description: str = "Envía notificaciones por correo a despachadores y conductores vía Outlook."

    def _run(self, recipient_email: str, subject: str, body: str) -> str:
        account = get_ms_account()
        if not account:
            return "ERROR_CONEXIÓN: No se pudo enviar el correo por falta de autenticación."

        try:
            message = account.new_message()
            message.to.add(recipient_email)
            message.subject = subject
            message.body = body
            message.send()
            return f"ENVÍO_EXITOSO: Correo enviado a {recipient_email}."
        except Exception as e:
            return f"ERROR_COMUNICACIÓN: {str(e)}"