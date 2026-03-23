#!/usr/bin/env python
import os
import sys
import shutil
from datetime import datetime
from dotenv import load_dotenv

# 1. FUNCIÓN DE LIMPIEZA DE CACHÉ
def clean_cache():
    """Elimina archivos .pyc y carpetas __pycache__ para evitar errores de versiones viejas."""
    print("DEBUG: Limpiando caché de Python (__pycache__)...")
    for root, dirs, files in os.walk('.', topdown=False):
        for name in files:
            if name.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, name))
                except:
                    pass
        for name in dirs:
            if name == '__pycache__':
                try:
                    shutil.rmtree(os.path.join(root, name))
                except:
                    pass

# 2. CONFIGURACIÓN DE ENTORNO
load_dotenv()
os.environ["OTEL_SDK_DISABLED"] = "true"

# Importamos la Crew después de configurar el entorno
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    print("DEBUG: Iniciando Gatekeeper System...")
    ahora = datetime.now()
    
    # Verificación de integridad de la llave
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        print("ERROR: GOOGLE_API_KEY no encontrada en el entorno.")
        sys.exit(1)
    print(f"DEBUG: API KEY detectada (Longitud: {len(key)})")

    # 3. INPUTS (Configurados para un único camión según la Fase 2)
    inputs = {
        'dispatcher_email': 'cliente_prueba@empresa.com',
        'driver_email': 'conductor1@transporte.com', 
        'driver_name': 'Juan Pérez',
        'truck_plate': 'ABC-1234',
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:00:00'), 
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        'fuel_volume': '5000',
        'order_id': f"ORD-{ahora.strftime('%y%m%d-%H%M')}"
    }

    try:
        # Ejecución del orquestador
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"ERROR DURANTE LA EJECUCIÓN: {e}")
        sys.exit(1)

# 4. PUNTO DE ENTRADA PRINCIPAL
if __name__ == "__main__":
    clean_cache()  # <--- Ejecuta la limpieza primero para forzar lectura de AccessControlTool.py
    run()          # <--- Inicia la lógica del Agente