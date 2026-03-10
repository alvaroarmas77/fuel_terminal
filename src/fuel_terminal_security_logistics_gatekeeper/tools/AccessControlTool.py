import os
from datetime import datetime
from typing import Type
from pydantic import BaseModel, Field
from crewai_tools import BaseTool

class AccessControlInput(BaseModel):
    """Esquema de entrada para la validación de acceso de seguridad."""
    driver_id: str = Field(..., description="ID único del conductor (ej. D-9876).")
    terminal_id: str = Field(default="TERM-01", description="ID de la terminal de acceso.")

class AccessControlTool(BaseTool):
    name: str = "access_control_tool"
    description: str = (
        "Consulta la base de datos de seguridad para validar permisos de entrada, "
        "vigencia de seguro SCTR y estado administrativo del conductor."
    )
    args_schema: Type[BaseModel] = AccessControlInput

    def _run(self, driver_id: str, terminal_id: str = "TERM-01") -> str:
        driver_id = driver_id.strip().upper()
        try:
            # Base de datos simulada para validación lógica
            registros_seguridad = {
                "D-9876": {"nombre": "Juan Pérez", "status": "Activo", "sctr_vence": "2026-12-31"},
                "D-5555": {"nombre": "Maria Lopez", "status": "Activo", "sctr_vence": "2026-06-15"},
                "D-1111": {"nombre": "Carlos Ruiz", "status": "Bloqueado", "sctr_vence": "2026-01-01"}
            }

            if driver_id not in registros_seguridad:
                return f"ERROR: El ID {driver_id} no existe en el sistema de seguridad."

            datos = registros_seguridad[driver_id]
            if datos["status"] == "Bloqueado":
                return f"ALERTA: Acceso Denegado. El conductor {datos['nombre']} tiene un bloqueo administrativo activo."

            fecha_actual = datetime.now()
            vencimiento_sctr = datetime.strptime(datos["sctr_vence"], "%Y-%m-%d")

            if vencimiento_sctr < fecha_actual:
                return f"ALERTA: Acceso Denegado. El seguro SCTR de {datos['nombre']} expiró el {datos['sctr_vence']}."

            return (
                f"CONFIRMACIÓN: Acceso Autorizado.\n"
                f"Conductor: {datos['nombre']}\n"
                f"Terminal: {terminal_id}\n"
                f"Estado SCTR: Vigente hasta {datos['sctr_vence']}"
            )
        except Exception as e:
            return f"ERROR CRÍTICO EN ACCESS_CONTROL: {str(e)}"