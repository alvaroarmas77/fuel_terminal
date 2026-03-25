import pandas as pd
import io
import os
import requests
import urllib.parse
import unicodedata
import time
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
        for _ in range(2):
            try:
                res = requests.post(url, data=data, timeout=25)
                return res.json().get('access_token')
            except: 
                time.sleep(2)
                continue
        return None

    def _normalize_text(self, text: str) -> str:
        if not text: return ""
        text = str(text).strip().lower()
        return "".join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )

    def _run(self, truck_plate: str, driver_name: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_AUTH"
        
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        
        try:
            path_file = "Fuel_Terminal_System/Master_Control.xlsx"
            encoded_path = urllib.parse.quote(path_file)
            url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/drive/root:/{encoded_path}:/content"
            
            res = None
            for _ in range(2):
                try:
                    res = requests.get(url, headers=headers, timeout=35)
                    if res.status_code == 200: break
                except: time.sleep(2)

            if not res or res.status_code != 200: return f"ERROR_ARCHIVO: {res.status_code if res else 'TIMEOUT'}"

            df = pd.read_excel(io.BytesIO(res.content), sheet_name="Vehicle_Registry", engine='openpyxl')
            df.columns = [str(c).strip() for c in df.columns]
            
            tp_search = str(truck_plate).strip().upper()
            dn_search_norm = self._normalize_text(driver_name)
            
            df_placa = df[df['Truck_Plate'].astype(str).str.strip().str.upper() == tp_search]

            if df_placa.empty:
                return f"RECHAZO_FASE_2: La placa {truck_plate} no se encuentra registrada."

            authorized_driver = None
            for _, row in df_placa.iterrows():
                current_excel_driver_norm = self._normalize_text(row.get('Driver_Name', ''))
                if current_excel_driver_norm == dn_search_norm:
                    authorized_driver = row
                    break
            
            if authorized_driver is not None:
                email = str(authorized_driver.get('Driver_Email', 'Sin Email'))
                id_interno = str(authorized_driver.get('ID_Interno', 'Sin ID'))
                return f"PHASE_2_SUCCESS|Email:{email}|ID:{id_interno}"
            else:
                conductores_validos = ", ".join(df_placa['Driver_Name'].astype(str).unique())
                return f"RECHAZO_FASE_2: El conductor {driver_name} no está autorizado para la placa {truck_plate}. Registrados: [{conductores_validos}]"

        except Exception as e:
            return f"ERROR_SISTEMA_REGISTRO: {str(e)}"