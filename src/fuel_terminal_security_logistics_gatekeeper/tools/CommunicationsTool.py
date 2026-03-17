from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account

try:
    from crewai_tools import BaseTool
except ImportError:
    from crewai.tools import BaseTool

class CommunicationsTool(BaseTool):
    name: str = "communications_tool"
    description: str = "Envía correos vía Outlook."

    def _run(self, recipient_email: str, subject: str, body: str) -> str:
        account = get_ms_account()
        try:
            target_user = "soportesap@frontera-virtual.com"
            mailbox = account.mailbox(target_user)
            message = mailbox.new_message()
            message.to.add(recipient_email)
            message.subject = subject
            message.body = body
            message.send()
            return f"ENVÍO_EXITOSO a {recipient_email}."
        except Exception as e:
            return f"ERROR_MAIL: {str(e)}"