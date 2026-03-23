import pandas as pd
import io
import os
import requests
from crewai.tools import BaseTool
from pydantic import Field # Añadido para compatibilidad con CrewAI/Pydantic

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = "Valida la identidad del despachador en la pestaña Authorized_Users de Master_Control.xlsx"
    
    # Arreglo para evitar errores de validación en CrewAI
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
            # Añadido timeout para evitar el error de "Server disconnected"
            res = requests.post(url, data=data, timeout=20)
            return res.json().get('access_token')
        except:
            return None

    def _run(self, dispatcher_email: str) -> str:
        token = self._get_token()
        if not token: 
            return "ERROR_CONEXIÓN_AZURE"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        try:
            # Endpoint optimizado
            url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/drive/root:/Fuel_Terminal_System/Master_Control.xlsx:/content"
            
            # Añadido timeout y verificación de errores de red
            res = requests.get(url, headers=headers, timeout=30)
            
            if res.status_code != 200:
                return f"ERROR_LECTURA_ARCHIVO: {res.status_code}"

            # Procesamiento de Excel con motor robusto
            # Se usa openpyxl para asegurar compatibilidad con .xlsx en Linux
            df = pd.read_excel(io.BytesIO(res.content), sheet_name="Authorized_Users", engine='openpyxl')
            
            # Normalización estricta de entrada y columnas
            email_check = str(dispatcher_email).strip().lower()
            df.columns = [str(c).strip() for c in df.columns] # Limpieza de nombres de columnas
            
            if 'Email' not in df.columns:
                return "ERROR_ESTRUCTURA: Columna 'Email' no encontrada en el Excel."

            df['Email'] = df['Email'].astype(str).str.strip().lower()
            
            match = df[df['Email'] == email_check]
            
            if not match.empty:
                # Uso de .get() seguro para evitar KeyErrors
                nombre = match.iloc[0].get('Nombre', 'Usuario')
                empresa = match.iloc[0].get('Empresa', 'Empresa Registrada')
                return f"PHASE_1_SUCCESS|Nombre:{nombre}|Empresa:{empresa}"
            
            return f"RECHAZO_FASE_1: El usuario {dispatcher_email} no tiene permisos de acceso."

        except Exception as e:
            return f"ERROR_SISTEMA_AUTH: {str(e)}"