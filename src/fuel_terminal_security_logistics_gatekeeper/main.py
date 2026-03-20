#!/usr/bin/env python
import os
import sys
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account

# Bypass para telemetría y OpenAI
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["OTEL_SDK_DISABLED"] = "true"

def run():
    print("DEBUG: Validando conexión con Microsoft Azure...")
    account = get_ms_account()
    if not account:
        print("\n[!] ERROR CRÍTICO: No se pudo establecer conexión con Microsoft Graph.")
        sys.exit(1)
    
    print("DEBUG: Conexión exitosa. Iniciando Crew...")
    ahora = datetime.now()
    
    inputs = {
        'dispatcher_email': 'soportesap@frontera-virtual.com',
        'driver_name': 'Juan Pérez, Ricardo Gómez',
        'driver_email': 'juan.perez@transporte.com, ricardo.g@transporte.com',
        'plate_id': 'ABC-1234, XYZ-9876',
        'truck_plate': 'ABC-1234, XYZ-9876', 
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:00:00'), 
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        'fuel_volume': '5000, 3000',
        'order_id': f"ORD-{ahora.strftime('%y%m%d%H%M')}",
        'assigned_island': '',
        'appointment_date': ahora.strftime('%Y-%m-%d'),
        'start_time': '', 
        'end_time': ''
    }

    try:
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    run()