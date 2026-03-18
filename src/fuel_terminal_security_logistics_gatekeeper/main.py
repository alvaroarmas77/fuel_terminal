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
    print(f"DEBUG: Versión de O365 cargada: {getattr(O365, '__version__', 'Desconocida')}\")
except ImportError:
    print("\n[!] ERROR CRÍTICO: Librería O365 no encontrada.")
    sys.exit(1)

# Importación del Crew
try:
    from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
    # Importamos la función de conexión para la validación previa
    from fuel_terminal_security_logistics_gatekeeper.utils.microsoft_graph import get_ms_account
except ImportError as e:
    print(f"\n[!] ERROR DE IMPORTACIÓN: {e}")
    sys.exit(1)

def run():
    # --- VALIDACIÓN PREVIA DE CONEXIÓN (PUNTO 5) ---
    # Si el secreto está bien pero hay un error de red o handshake, el script muere aquí
    # antes de llamar a Gemini y gastar la cuota.
    print("DEBUG: Verificando conexión con Microsoft Graph antes de iniciar Crew...")
    account = get_ms_account()
    if not account:
        print("\n[!] ERROR CRÍTICO: No se pudo establecer conexión con Microsoft Azure.")
        print("Revisa que el CLIENT_SECRET sea el 'Value' y que el Tenant ID sea correcto.")
        sys.exit(1)
    
    print("DEBUG: Conexión exitosa. Iniciando motor de agentes...")

    ahora = datetime.now()
    
    # --- CONFIGURACIÓN DE ENTRADAS (INPUTS) ---
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
        print(f"\n--- Iniciando Crew para la Orden: {inputs['order_id']} ---\n")
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"\n[!] ERROR DURANTE LA EJECUCIÓN: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()