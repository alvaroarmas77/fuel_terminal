import os
import pandas as pd
import io
import requests
from datetime import datetime
from crewai.tools import BaseTool

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = (
        "Gestiona órdenes en Master_Control_Orders.xlsx. "
        "Permite 'create' (registrar nuevas filas), 'read' (consultar) y actualizar datos "
        "de asignación de islas y horarios para cada camión."
    )

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

    def _run(self, action: str = "create", order_id: str = None, dispatcher_email: str = None, 
             truck_plate: str = None, driver_name: str = None, fuel_volume: str = None, 
             assigned_island: str = None, appointment_date: str = None, 
             start_time: str = None, end_time: str = None) -> str:
        
        token = self._get_token()
        if not token: return "ERROR_CONEXIÓN_AZURE"

        headers = {'Authorization': f'Bearer {token}'}
        target_user = "soportesap@frontera-virtual.com"
        # Ruta al archivo en OneDrive
        content_url = f"https://graph.microsoft.com/v1.0/users/{target_user}/drive/root:/Fuel_Terminal_System/Master_Control_Orders.xlsx:/content"

        try:
            # 1. Descargar el archivo actual
            res_download = requests.get(content_url, headers=headers)
            if res_download.status_code == 200:
                df = pd.read_excel(io.BytesIO(res_download.content))
            else:
                # Si el archivo no existe, crear estructura base
                df = pd.DataFrame(columns=[
                    'OrderID', 'Date_of_Request', 'dispatcher_email', 'Driver_Email', 
                    'truck_plate', 'Driver_Name', 'Fuel Volume (Gallons)', 
                    'Assigned Island', 'Appointment Date', 'Start Time', 'End Time'
                ])

            if action == "create":
                # Procesamiento multi-unidad (separa por comas si vienen varios)
                plates = [p.strip() for p in str(truck_plate).split(',')]
                drivers = [d.strip() for d in str(driver_name).split(',')]
                volumes = [v.strip() for v in str(fuel_volume).split(',')]
                
                new_entries = []
                num_units = len(plates)

                for i in range(num_units):
                    new_entries.append({
                        'OrderID': order_id,
                        'Date_of_Request': datetime.now().strftime('%Y-%m-%d'),
                        'dispatcher_email': dispatcher_email,
                        'Driver_Email': "pendiente@correo.com", # Se actualiza en flujo
                        'truck_plate': plates[i],
                        'Driver_Name': drivers[i] if i < len(drivers) else drivers[0],
                        'Fuel Volume (Gallons)': volumes[i] if i < len(volumes) else volumes[0],
                        'Assigned Island': assigned_island,
                        'Appointment Date': appointment_date,
                        'Start Time': start_time,
                        'End Time': end_time
                    })
                
                df_final = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
                
                # 2. Guardar en memoria y subir a OneDrive
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                output.seek(0)
                
                res_upload = requests.put(content_url, headers=headers, data=output.read())
                
                if res_upload.status_code in [200, 201]:
                    return f"ORDEN REGISTRADA: {num_units} unidades bajo ID {order_id}."
                else:
                    return f"ERROR_AL_GUARDAR: {res_upload.status_code}"

            elif action == "read":
                result = df[df['OrderID'] == order_id]
                return result.to_string() if not result.empty else "ORDEN_NO_ENCONTRADA"

            return "ACCION_SOLICITADA_NO_VALIDA"

        except Exception as e:
            return f"ERROR_OPERATIVO_EXCEL: {str(e)}"