import pandas as pd
import io
from crewai_tools import BaseTool
from datetime import datetime

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = "Registra la orden final en Master_Control_Orders.xlsx en la nube."

    def _run(self, dispatcher_email: str, truck_plate: str, driver_name: str, fuel_volume: str, assigned_island: str, start_time: str, end_time: str) -> str:
        try:
            account = get_ms_account()
            drive = account.storage().get_default_drive()
            items = drive.get_root().get_items()
            
            target_folder = next((i for i in items if i.name == 'Fuel_Terminal_System' and i.is_folder), None)
            folder_items = target_folder.get_items()
            file_item = next((f for f in folder_items if f.name == 'Master_Control_Orders.xlsx'), None)

            # Leer, actualizar y subir
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            
            order_id = f"FL-{datetime.now().strftime('%y%m%d-%H%M%S')}"
            new_row = {
                'Order_ID': order_id, 'Date': datetime.now().strftime('%Y-%m-%d'),
                'Truck_Plate': truck_plate.upper(), 'Driver_Name': driver_name,
                'Volume': fuel_volume, 'Island': assigned_island,
                'Start_Time': start_time, 'End_Time': end_time, 'Dispatcher': dispatcher_email
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            output.seek(0)
            file_item.update_contents(output.read())
            
            return f"ÉXITO: Orden {order_id} registrada para placa {truck_plate}."
        except Exception as e:
            return f"ERROR_LOGGING: {str(e)}"