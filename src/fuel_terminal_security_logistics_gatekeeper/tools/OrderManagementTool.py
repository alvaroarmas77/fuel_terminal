import pandas as pd
import io
from crewai_tools import BaseTool
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = "Registra físicamente la orden en Master_Control_Orders.xlsx en OneDrive."

    def _run(self, dispatcher_email: str, truck_plate: str, driver_name: str, fuel_volume: str, assigned_island: str, start_time: str, end_time: str) -> str:
        try:
            account = get_ms_account()
            if not account: return "ERROR: Autenticación MS Graph fallida."
            
            drive = account.storage().get_default_drive()
            # RUTA ABSOLUTA CORREGIDA
            file_path = '/Fuel_Terminal_System/Master_Control_Orders.xlsx'
            
            # 1. Descargar el log de órdenes existente
            file_item = drive.get_item_by_path(file_path)
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            
            # 2. Preparar nueva fila
            order_id = f"FL-{datetime.now().strftime('%y%m%d-%H%M%S')}"
            new_row = {
                'Order_ID': order_id,
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Truck_Plate': truck_plate.upper(),
                'Driver_Name': driver_name,
                'Volume': fuel_volume,
                'Island': assigned_island,
                'Start_Time': start_time,
                'End_Time': end_time,
                'Dispatcher': dispatcher_email
            }
            
            # 3. Añadir fila y guardar en buffer
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            # 4. Subir el archivo actualizado (Sobrescribir)
            output.seek(0)
            file_item.update_contents(output.read())
            
            return f"ÉXITO: Orden {order_id} registrada físicamente en OneDrive para la placa {truck_plate}."

        except Exception as e:
            return f"ERROR_LOGGING: {str(e)}"