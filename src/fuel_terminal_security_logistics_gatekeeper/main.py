#!/usr/bin/env python
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 1. CARGA DE ENTORNO
load_dotenv()

# Bypass para telemetría y evitar que CrewAI busque OpenAI por defecto
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["OTEL_SDK_DISABLED"] = "true"

# Importación de la Crew
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    print("DEBUG: Iniciando Gatekeeper System...")
    ahora = datetime.now()
    
    # Inputs homogeneizados con tasks.yaml
    # Nota: Mantenemos plate_id temporalmente por compatibilidad con las herramientas físicas
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
        # Ejecución con los inputs alineados
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"ERROR DURANTE LA EJECUCIÓN: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()