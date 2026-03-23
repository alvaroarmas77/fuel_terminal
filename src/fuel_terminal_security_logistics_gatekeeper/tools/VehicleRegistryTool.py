import pandas as pd
import io
import os
import requests
from crewai.tools import BaseTool
from pydantic import Field # Añadido para compatibilidad con CrewAI/Pydantic

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = "Consulta la base de datos de vehículos autorizados usando la placa (truck_plate)."
    
    # Campo definido para evitar errores de validación en la instancia de CrewAI
    target_user: str = Field(default="soportesap@frontera-virtual.com")

    def _get_token(self):
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        
        if not all([client_id, client_secret, tenant_id]):
            return None

        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        try:
            # Timeout añadido para estabilidad en la nube
            res = requests.post(token_url, data=data, timeout=20)
            return res.json().get('access_token')
        except:
            return None

    def _run(self, truck_plate: str, driver_name: str) -> str:
        token = self._get_token()
        if not token: return "ERROR_AUTH"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        try:
            url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/drive/root:/Fuel_Terminal_System/Master_Control.xlsx:/content"
            # Se añade timeout para evitar "Server disconnected"
            res = requests.get(url, headers=headers, timeout=30)
            
            if res.status_code != 200:
                return f"ERROR_ARCHIVO: {res.status_code}"

            # Leer pestaña específica usando openpyxl para entorno Linux
            df = pd.read_excel(io.BytesIO(res.content), sheet_name="Vehicle_Registry", engine='openpyxl')
            
            # Limpieza de nombres de columnas
            df.columns = [str(c).strip() for c in df.columns]
            
            # Limpieza de datos para búsqueda robusta
            tp_search = str(truck_plate).strip().upper()
            dn_search = str(driver_name).strip().lower()
            
            # Normalización de columnas en el DataFrame
            df['Truck Plate'] = df['Truck Plate'].astype(str).str.strip().upper()
            df['Driver Name'] = df['Driver Name'].astype(str).str.strip().lower()
            
            # Buscamos coincidencias
            match = df[(df['Truck Plate'] == tp_search) & (df['Driver Name'] == dn_search)]
            
            if not match.empty:
                # Extraemos datos adicionales usando .get() para seguridad
                email_conductor = match.iloc[0].get('Driver_Email', 'Sin Email')
                id_interno = match.iloc[0].get('ID_Interno', 'Sin ID')
                return f"PHASE_2_SUCCESS|Email:{email_conductor}|ID:{id_interno}"
            
            return "RECHAZO_FASE_2: El vehículo o conductor no están autorizados o los documentos han expirado."

        except Exception as e:
            return f"ERROR_SISTEMA_REGISTRO: {str(e)}"