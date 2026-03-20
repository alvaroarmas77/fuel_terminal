from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
try:
    from crewai.tools import BaseTool
except ImportError:
    from crewai_tools import BaseTool

class CommunicationsTool(BaseTool):
    name: str = "communications_tool"
    description: str = "Envía correos de confirmación o rechazo vía Outlook Business."

    def _run(self, recipient_email: str, subject: str, body: str) -> str:
        account = get_ms_account()
        if not account: return "ERROR_CONEXIÓN"
            
        try:
            target_user = "soportesap@frontera-virtual.com"
            # CRÍTICO: En modo Aplicación, se debe especificar el recurso (buzón)
            mailbox = account.mailbox(resource=target_user)
            message = mailbox.new_message()
            
            # Limpieza de destinatarios múltiples si existieran
            emails = [e.strip() for e in str(recipient_email).split(',')]
            message.to.add(emails)
            
            message.subject = subject
            message.body = body
            
            message.send()
            return f"ENVÍO_EXITOSO: Notificación enviada a {recipient_email}."
        except Exception as e:
            return f"ERROR_COMUNICACION: {str(e)}"