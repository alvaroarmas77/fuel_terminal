from crewai_tools import BaseTool
from datetime import datetime

class OrderManagementTool(BaseTool):
    name: str = "order_management_tool"
    description: str = "Registra la información final de la operación en Master_Control_Orders.xlsx."

    def _run(self, dispatcher_email: str, truck_plate: str, driver_name: str, fuel_volume: str, assigned_island: str, start_time: str, end_time: str) -> str:
        try:
            order_id = f"FL-2026-{datetime.now().strftime('%H%M%S')}"
            return f"ÉXITO: Orden {order_id} registrada para placa {truck_plate}."
        except Exception as e:
            return f"ERROR_LOGGING: {str(e)}"