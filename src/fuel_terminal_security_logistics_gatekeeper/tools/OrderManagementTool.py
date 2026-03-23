import os
import pandas as pd
import io
import requests
import urllib.parse
from datetime import datetime
from crewai.tools import BaseTool
from pydantic import Field
from typing import Optional, Type, Any

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = (
        "Gestiona órdenes en Master_Control_Orders.xlsx. "
        "Permite 'create' (registrar nuevas filas), 'read' (consultar) y actualizar datos "
        "de asignación de islas y horarios para cada camión."
    )
    
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
            res = requests.post(token_url, data=data, timeout=20)
            return res.json().get('access_token')
        except Exception:
            return None

    def _run(self, action: str = "create", order_id: str = None, dispatcher_email: str = None, 
             truck_plate: str = None, driver_name: str = None, fuel_volume: str = None, 
             assigned_island: str = None, appointment_date: str = None, 
             start_time: str = None, end_time: str = None) -> str:
        
        token = self._get_token()
        if not token: 
            return "ERROR_CONEXIÓN_AZURE"

        file_name = "Fuel_Terminal_System/Master_Control_Orders.xlsx"
        encoded_path = urllib.parse.quote(file_name)
        content_url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/drive/root:/{encoded_path}:/content"

        headers_base = {
            'Authorization': f'Bearer {token}'
        }

        try:
            # 1. INTENTAR DESCARGAR EL ARCHIVO ACTUAL
            res_download = requests.get(content_url, headers=headers_base, timeout=30)
            
            if res_download.status_code == 200:
                df = pd.read_excel(io.BytesIO(res_download.content), engine='openpyxl')
                # Limpieza preventiva de nombres de columnas
                df.columns = [str(c).strip() for c in df.columns]
            else:
                # Si el archivo no existe, creamos la estructura maestra
                df = pd.DataFrame(columns=[
                    'OrderID', 'Date_of_Request', 'dispatcher_email', 'Driver_Email', 
                    'truck_plate', 'Driver_Name', 'Fuel Volume', 
                    'Assigned Island', 'Appointment Date', 'Start Time', 'End Time'
                ])

            # --- ACCIÓN: CREATE (REGISTRO DE NUEVA ORDEN) ---
            if action == "create":
                # Manejo de entradas múltiples (separadas por coma)
                plates = [p.strip() for p in str(truck_plate).split(',')] if truck_plate else []
                drivers = [d.strip() for d in str(driver_name).split(',')] if driver_name else []
                volumes = [v.strip() for v in str(fuel_volume).split(',')] if fuel_volume else []
                
                new_entries = []
                num_units = len(plates)

                if num_units == 0:
                    return "ERROR_DATOS: No se proporcionaron placas de camión."

                for i in range(num_units):
                    # Lógica de emparejamiento para conductores y volúmenes
                    d_name = drivers[i] if i < len(drivers) else (drivers[0] if drivers else "N/A")
                    f_vol = volumes[i] if i < len(volumes) else (volumes[0] if volumes else "0")
                    
                    new_entries.append({
                        'OrderID': str(order_id),
                        'Date_of_Request': datetime.now().strftime('%Y-%m-%d'),
                        'dispatcher_email': str(dispatcher_email),
                        'Driver_Email': "pendiente@correo.com", # Se llena en fase posterior
                        'truck_plate': str(plates[i]).upper(),
                        'Driver_Name': d_name,
                        'Fuel Volume': f_vol,
                        'Assigned Island': str(assigned_island) if assigned_island else "TBD",
                        'Appointment Date': str(appointment_date) if appointment_date else "TBD",
                        'Start Time': str(start_time) if start_time else "--:--",
                        'End Time': str(end_time) if end_time else "--:--"
                    })
                
                df_new = pd.DataFrame(new_entries)
                df_final = pd.concat([df, df_new], ignore_index=True)
                
                # Guardar y Subir
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                
                headers_upload = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/octet-stream'
                }
                
                res_upload = requests.put(content_url, headers=headers_upload, data=output.getvalue(), timeout=30)
                
                if res_upload.status_code in [200, 201]:
                    return f"PHASE_4_SUCCESS|ORDEN REGISTRADA: {num_units} unidades bajo ID {order_id}."
                else:
                    return f"ERROR_AL_GUARDAR: {res_upload.status_code} - {res_upload.text}"

            # --- ACCIÓN: READ (CONSULTA DE ÓRDENES) ---
            elif action == "read":
                if not order_id:
                    return "ERROR: Se requiere OrderID para la lectura."
                
                search_id = str(order_id).strip().lower()
                matches = []

                # BÚSQUEDA MANUAL BLINDADA (Igual que AccessControlTool)
                for _, row in df.iterrows():
                    current_id = str(row.get('OrderID', '')).strip().lower()
                    if current_id == search_id:
                        matches.append(row.to_dict())
                
                if not matches:
                    return "ORDEN_NO_ENCONTRADA"
                
                return f"RESULTADOS_ORDEN|{str(matches)}"

            return "ERROR: Acción solicitada ('{}') no es válida.".format(action)

        except Exception as e:
            return f"ERROR_OPERATIVO_EXCEL: {str(e)}"