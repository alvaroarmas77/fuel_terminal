import pandas as pd
import io
import os
import requests
from crewai.tools import BaseTool

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = "Valida la identidad del despachador en la pestaña Authorized_Users de Master_Control.xlsx"

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
        if not token: return "ERROR_CONEXIÓN_AZURE"
        
        target_user = "soportesap@frontera-virtual.com"
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            # Endpoint directo al contenido para evitar dobles llamadas
            url = f"https://graph.microsoft.com/v1.0/users/{target_user}/drive/root:/Fuel_Terminal_System/Master_Control.xlsx:/content"
            res = requests.get(url, headers=headers)
            
            if res.status_code != 200:
                return f"ERROR_LECTURA_ARCHIVO: {res.status_code}"

            # Leer la pestaña específica de usuarios autorizados
            df = pd.read_excel(io.BytesIO(res.content), sheet_name="Authorized_Users")
            
            # Normalización estricta
            email_check = str(dispatcher_email).strip().lower()
            df['Email'] = df['Email'].astype(str).str.strip().lower()
            
            match = df[df['Email'] == email_check]
            
            if not match.empty:
                # Extraemos datos para el reporte de la Fase 1
                nombre = match.iloc[0].get('Nombre', 'Usuario')
                empresa = match.iloc[0].get('Empresa', 'Empresa Registrada')
                return f"PHASE_1_SUCCESS|Nombre:{nombre}|Empresa:{empresa}"
            
            # El prefijo RECHAZO_FASE_1 es crítico para la regla de detención en tasks.yaml
            return f"RECHAZO_FASE_1: El usuario {dispatcher_email} no tiene permisos de acceso."

        except Exception as e:
            return f"ERROR_SISTEMA_AUTH: {str(e)}"