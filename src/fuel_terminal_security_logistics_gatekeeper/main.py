#!/usr/bin/env python
import os
secret = os.getenv("AZURE_CLIENT_SECRET", "")
print(f"DEBUG: Longitud del secreto cargado: {len(secret)}")
import sys
from datetime import datetime
from dotenv import load_dotenv

# 1. CARGA DE ENTORNO: Debe ser lo primero para que microsoft_graph lea las keys
load_dotenv()

# Bypass para telemetría y evitar que CrewAI busque OpenAI por defecto
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["OTEL_SDK_DISABLED"] = "true"

# Importaciones después de cargar el entorno
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account

def run():
    print("DEBUG: Validando conexión con Microsoft Azure...")
    # 2. PRE-FLIGHT CHECK: Si esto falla, sys.exit(1) evita gastos innecesarios de LLM
    account = get_ms_account()
    if not account:
        print("\n[!] ERROR CRÍTICO: No se pudo establecer conexión con Microsoft Graph.")
        sys.exit(1)
    
    print("DEBUG: Conexión exitosa. Iniciando Crew...")
    ahora = datetime.now()
    
    # Inputs optimizados para multi-unidad
    inputs = {
        'dispatcher_email': 'soportesap@frontera-virtual.com',
        'driver_name': 'Juan Pérez, Ricardo Gómez',
        'plate_id': 'ABC-1234, XYZ-9876',
        'truck_plate': 'ABC-1234, XYZ-9876', 
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:00:00'), 
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        'fuel_volume': '5000, 3000',
        'order_id': f"ORD-{ahora.strftime('%y%m%d%H%M')}"
    }

    try:
        # Instanciamos y ejecutamos
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"ERROR DURANTE LA EJECUCIÓN DEL CREW: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()