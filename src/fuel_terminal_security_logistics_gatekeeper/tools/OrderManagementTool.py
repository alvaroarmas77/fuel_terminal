import os
import pandas as pd
import io
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account

try:
    from crewai_tools import BaseTool
except ImportError:
    from crewai.tools import BaseTool

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = (
        "Gestiona órdenes en Master_Control_Orders.xlsx. "
        "Acciones: 'create' (registrar), 'read' (buscar detalles de una orden) "
        "o 'delete' (eliminar filas de una orden)."
    )

    def _run(self, action: str = "create", order_id: str = None, dispatcher_email: str = None, 
             plate_id: str = None, driver_name: str = None, fuel_volume: str = None, 
             assigned_island: str = None, appointment_date: str = None, 
             start_time: str = None, end_time: str = None) -> str:
        
        account = get_ms_account()
        if not account:
            return "ERROR_CONEXIÓN: No se pudo acceder a Excel."

        try:
            drive = account.storage().get_default_drive()
            root = drive.get_root()
            folder = root.get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control_Orders.xlsx')
            
            content = file_item.download()
            try:
                df = pd.read_excel(io.BytesIO(content))
            except Exception:
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')

            # --- LÓGICA DE LECTURA (Para Agente 3) ---
            if action == "read":
                result = df[df['OrderID'] == order_id]
                if result.empty:
                    return f"ERROR: No se encontró la orden {order_id}."
                
                # Retornamos los detalles para que el Agente 3 sepa qué borrar en Outlook
                detalles = result[['Assigned Island', 'Appointment Date', 'Start Time']].to_dict('records')
                return f"DATOS_ORDEN: {str(detalles)}"

            # --- LÓGICA DE ELIMINACIÓN (Para Agente 4) ---
            elif action == "delete":
                if order_id not in df['OrderID'].values:
                    return f"ERROR: La orden {order_id} no existe en el registro."
                
                new_df = df[df['OrderID'] != order_id]
                self._save_to_excel(file_item, new_df)
                return f"CANCELACIÓN_EXITOSA: La orden {order_id} ha sido borrada del registro maestro."

            # --- LÓGICA DE REGISTRO (Original) ---
            else:
                plates = [p.strip() for p in str(plate_id).split(',')]
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
                self._save_to_excel(file_item, new_df)
                return f"REGISTRO_EXITOSO: Se han registrado {num_units} unidades bajo la orden {order_id}."
            
        except Exception as e:
            return f"ERROR_OPERATIVO: Detalle: {str(e)}"

    def _save_to_excel(self, file_item, df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        file_item.update_contents(output.read())