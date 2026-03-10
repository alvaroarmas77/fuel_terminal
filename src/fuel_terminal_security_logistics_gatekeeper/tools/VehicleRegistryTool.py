import pandas as pd
import io
from typing import Optional
from crewai_tools import BaseTool

try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    def get_ms_account(): return None

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = (
        "Usa esta herramienta para validar: "
        "1. (Fase 1) Si el dispatcher_email está autorizado en 'Authorized_Users'. "
        "2. (Fase 2) Si truck_plate y driver_name están registrados en 'Vehicle_Registry'."
    )

    def _run(self, dispatcher_email: Optional[str] = None, truck_plate: Optional[str] = None, driver_name: Optional[str] = None) -> str:
        try:
            account = get_ms_account()
            if not account:
                return "ERROR_AUTH: No se pudo conectar con Microsoft Graph."
            
            drive = account.storage().get_default_drive()
            # Navegación por la carpeta raíz del sistema
            folder = drive.get_root().get_item('Fuel_Terminal_System')
            file_item = folder.get_item('Master_Control.xlsx')
            content = file_item.download()
            
            # --- LÓGICA FASE 1: Validación de Usuario ---
            if dispatcher_email and not truck_plate:
                df_users = pd.read_excel(io.BytesIO(content), sheet_name="Authorized_Users", engine='openpyxl')
                email_limpio = str(dispatcher_email).strip().lower()
                
                # Encabezados: Email, Nombre, Empresa
                if email_limpio in df_users['Email'].astype(str).str.lower().values:
                    return f"PHASE_1_SUCCESS: El usuario {email_limpio} está registrado. Proceder a Fase 2."
                else:
                    return f"RECHAZO_FASE_1: El correo {email_limpio} no es un usuario registrado. No se puede continuar."

            # --- LÓGICA FASE 2: Validación de Camión y Conductor ---
            if truck_plate and driver_name:
                df_fleet = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_Registry", engine='openpyxl')
                plate_limpia = str(truck_plate).strip().upper()
                driver_limpio = str(driver_name).strip().lower()

                # Encabezados: Truck Plate, Driver Name, Driver Email, ID_Interno
                # Validamos que AMBOS existan en la misma fila (o al menos en la base)
                match_plate = df_fleet['Truck Plate'].astype(str).str.upper() == plate_limpia
                match_driver = df_fleet['Driver Name'].astype(str).str.lower() == driver_limpio
                
                if any(match_plate & match_driver):
                    return f"PHASE_2_SUCCESS: Camión {plate_limpia} y Conductor {driver_name} validados. Proceder a Fase 3."
                else:
                    return f"RECHAZO_FASE_2: El camión {plate_limpia} o el conductor {driver_name} no están registrados en la flota oficial."

            return "ERROR_PARAM: Se requiere dispatcher_email O (truck_plate Y driver_name)."

        except Exception as e:
            return f"ERROR_SISTEMA: Fallo al leer Master_Control.xlsx. Detalle: {str(e)}"