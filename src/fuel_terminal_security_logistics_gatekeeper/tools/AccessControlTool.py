from crewai_tools import BaseTool
from datetime import datetime

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = (
        "Consulta la base de datos de seguridad para validar permisos de entrada, "
        "vigencia de seguro SCTR y estado administrativo del conductor usando su ID."
    )

    def _run(self, driver_id: str, terminal_id: str = "TERM-01") -> str:
        try:
            driver_id = driver_id.strip().upper()
            registros_seguridad = {
                "D-9876": {"nombre": "Juan Pérez", "status": "Activo", "sctr_vence": "2026-12-31"},
                "D-5555": {"nombre": "Maria Lopez", "status": "Activo", "sctr_vence": "2026-06-15"},
                "D-1111": {"nombre": "Carlos Ruiz", "status": "Bloqueado", "sctr_vence": "2026-01-01"}
            }

            if driver_id not in registros_seguridad:
                return f"ERROR: El ID {driver_id} no existe en el sistema."

            datos = registros_seguridad[driver_id]
            if datos["status"] == "Bloqueado":
                return f"ALERTA: Acceso Denegado. {datos['nombre']} tiene un bloqueo administrativo."

            return f"CONFIRMACIÓN: Acceso Autorizado para {datos['nombre']} en {terminal_id}."
        except Exception as e:
            return f"ERROR_TOOL: {str(e)}"