import pandas as pd
import io
import os
from datetime import datetime
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# Importación del helper de autenticación
try:
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError:
    from utils.microsoft_graph import get_ms_account

class OrderManagementInput(BaseModel):
    """Esquema para el registro final de la orden de carga."""
    dispatcher_email: str = Field(..., description="Email del despachador que solicitó la carga.")
    truck_plate: str = Field(..., description="Placa del camión validada.")
    driver_name: str = Field(..., description="Nombre del conductor validado.")
    fuel_volume: str = Field(..., description="Volumen de combustible solicitado (ej. 5000 Gal).")
    assigned_island: str = Field(..., description="La isla asignada por el coordinador (ej. Terminal_Isla_3).")
    start_time: str = Field(..., description="Hora de inicio del slot.")
    end_time: str = Field(..., description="Hora de fin del slot.")

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = (
        "Crea el registro oficial en 'Master_Control_Orders.xlsx' en OneDrive. "
        "Genera un ID único correlativo (FL-2026-NNNN) para cada operación exitosa."
    )
    args_schema: Type[BaseModel] = OrderManagementInput

    def _run(self, **kwargs) -> str:
        try:
            account = get_ms_account()
            drive = account.storage().get_default_drive()
            folder_path = 'Fuel_Terminal_System'
            file_name = 'Master_Control_Orders.xlsx'
            full_path = f"{folder_path}/{file_name}"
            
            # 1. Intentar obtener el archivo actual para mantener la correlatividad
            try:
                file_item = drive.get_item_by_path(full_path)
                content = file_item.download()
                df = pd.read_excel(io.BytesIO(content))
            except:
                # Si el archivo no existe, iniciamos uno nuevo con las columnas correctas
                df = pd.DataFrame(columns=[
                    "OrderID", "Date", "Dispatcher", "Plate", "Driver", "Volume", "Island", "Start", "End"
                ])

            # 2. Generar el ID correlativo (FL-2026-0001, 0002, etc.)
            new_id = f"FL-2026-{len(df) + 1:04d}"
            
            # 3. Preparar la nueva fila
            new_entry = {
                "OrderID": new_id,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Dispatcher": kwargs.get('dispatcher_email'),
                "Plate": kwargs.get('truck_plate'),
                "Driver": kwargs.get('driver_name'),
                "Volume": kwargs.get('fuel_volume'),
                "Island": kwargs.get('assigned_island'),
                "Start": kwargs.get('start_time'),
                "End": kwargs.get('end_time')
            }

            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

            # 4. Guardar el DataFrame en un buffer de memoria
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            # 5. Subir a OneDrive (sobrescribe el archivo existente con la nueva data)
            target_folder = drive.get_item_by_path(folder_path)
            target_folder.upload(output.getvalue(), name=file_name)
            
            return f"OPERACION_EXITOSA: Orden registrada con ID {new_id} en OneDrive."

        except Exception as e:
            return f"ERROR_CRITICO: No se pudo completar el registro de la orden: {str(e)}"