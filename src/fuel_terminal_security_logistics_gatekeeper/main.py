#!/usr/bin/env python
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargamos el entorno (Secrets en GitHub o .env local)
load_dotenv()

# SOLUCIÓN DE BLINDAJE: Eliminamos el 'fake-key' para que no interfiera con la clase LLM
os.environ["OTEL_SDK_DISABLED"] = "true"

from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    print("DEBUG: Iniciando Gatekeeper System...")
    ahora = datetime.now()
    
    # Verificación de integridad de la llave (sin mostrarla)
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        print("ERROR: GOOGLE_API_KEY no encontrada en el entorno.")
        sys.exit(1)
    print(f"DEBUG: API KEY detectada (Longitud: {len(key)})")

    inputs = {
        'dispatcher_email': 'cliente_prueba@empresa.com',
        'driver_email': 'conductor1@transporte.com, conductor2@transporte.com', 
        'driver_name': 'Juan Pérez, Ricardo Gómez',
        'truck_plate': 'ABC-1234, XYZ-9876', 
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:00:00'), 
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        'fuel_volume': '5000, 3000',
        'order_id': f"ORD-{ahora.strftime('%y%m%d-%H%M')}"
    }

    try:
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"ERROR DURANTE LA EJECUCIÓN: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()