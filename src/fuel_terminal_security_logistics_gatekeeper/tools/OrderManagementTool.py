import pandas as pd
import io
from crewai_tools import BaseTool
from datetime import datetime

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = "Registra la orden en Master_Control_Orders.xlsx con encabezados oficiales."

    def _run(self, order_id: str, dispatcher_email: str, plate_id: str, driver_name: str, fuel_volume: str, assigned_island: str, appointment_date: str, start_time: str, end_time: str) -> str:
        try:
            account = get_ms_account()
            drive = account.storage().get_default_drive()
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control_Orders.xlsx')

            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            
            # Encabezados EXACTOS según tu requerimiento
            new_row = {
                'OrderID': order_id,
                'Date of Request': datetime.now().strftime('%Y-%m-%d'),
                'Dispatcher Email': dispatcher_email,
                'Truck Plate': plate_id.upper(),
                'Driver Name': driver_name,
                'Fuel Volume (Gallons)': fuel_volume,
                'Assigned Island': assigned_island,
                'Appointment Date': appointment_date,
                'Start Time': start_time,
                'End_Time': end_time
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            output.seek(0)
            file_item.update_contents(output.read())
            
            return f"ÉXITO: Orden {order_id} registrada con todos los campos técnicos."
        except Exception as e:
            return f"ERROR_SISTEMA: Fallo al registrar orden. Detalle: {str(e)}"