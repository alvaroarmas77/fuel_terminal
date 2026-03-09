import os
import pandas as pd
from datetime import datetime
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai_tools import BaseTool

class AccessControlInput(BaseModel):
    """Input schema para la validación de acceso de seguridad."""
    driver_id: str = Field(..., description="El ID único del conductor para verificar en la base de datos.")
    terminal_id: Optional[str] = Field("TERM-01", description="ID de la terminal donde se solicita el acceso.")

class AccessControlTool(BaseTool):
    name: str = "AccessControlTool"
    description: str = (
        "Esta herramienta consulta la base de datos de seguridad de la terminal "
        "para validar si un conductor tiene permisos de entrada activos, "
        "seguro SCTR vigente y si no tiene bloqueos administrativos."
    )
    args_schema: Type[BaseModel] = AccessControlInput

    def _run(self, driver_id: str, terminal_id: str = "TERM-01") -> str:
        """
        Ejecuta la validación lógica del conductor.
        En un entorno real, esto conectaría con un SQL o un Excel de seguridad.
        """
        print(f"\n[SISTEMA] Consultando base de datos de seguridad para: {driver_id}...")
        
        # Simulación de carga de datos (Punto de extensión para CSV/Excel)
        # database_path = os.path.join(os.getcwd(), "data", "security_db.xlsx")
        
        try:
            # Lógica de validación simulada pero estructurada
            registros_seguridad = {
                "D-9876": {"nombre": "Juan Pérez", "status": "Activo", "sctr_vence": "2026-12-31"},
                "D-5555": {"nombre": "Maria Lopez", "status": "Activo", "sctr_vence": "2026-06-15"},
                "D-1111": {"nombre": "Carlos Ruiz", "status": "Bloqueado", "sctr_vence": "2026-01-01"}
            }

            if driver_id not in registros_seguridad:
                return f"ERROR: El ID {driver_id} no existe en el Registro Nacional de Conductores de Combustible."

            datos = registros_seguridad[driver_id]
            
            if datos["status"] == "Bloqueado":
                return f"ALERTA: Acceso Denegado. El conductor {datos['nombre']} tiene un bloqueo administrativo vigente."

            # Validación de fecha de seguro
            fecha_actual = datetime.now()
            vencimiento_sctr = datetime.strptime(datos["sctr_vence"], "%Y-%m-%d")

            if vencimiento_sctr < fecha_actual:
                return f"ALERTA: Acceso Denegado. El seguro SCTR de {datos['nombre']} expiró el {datos['sctr_vence']}."

            return (
                f"CONFIRMACIÓN: Acceso Autorizado.\n"
                f"Conductor: {datos['nombre']}\n"
                f"Estado: {datos['status']}\n"
                f"SCTR: Válido hasta {datos['sctr_vence']}\n"
                f"Terminal: {terminal_id}\n"
                f"Timestamp: {fecha_actual.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except Exception as e:
            return f"ERROR CRÍTICO del sistema de seguridad: {str(e)}"