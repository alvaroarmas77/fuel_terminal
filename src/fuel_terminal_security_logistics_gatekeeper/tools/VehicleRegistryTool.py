import pandas as pd
import io
import os
import requests
from crewai.tools import BaseTool

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Consulta la base de datos de vehículos autorizados usando la placa (truck_plate)."

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

    def _run(self, truck_plate: str, driver_name: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_AUTH"
        
        headers = {'Authorization': f'Bearer {token}'}
        target_user = "soportesap@frontera-virtual.com"
        
        try:
            url = f"https://graph.microsoft.com/v1.0/users/{target_user}/drive/root:/Fuel_Terminal_System/Master_Control.xlsx:/content"
            res = requests.get(url, headers=headers)
            
            if res.status_code != 200:
                return "ERROR_ARCHIVO_NO_ENCONTRADO"

            # Leer pestaña específica
            df = pd.read_excel(io.BytesIO(res.content), sheet_name="Vehicle_Registry")
            
            # Limpieza de datos para búsqueda robusta
            tp_search = str(truck_plate).strip().upper()
            dn_search = str(driver_name).strip().lower()
            
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().upper()
            df['Driver Name'] = df['Driver Name'].astype(str).str.strip().lower()
            
            # Buscamos coincidencias
            match = df[(df['Truck Plate'] == tp_search) & (df['Driver Name'] == dn_search)]
            
            if not match.empty:
                # Extraemos datos adicionales para la Fase 5
                email_conductor = match.iloc[0]['Driver_Email']
                id_interno = match.iloc[0]['ID_Interno']
                return f"PHASE_2_SUCCESS|Email:{email_conductor}|ID:{id_interno}"
            
            return "RECHAZO_FASE_2: El vehículo o conductor no están autorizados o los documentos han expirado."

        except Exception as e:
            return f"ERROR_SISTEMA_REGISTRO: {str(e)}"