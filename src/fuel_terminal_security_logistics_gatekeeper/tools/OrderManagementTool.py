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
            return "ERROR_CONEXIÓN: No se pudo acceder a Microsoft Graph."

        try:
            # CONFIGURACIÓN APPLICATION: El recurso es el correo de soporte
            # Esto permite que la App acceda al Drive de este usuario específico
            target_user = "soportesap@frontera-virtual.com"
            drive = account.storage().get_drive_by_endpoint(target_user)
            root = drive.get_root()
            
            # Localizar carpeta y archivo
            try:
                folder = root.get_item('Fuel_Terminal_System')
                file_item = folder.get_item('Master_Control_Orders.xlsx')
            except Exception:
                # Si no está en la carpeta, intentar en la raíz
                file_item = root.get_item('Master_Control_Orders.xlsx')

            # Descargar contenido actual
            content = file_item.download()
            try:
                df = pd.read_excel(io.BytesIO(content))
            except Exception:
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')

            # --- ACCIÓN: READ ---
            if action == "read":
                if not order_id: return "ERROR: Se requiere order_id para leer."
                result = df[df['OrderID'].astype(str) == str(order_id)]
                return result.to_string() if not result.empty else "ORDEN_NO_ENCONTRADA"

            # --- ACCIÓN: DELETE ---
            if action == "delete":
                if not order_id: return "ERROR: Se requiere order_id para borrar."
                df = df[df['OrderID'].astype(str) != str(order_id)]
                self._save_to_excel(file_item, df)
                return f"ORDEN_{order_id}_ELIMINADA"

            # --- ACCIÓN: CREATE ---
            if action == "create":
                # Lógica multi-unidad: permite procesar placas/conductores separados por coma
                plates = [p.strip() for p in str(plate_id).split(',')]
                drivers = [d.strip() for d in str(driver_name).split(',')]
                volumes = [v.strip() for v in str(fuel_volume).split(',')]
                
                num_units = len(plates)
                # Sincronizar longitudes de listas
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
                
                # Concatenar y guardar cambios
                df_final = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
                self._save_to_excel(file_item, df_final)
                
                return f"REGISTRO_EXITOSO: {num_units} unidades registradas bajo la orden {order_id}."

        except Exception as e:
            return f"ERROR_OPERATIVO_EXCEL: {str(e)}"

    def _save_to_excel(self, file_item, df):
        """Sube el archivo actualizado a Microsoft Graph (Modo Application)"""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        file_item.upload(output)