import pandas as pd
import io
import os
import requests
from crewai.tools import BaseTool

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = "Valida la identidad del despachador en Master_Control.xlsx"

    def _get_token(self):
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        res = requests.post(url, data=data)
        return res.json().get('access_token')

    def _run(self, dispatcher_email: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_CONEXIÓN"
        
        target_user = "soportesap@frontera-virtual.com"
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            # Buscar el archivo en la ruta específica
            search_url = f"https://graph.microsoft.com/v1.0/users/{target_user}/drive/root:/Fuel_Terminal_System/Master_Control.xlsx"
            file_info = requests.get(search_url, headers=headers).json()
            download_url = file_info.get('@microsoft.graph.downloadUrl')
            
            content = requests.get(download_url).content
            df = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users")
            
            email_check = str(dispatcher_email).strip().lower()
            df['Email'] = df['Email'].astype(str).str.strip().lower()
            
            match = df[df['Email'] == email_check]
            if not match.empty:
                return "PHASE_1_SUCCESS"
            return f"RECHAZO_FASE_1: El correo {dispatcher_email} no está autorizado."
        except Exception as e:
            return f"ERROR_SISTEMA: {str(e)}"