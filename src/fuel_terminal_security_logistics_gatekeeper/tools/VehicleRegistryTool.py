import pandas as pd
import io
import os
import requests
from datetime import datetime
try:
    from crewai.tools import BaseTool
except ImportError:
    from crewai_tools import BaseTool

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Valida placa y conductor en la pestaña Vehicle_registry de Master_Control.xlsx"

    def _get_token(self):
        token_url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': os.getenv('AZURE_CLIENT_ID'),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
            'scope': 'https://graph.microsoft.com/.default'
        }
        res = requests.post(token_url, data=data)
        return res.json().get('access_token')

    def _run(self, plate_id: str, driver_name: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_CONEXIÓN"
        
        headers = {'Authorization': f'Bearer {token}'}
        target_user = "soportesap@frontera-virtual.com"
        
        try:
            # Endpoint para descargar el archivo Master_Control.xlsx desde OneDrive del target_user
            url = f"https://graph.microsoft.com/v1.0/users/{target_user}/drive/root:/Fuel_Terminal_System/Master_Control.xlsx:/content"
            
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                return f"ERROR_LECTURA_ARCHIVO: {res.status_code}"

            content = res.content
            df = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry")
            
            # Normalización para búsqueda exacta
            p_limpia = str(plate_id).strip().upper()
            d_limpio = str(driver_name).strip().lower()
            
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().upper()
            df['Driver Name'] = df['Driver Name'].astype(str).str.strip().lower()
            
            match = df[(df['Truck Plate'] == p_limpia) & (df['Driver Name'] == d_limpio)]
            
            if not match.empty:
                return "PHASE_2_SUCCESS"
            else:
                return "VEHÍCULO_O_CONDUCTOR_NO_REGISTRADO"

        except Exception as e:
            return f"ERROR_OPERATIVO: {str(e)}"