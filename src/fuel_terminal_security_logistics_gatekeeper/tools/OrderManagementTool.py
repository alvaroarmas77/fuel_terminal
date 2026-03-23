import os
import pandas as pd
import io
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account

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

    def _run(self, action: str = "create", order_id: str = None, dispatcher_email: str = None, 
             plate_id: str = None, driver_name: str = None, fuel_volume: str = None, 
             assigned_island: str = None, appointment_date: str = None, 
             start_time: str = None, end_time: str = None) -> str:
        
        account = get_ms_account()
        if not account:
            return "ERROR_CONEXIÓN: Fallo de autenticación en Microsoft Graph."

        try:
            target_user = "soportesap@frontera-virtual.com"
            # CAMBIO MÍNIMO: Especificar resource para permisos de Aplicación
            drive = account.storage().get_drive_by_endpoint(target_user)
            
            root = drive.get_root()
            folder = root.get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control_Orders.xlsx')
            
            # Lógica original de búsqueda de carpeta/archivo
            try:
                folder = root.get_item('Fuel_Terminal_System')
                file_item = folder.get_item('Master_Control_Orders.xlsx')
            except Exception:
                # Si no está en la carpeta, intenta en la raíz
                file_item = root.get_item('Master_Control_Orders.xlsx')

            # Descarga y lectura del Excel
            content = file_item.download()
            try:
                df = pd.read_excel(io.BytesIO(content))
            except Exception:
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')

            # --- ACCIÓN: LECTURA ---
            if action == "read":
                if not order_id: return "ERROR: Falta order_id."
                result = df[df['OrderID'].astype(str) == str(order_id)]
                return result.to_string() if not result.empty else "ORDEN_NO_ENCONTRADA"

            # --- ACCIÓN: ELIMINACIÓN ---
            if action == "delete":
                if not order_id: return "ERROR: Falta order_id."
                df = df[df['OrderID'].astype(str) != str(order_id)]
                self._save_to_excel(file_item, df)
                return f"ORDEN_{order_id}_ELIMINADA"

            # --- ACCIÓN: CREACIÓN (Manejo Multi-unidad) ---
            if action == "create":
                # Limpieza y preparación de listas
                plates = [p.strip() for p in str(plate_id).split(',')]
                drivers = [d.strip() for d in str(driver_name).split(',')]
                volumes = [v.strip() for v in str(fuel_volume).split(',')]
                
                num_units = len(plates)
                
                # Aseguramos que las listas tengan el mismo largo que las placas
                if len(drivers) < num_units: drivers = (drivers * num_units)[:num_units]
                if len(volumes) < num_units: volumes = (volumes * num_units)[:num_units]

                new_entries = []
                for i in range(num_units):
                    new_entries.append({
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
                    })
                
                # Concatenamos y guardamos
                df_final = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
                self._save_to_excel(file_item, df_final)
                return f"REGISTRO_EXITOSO: {num_units} unidades en la orden {order_id}."

        except Exception as e:
            return f"ERROR_OPERATIVO_EXCEL: {str(e)}"

    def _save_to_excel(self, file_item, df):
        """Función auxiliar para subir el archivo actualizado a OneDrive"""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        # Usamos upload() para sobreescribir el contenido en OneDrive
        file_item.upload(output)