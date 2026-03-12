import os
import pandas as pd
import io
import sys
from crewai_tools import BaseTool
from datetime import datetime

# --- BLINDAJE DE IMPORTACIÓN ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = "Registra físicamente una o múltiples unidades bajo el mismo OrderID en Master_Control_Orders.xlsx."

    def _run(self, order_id: str, dispatcher_email: str, plate_id: str, driver_name: str, fuel_volume: str, assigned_island: str, appointment_date: str, start_time: str, end_time: str) -> str:
        from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
        
        account = get_ms_account()
        if not account:
            return "ERROR_CONEXIÓN: No se puede registrar la orden sin acceso a OneDrive."

        try:
            drive = account.storage().get_default_drive()
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control_Orders.xlsx')
            
            content = file_item.download()
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            
            # --- LÓGICA MULTI-UNIDAD ---
            # Convertimos los strings (que pueden venir como "ABC, DEF") en listas limpias
            plates = [p.strip().upper() for p in str(plate_id).split(',')]
            drivers = [d.strip() for d in str(driver_name).split(',')]
            volumes = [v.strip() for v in str(fuel_volume).split(',')]
            
            # Validamos que las listas tengan la misma longitud para evitar desalineación
            # Si solo viene un conductor para varios camiones, lo repetimos
            max_len = len(plates)
            if len(drivers) < max_len: drivers = drivers * max_len
            if len(volumes) < max_len: volumes = volumes * max_len

            rows_to_add = []
            
            # Creamos una fila por cada unidad compartiendo el mismo OrderID
            for i in range(max_len):
                new_row = {
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
                rows_to_add.append(new_row)
            
            # Concatenamos todas las nuevas filas al DataFrame original
            df = pd.concat([df, pd.DataFrame(rows_to_add)], ignore_index=True)
            
            # Escritura en Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            output.seek(0)
            file_item.update_contents(output.read())
            
            return f"REGISTRO_EXITOSO: Se han registrado {max_len} filas bajo la Orden {order_id}."
            
        except Exception as e:
            return f"ERROR_ESCRITURA: {str(e)}"