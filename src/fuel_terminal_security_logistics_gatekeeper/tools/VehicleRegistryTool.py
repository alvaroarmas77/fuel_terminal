import pandas as pd
import io
import os
import requests
import urllib.parse
from crewai.tools import BaseTool
from pydantic import Field
from typing import Type

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Consulta la base de datos de vehículos autorizados usando la placa (truck_plate) y nombre del conductor."
    
    target_user: str = Field(default="soportesap@frontera-virtual.com")

    def _get_token(self):
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        if not all([client_id, client_secret, tenant_id]): return None
        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret, 'scope': 'https://graph.microsoft.com/.default'}
        try:
            res = requests.post(url, data=data, timeout=20)
            return res.json().get('access_token')
        except: return None

    def _run(self, truck_plate: str, driver_name: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_AUTH"
        
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        
        try:
            path_file = "Fuel_Terminal_System/Master_Control.xlsx"
            encoded_path = urllib.parse.quote(path_file)
            url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/drive/root:/{encoded_path}:/content"
            
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code != 200: return f"ERROR_ARCHIVO: {res.status_code}"

            # Leer pestaña "Vehicle_Registry"
            df = pd.read_excel(io.BytesIO(res.content), sheet_name="Vehicle_Registry", engine='openpyxl')
            
            # Limpieza de nombres de columnas (quitar espacios invisibles)
            df.columns = [str(c).strip() for c in df.columns]
            
            # --- LÓGICA DE BÚSQUEDA BLINDADA ---
            tp_search = str(truck_plate).strip().upper()
            dn_search = str(driver_name).strip().lower()
            
            found = False
            result_data = {}

            # Iteración manual para evitar errores de tipos de datos en Pandas
            for _, row in df.iterrows():
                # Buscamos las columnas de forma flexible (con o sin espacio)
                current_plate = str(row.get('Truck Plate', row.get('truck_plate', ''))).strip().upper()
                current_driver = str(row.get('Driver Name', row.get('driver_name', ''))).strip().lower()

                if current_plate == tp_search and current_driver == dn_search:
                    found = True
                    result_data = {
                        'Email': row.get('Driver_Email', row.get('driver_email', 'Sin Email')),
                        'ID': row.get('ID_Interno', row.get('id_interno', 'Sin ID'))
                    }
                    break
            
            if found:
                return f"PHASE_2_SUCCESS|Email:{result_data['Email']}|ID:{result_data['ID']}"
            
            return "RECHAZO_FASE_2: El vehículo o conductor no están autorizados o datos no coinciden."

        except Exception as e:
            return f"ERROR_SISTEMA_REGISTRO: {str(e)}"