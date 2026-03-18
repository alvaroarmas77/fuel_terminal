import os
import pandas as pd
import io
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
from crewai_tools import BaseTool

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = "Gestiona órdenes en Master_Control_Orders.xlsx."

    def _run(self, action: str = "create", order_id: str = None, dispatcher_email: str = None, 
             plate_id: str = None, driver_name: str = None, fuel_volume: str = None, 
             assigned_island: str = None, appointment_date: str = None, 
             start_time: str = None, end_time: str = None) -> str:
        
        account = get_ms_account()
        if not account: return "ERROR_CONEXIÓN"

        target_user = "soportesap@frontera-virtual.com"
        try:
            drive = account.storage().get_drive_by_endpoint(target_user)
            root = drive.get_root()
            
            try:
                folder = root.get_item('Fuel_Terminal_System')
                file_item = folder.get_item('Master_Control_Orders.xlsx')
            except:
                file_item = root.get_item('Master_Control_Orders.xlsx')

            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content))

            if action == "read":
                result = df[df['OrderID'].astype(str) == str(order_id)]
                return result.to_string() if not result.empty else "ORDEN_NO_ENCONTRADA"

            if action == "delete":
                df = df[df['OrderID'].astype(str) != str(order_id)]
                self._save_to_excel(file_item, df)
                return f"ORDEN_{order_id}_ELIMINADA"

            if action == "create":
                plates = [p.strip() for p in str(plate_id).split(',')]
                drivers = [d.strip() for d in str(driver_name).split(',')]
                volumes = [v.strip() for v in str(fuel_volume).split(',')]
                
                new_entries = []
                for i in range(len(plates)):
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
                self._save_to_excel(file_item, df_final)
                return f"REGISTRO_EXITOSO: {len(plates)} unidades registradas."

        except Exception as e:
            return f"ERROR_OPERATIVO: {str(e)}"

    def _save_to_excel(self, file_item, df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        file_item.upload(output)