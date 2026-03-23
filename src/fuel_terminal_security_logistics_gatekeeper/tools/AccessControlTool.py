import pandas as pd
import io
import os
import requests
import urllib.parse
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class AccessControlInput(BaseModel):
    """Esquema para asegurar que el agente solo envíe un string de email."""
    dispatcher_email: str = Field(..., description="Email del despachador a validar.")

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = "Valida la identidad del despachador en la pestaña Authorized_Users de Master_Control.xlsx"
    args_schema: Type[BaseModel] = AccessControlInput

    target_user: str = Field(default="soportesap@frontera-virtual.com")

    def _get_token(self):
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        if not all([client_id, client_secret, tenant_id]): return None

        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        try:
            res = requests.post(url, data=data, timeout=20)
            return res.json().get('access_token')
        except: return None

    def _run(self, dispatcher_email: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_CONEXIÓN_AZURE"
        
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        
        try:
            path_file = "Fuel_Terminal_System/Master_Control.xlsx"
            encoded_path = urllib.parse.quote(path_file)
            url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/drive/root:/{encoded_path}:/content"
            
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code != 200: return f"ERROR_LECTURA_ARCHIVO: {res.status_code}"

            df = pd.read_excel(io.BytesIO(res.content), sheet_name="Authorized_Users", engine='openpyxl')
            
            # Normalización de columnas
            df.columns = [str(c).strip() for c in df.columns]
            if 'Email' not in df.columns: return "ERROR_ESTRUCTURA: Columna 'Email' no encontrada."

            # BLINDAJE ANTI-ERROR 'Series' lower:
            # 1. Forzamos conversión a string y llenamos vacíos
            # 2. Usamos .str para procesar la columna como texto
            df['Email'] = df['Email'].fillna('').astype(str).str.strip().lower()
            email_check = str(dispatcher_email).strip().lower()

            match = df[df['Email'] == email_check]
            
            if not match.empty:
                nombre = match.iloc[0].get('Nombre', 'Usuario')
                empresa = match.iloc[0].get('Empresa', 'Empresa Registrada')
                return f"PHASE_1_SUCCESS|Nombre:{nombre}|Empresa:{empresa}"
            
            return f"RECHAZO_FASE_1: El usuario {dispatcher_email} no tiene permisos de acceso."

        except Exception as e:
            return f"ERROR_SISTEMA_AUTH: {str(e)}"