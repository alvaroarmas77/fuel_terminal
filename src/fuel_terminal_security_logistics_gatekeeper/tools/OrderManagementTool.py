import os
import pandas as pd
import io
import requests
import urllib.parse
from datetime import datetime
from crewai.tools import BaseTool
from pydantic import Field
from typing import Optional, Any

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
             driver_email: str = None, truck_plate: str = None, driver_name: str = None, 
             fuel_volume: str = None, assigned_island: str = None, appointment_date: str = None, 
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

        # Definición estricta de encabezados según tu requerimiento
        expected_columns = [
            'OrderID', 'Date_of_Request', 'dispatcher_email', 'Driver_Email', 
            'truck_plate', 'Driver_Name', 'Fuel Volume (Gallons)', 
            'Assigned Island', 'Appointment Date', 'Start Time', 'End Time'
        ]

        try:
            # 1. DESCARGA DEL ARCHIVO
            res_download = requests.get(content_url, headers=headers_base, timeout=30)
            
            if res_download.status_code == 200:
                df = pd.read_excel(io.BytesIO(res_download.content), engine='openpyxl')
                df.columns = [str(c).strip() for c in df.columns]
                # Asegurar que todas las columnas existan
                for col in expected_columns:
                    if col not in df.columns:
                        df[col] = None
            else:
                df = pd.DataFrame(columns=expected_columns)

            # --- ACCIÓN: CREATE ---
            if action == "create":
                # Limpieza de datos recibidos
                plates = [p.strip() for p in str(truck_plate).split(',')] if truck_plate else []
                
                if not plates:
                    return "ERROR_DATOS: No se proporcionó truck_plate."

                new_entries = []
                for plate in plates:
                    new_entries.append({
                        'OrderID': str(order_id),
                        'Date_of_Request': datetime.now().strftime('%Y-%m-%d'),
                        'dispatcher_email': str(dispatcher_email),
                        'Driver_Email': str(driver_email) if driver_email else "soporte@frontera-virtual.com",
                        'truck_plate': plate.upper(),
                        'Driver_Name': str(driver_name),
                        'Fuel Volume (Gallons)': str(fuel_volume),
                        'Assigned Island': str(assigned_island),
                        'Appointment Date': str(appointment_date),
                        'Start Time': str(start_time),
                        'End Time': str(end_time)
                    })
                
                df_new = pd.DataFrame(new_entries)
                df_final = pd.concat([df, df_new], ignore_index=True)
                
                # Reordenar columnas para mantener consistencia
                df_final = df_final[expected_columns]

                # GUARDADO EN MEMORIA
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                
                # SUBIDA A ONEDRIVE
                headers_upload = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/octet-stream'
                }
                
                res_upload = requests.put(content_url, headers=headers_upload, data=output.getvalue(), timeout=30)
                
                if res_upload.status_code in [200, 201]:
                    return f"PHASE_4_SUCCESS|ORDEN:{order_id}|UNIDADES:{len(plates)}"
                else:
                    return f"ERROR_AL_GUARDAR: Status {res_upload.status_code}"

            # --- ACCIÓN: READ ---
            elif action == "read":
                if not order_id: return "ERROR: OrderID requerido."
                search_id = str(order_id).strip().lower()
                matches = df[df['OrderID'].astype(str).str.lower() == search_id]
                
                if matches.empty: return "ORDEN_NO_ENCONTRADA"
                return f"RESULTADOS_ORDEN|{matches.to_dict(orient='records')}"

            return f"ERROR: Acción '{action}' no válida."

        except Exception as e:
            return f"ERROR_OPERATIVO_EXCEL: {str(e)}"