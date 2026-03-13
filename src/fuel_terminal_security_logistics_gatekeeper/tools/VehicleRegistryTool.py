import os
import pandas as pd
import io
import sys
from O365 import Account, FileSystemTokenBackend
# Si también usas la conexión de tu utilidad:
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
from typing import Optional

try:
    from crewai_tools import BaseTool
except ImportError:
    try:
        from crewai.tools import BaseTool
    except ImportError:
        from crewai.tools.base_tool import BaseTool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from utils.microsoft_graph import get_ms_account
except ImportError:
    try:
        from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
    except ImportError:
        def get_ms_account(): return None

class VehicleRegistryTool(BaseTool):
    name: str = "vehicle_registry_tool"
    description: str = (
        "Valida la placa del camión y el nombre del conductor en la pestaña 'Vehicle_registry' "
        "del archivo Master_Control.xlsx. Solo debe usarse para validación de activos."
    )

    def _run(self, plate_id: str, driver_name: str) -> str:
        try:
            account = get_ms_account()
            if not account:
                return "ERROR_CONEXIÓN: No se pudo conectar con Microsoft Graph. Verifique el token."

            drive = account.storage().get_default_drive()
            root = drive.get_root()
            try:
                folder = root.get_item('Fuel_Terminal_System')
                file_item = folder.get_item('Master_Control.xlsx')
            except Exception:
                file_item = root.get_item('Master_Control.xlsx')
                
            content = file_item.download()
            try:
                df_veh = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_registry")
            except Exception:
                df_veh = pd.read_excel(io.BytesIO(content), sheet_name="Vehicle_registry", engine='openpyxl')
            
            p_limpia = str(plate_id).strip().upper()
            d_limpio = str(driver_name).strip().lower()
            
            match = df_veh[
                (df_veh['Truck Plate'].astype(str).str.strip().upper() == p_limpia) & 
                (df_veh['Driver Name'].astype(str).str.strip().lower() == d_limpio)
            ]
            
            if not match.empty:
                id_interno = match['ID_Interno'].iloc[0]
                return (f"PHASE_2_SUCCESS: ACTIVOS VALIDADOS - Vehículo: {p_limpia} - "
                        f"Conductor: {driver_name} - ID Interno: {id_interno}. "
                        f"Proceder a asignación de isla.")
            
            return (f"RECHAZO_FASE_2: Error en validación de activos para la placa {p_limpia}. "
                    f"El vehículo o el conductor no están autorizados en el registro oficial.")

        except Exception as e:
            return f"ERROR_SISTEMA: Fallo al leer el registro de vehículos. Detalle: {str(e)}"