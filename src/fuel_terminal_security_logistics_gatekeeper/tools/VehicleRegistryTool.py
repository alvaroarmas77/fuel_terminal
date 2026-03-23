import pandas as pd
import io
import os
import requests
import urllib.parse
import unicodedata
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

    def _normalize_text(self, text: str) -> str:
        """Elimina tildes, convierte a minúsculas y quita espacios en blanco extremos."""
        if not text:
            return ""
        # Convertir a string, quitar espacios y pasar a minúsculas
        text = str(text).strip().lower()
        # Eliminar acentos/tildes usando normalización Unicode
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
            
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code != 200: return f"ERROR_ARCHIVO: {res.status_code}"

            # Leer pestaña "Vehicle_Registry"
            df = pd.read_excel(io.BytesIO(res.content), sheet_name="Vehicle_Registry", engine='openpyxl')
            
            # Limpieza de nombres de columnas
            df.columns = [str(c).strip() for c in df.columns]
            
            # Normalización de los inputs de búsqueda
            tp_search = str(truck_plate).strip().upper()
            dn_search_norm = self._normalize_text(driver_name)
            
            # 1. Filtramos primero por Placa (Búsqueda exacta de placa)
            df_placa = df[df['Truck_Plate'].astype(str).str.strip().str.upper() == tp_search]

            if df_placa.empty:
                return f"RECHAZO_FASE_2: La placa {truck_plate} no se encuentra registrada en el sistema."

            # 2. Buscamos al conductor comparando versiones NORMALIZADAS
            authorized_driver = None
            for _, row in df_placa.iterrows():
                # Normalizamos el nombre que viene de la fila del Excel
                current_excel_driver_norm = self._normalize_text(row.get('Driver_Name', ''))
                
                if current_excel_driver_norm == dn_search_norm:
                    authorized_driver = row
                    break
            
            if authorized_driver is not None:
                # ÉXITO: Los nombres coinciden tras normalizar
                email = str(authorized_driver.get('Driver_Email', 'Sin Email'))
                id_interno = str(authorized_driver.get('ID_Interno', 'Sin ID'))
                return f"PHASE_2_SUCCESS|Email:{email}|ID:{id_interno}"
            else:
                # FALLO: La placa existe pero el conductor no coincide