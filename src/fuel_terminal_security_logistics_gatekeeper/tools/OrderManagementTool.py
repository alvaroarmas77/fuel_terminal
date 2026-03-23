import os
import pandas as pd
import io
import requests
import urllib.parse
from datetime import datetime
from crewai.tools import BaseTool
from pydantic import Field

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = (
        "Gestiona órdenes en Master_Control_Orders.xlsx. "
        "Permite 'create' (registrar nuevas filas), 'read' (consultar) y actualizar datos "
        "de asignación de islas y horarios para cada camión."
    )
    
    # Campo definido para evitar errores de validación en CrewAI
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

    def _run(self, action: str = "create", order_id: str = None, dispatcher_email: str = None, 
             truck_plate: str = None, driver_name: str = None, fuel_volume: str = None, 
             assigned_island: str = None, appointment_date: str = None, 
             start_time: str = None, end_time: str = None) -> str:
        
        token = self._get_token()
        if not token: 
            return "ERROR_CONEXIÓN_AZURE"

        # --- CORRECCIÓN DE RUTA (Sincronizada con las otras herramientas) ---
        file_name = "Fuel_Terminal_System/Master_Control_Orders.xlsx"
        encoded_path = urllib.parse.quote(file_name)
        content_url = f"https://graph.microsoft.com/v1.0/users/{self.target_user}/drive/root:/{encoded_path}:/content"

        headers_upload = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/octet-stream'
        }
        
        headers_download = {
            'Authorization': f'Bearer {token}'
        }

        try:
            # 1. Intentar descargar el archivo actual
            res_download = requests.get(content_url, headers=headers_download, timeout=30)
            
            if res_download.status_code == 200:
                # Se especifica openpyxl para compatibilidad en runners de GitHub
                df = pd.read_excel(io.BytesIO(res_download.content), engine='openpyxl')
            else:
                # Si el archivo no existe (404) o hay error, crear estructura base
                df = pd.DataFrame(columns=[
                    'OrderID', 'Date_of_Request', 'dispatcher_email', 'Driver_Email', 
                    'truck_plate', 'Driver_Name', 'Fuel Volume (Gallons)', 
                    'Assigned Island', 'Appointment Date', 'Start Time', 'End Time'
                ])

            if action == "create":
                # Procesamiento multi-unidad (separa por comas si vienen varios)
                # Normalización preventiva con .strip()
                plates = [p.strip() for p in str(truck_plate).split(',')]
                drivers = [d.strip() for d in str(driver_name).split(',')]
                volumes = [v.strip() for v in str(fuel_volume).split(',')]
                
                new_entries = []
                num_units = len(plates)

                for i in range(num_units):
                    # Lógica de asignación: usa el índice o el primer elemento si no hay suficientes
                    d_name = drivers[i] if i < len(drivers) else (drivers[0] if drivers else "")
                    f_vol = volumes[i] if i < len(volumes) else (volumes[0] if volumes else "")
                    
                    new_entries.append({
                        'OrderID': str(order_id),
                        'Date_of_Request': datetime.now().strftime('%Y-%m-%d'),
                        'dispatcher_email': dispatcher_email,
                        'Driver_Email': "pendiente@correo.com",
                        'truck_plate': plates[i].upper(),
                        'Driver_Name': d_name,
                        'Fuel Volume (Gallons)': f_vol,
                        'Assigned Island': assigned_island,
                        'Appointment Date': appointment_date,
                        'Start Time': start_time,
                        'End Time': end_time
                    })
                
                # Crear DataFrame de nuevas entradas y concatenar
                df_new = pd.DataFrame(new_entries)
                df_final = pd.concat([df, df_new], ignore_index=True)
                
                # 2. Guardar en memoria y subir a OneDrive
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                
                # Subida de contenido binario (PUT reemplaza el archivo con la nueva versión)
                res_upload = requests.put(content_url, headers=headers_upload, data=output.getvalue(), timeout=30)
                
                if res_upload.status_code in [200, 201]:
                    return f"ORDEN REGISTRADA: {num_units} unidades bajo ID {order_id}."
                else:
                    return f"ERROR_AL_GUARDAR: {res_upload.status_code} - {res_upload.text}"

            elif action == "read":
                # Normalización para búsqueda robusta
                df['OrderID'] = df['OrderID'].astype(str).str.strip()
                result = df[df['OrderID'] == str(order_id).strip()]
                return result.to_string() if not result.empty else "ORDEN_NO_ENCONTRADA"

            return "ACCION_SOLICITADA_NO_VALIDA"

        except Exception as e:
            return f"ERROR_OPERATIVO_EXCEL: {str(e)}"