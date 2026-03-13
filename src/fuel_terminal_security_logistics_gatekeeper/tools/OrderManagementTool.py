import os
import pandas as pd
import io
import sys
from datetime import datetime
try:
    from crewai_tools import BaseTool
except ImportError:
    try:
        from crewai.tools import BaseTool
    except ImportError:
        from crewai.tools.base_tool import BaseTool

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = (
        "Registra una o múltiples unidades en Master_Control_Orders.xlsx. "
        "Recibe datos separados por comas para procesar órdenes multi-unidad."
    )

    def _run(self, order_id: str, dispatcher_email: str, plate_id: str, driver_name: str, 
             fuel_volume: str, assigned_island: str, appointment_date: str, 
             start_time: str, end_time: str) -> str:
        
        # CAMBIO: Importación de la utilidad corregida
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        try:
            from utils.microsoft_graph import get_ms_account
        except ImportError:
            from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
        
        account = get_ms_account()
        if not account:
            return "ERROR_CONEXIÓN: No se pudo obtener acceso a la cuenta de Microsoft."

        try:
            # Lógica de procesamiento de listas intacta
            drive = account.storage().get_default_drive()
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control_Orders.xlsx')
            
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            
            plates = [p.strip().upper() for p in str(plate_id).split(',')]
            drivers = [d.strip() for d in str(driver_name).split(',')]
            volumes = [v.strip() for v in str(fuel_volume).split(',')]
            
            num_units = len(plates)
            if len(drivers) < num_units: drivers = drivers * num_units
            if len(volumes) < num_units: volumes = volumes * num_units

            new_entries = []
            for i in range(num_units):
                row = {
                    'OrderID': order_id,
                    'Date of Request': datetime.now().strftime('%Y-%m-%d'),
                    'Dispatcher Email': dispatcher_email,
                    'Truck Plate': plates[i],
                    'Driver Name': drivers[i],
                    'Fuel Volume (Gallons)': volumes[i],
                    'Assigned Island': assigned_island,
                    'Appointment Date': appointment_date,
                    'Start Time': start_time,
                    'End Time': end_time
                }
                new_entries.append(row)
            
            new_df = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                new_df.to_excel(writer, index=False)
            
            output.seek(0)
            file_item.update_contents(output.read())
            return f"REGISTRO_EXITOSO: Se han registrado {num_units} unidades bajo la orden maestra {order_id}."
            
        except Exception as e:
            return f"ERROR_OPERATIVO: Falló el registro en Master_Control_Orders. Detalle: {str(e)}"