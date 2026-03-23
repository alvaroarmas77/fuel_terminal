import os
import pandas as pd
import io
import requests
from datetime import datetime

# Sistema de importación compatible con CrewAI v0.100.1+
try:
    from crewai_tools import BaseTool
except ImportError:
    try:
        from crewai.tools import BaseTool
    except ImportError:
        class BaseTool: pass

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = (
        "Gestiona órdenes en Master_Control_Orders.xlsx. "
        "Acciones: 'create' (registrar), 'read' (buscar) o 'delete' (eliminar)."
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
             plate_id: str = None, driver_name: str = None, fuel_volume: str = None, 
             assigned_island: str = None, appointment_date: str = None, 
             start_time: str = None, end_time: str = None) -> str:
        
        token = self._get_token()
        if not token:
            return "ERROR_CONEXIÓN: Fallo de autenticación en Microsoft Graph."

        headers = {'Authorization': f'Bearer {token}'}
        target_user = "soportesap@frontera-virtual.com"
        file_url = f"https://graph.microsoft.com/v1.0/users/{target_user}/drive/root:/Fuel_Terminal_System/Master_Control_Orders.xlsx"
        content_url = f"{file_url}:/content"

        try:
            # 1. Leer el archivo actual
            res_download = requests.get(content_url, headers=headers)
            if res_download.status_code == 200:
                df = pd.read_excel(io.BytesIO(res_download.content))
            else:
                # Si el archivo no existe, creamos un DataFrame nuevo con las columnas necesarias
                df = pd.DataFrame(columns=[
                    'OrderID', 'Date of Request', 'Dispatcher Email', 'Truck Plate', 
                    'Driver Name', 'Fuel Volume (Gallons)', 'Assigned Island', 
                    'Appointment Date', 'Start Time', 'End Time'
                ])

            if action == "create":
                # Lógica para manejar múltiples unidades si vienen separadas por comas
                plates = [p.strip() for p in str(plate_id).split(',')]
                drivers = [d.strip() for d in str(driver_name).split(',')]
                volumes = [v.strip() for v in str(fuel_volume).split(',')]
                num_units = len(plates)

                new_entries = []
                for i in range(num_units):
                    new_entries.append({
                        'OrderID': order_id,
                        'Date of Request': datetime.now().strftime('%Y-%m-%d'),
                        'Dispatcher Email': dispatcher_email,
                        'Truck Plate': plates[i],
                        'Driver Name': drivers[i] if i < len(drivers) else drivers[0],
                        'Fuel Volume (Gallons)': volumes[i] if i < len(volumes) else volumes[0],
                        'Assigned Island': assigned_island,
                        'Appointment Date': appointment_date,
                        'Start Time': start_time,
                        'End Time': end_time
                    })
                
                df_final = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
                
                # 2. Guardar y subir (PUT)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                output.seek(0)
                
                res_upload = requests.put(content_url, headers=headers, data=output.read())
                
                if res_upload.status_code in [200, 201]:
                    return f"REGISTRO_EXITOSO: {num_units} unidades en la orden {order_id}."
                else:
                    return f"ERROR_UPLOAD: {res_upload.status_code}"

            return "ACCION_NO_IMPLEMENTADA"

        except Exception as e:
            return f"ERROR_OPERATIVO_EXCEL: {str(e)}"