#!/usr/bin/env python
import os
import sys
from datetime import datetime

# --- BYPASS PARA FORZAR GEMINI ---
os.environ["OPENAI_API_KEY"] = "fake-key-to-bypass-openai-check"
os.environ["OTEL_SDK_DISABLED"] = "true"

# --- BLOQUE DE SEGURIDAD DE LIBRERÍAS ---
try:
    import O365
    print(f"DEBUG: Versión de O365 cargada: {getattr(O365, '__version__', 'Desconocida')}")
except ImportError:
    print("\n[!] ERROR CRÍTICO: Librería O365 no encontrada.")
    sys.exit(1)

# Importación del Crew y la utilidad de conexión
try:
    from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError as e:
    print(f"\n[!] ERROR DE IMPORTACIÓN: {e}")
    sys.exit(1)

def run():
    # --- VALIDACIÓN PREVIA (Punto de control para no quemar tokens de Gemini) ---
    print("DEBUG: Validando credenciales de Microsoft Graph...")
    account = get_ms_account()
    if not account:
        print("\n[!] ERROR: La conexión con Azure falló. El proceso se detiene para proteger la cuota de API.")
        sys.exit(1)
    
    print("DEBUG: Conexión exitosa. Iniciando agentes...")

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
        print(f"\n--- Ejecutando Gatekeeper: {inputs['order_id']} ---\n")
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"\n[!] ERROR EN EJECUCIÓN: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()