#!/usr/bin/env python
import os
import sys
from datetime import datetime

# --- BYPASS PARA FORZAR GEMINI Y EVITAR ERROR DE OPENAI ---
os.environ["OPENAI_API_KEY"] = "fake-key-to-bypass-openai-check"
os.environ["OTEL_SDK_DISABLED"] = "true"

def verify_microsoft_token():
    """
    Verifica que el archivo o365_token.txt exista.
    En GitHub Actions, este archivo es creado por el paso anterior en el workflow.yml.
    """
    if os.path.exists("o365_token.txt"):
        print("DEBUG: [OK] Archivo o365_token.txt detectado. Iniciando con autenticación por token.")
    else:
        print("DEBUG: [!] ERROR CRÍTICO: No se encontró o365_token.txt.")
        print("Asegúrate de que el Workflow de GitHub esté creando el archivo correctamente.")
        # No salimos aquí para permitir que la librería intente cargar, 
        # pero es una advertencia de fallo inminente si no existe.

# --- BLOQUE DE SEGURIDAD DE LIBRERÍAS ---
try:
    import O365
    import msal
    print(f"DEBUG: Versión de O365 cargada: {getattr(O365, '__version__', 'Desconocida')}")
except ImportError:
    print("\n[!] ERROR CRÍTICO: Librerías O365 o msal no encontradas.")
    sys.exit(1)

# Importación del Crew
try:
    from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
except ImportError as e:
    print(f"\n[!] ERROR DE IMPORTACIÓN: No se encuentra el paquete del Crew. {e}")
    sys.exit(1)

def run():
    # --- BLOQUE NUEVO: RECONSTRUCCIÓN DEL TOKEN DESDE GITHUB SECRETS ---
    token_json = os.getenv('O365_TOKEN_JSON')
    if token_json:
        with open('o365_token.txt', 'w') as f:
            f.write(token_json)
    # -----------------------------------------------------------------
    # --- PREPARACIÓN DE ENTORNO ---
    verify_microsoft_token()
    
    ahora = datetime.now()
    
    # --- CONFIGURACIÓN DE ENTRADAS (INPUTS) ---
    inputs = {
        'dispatcher_email': 'logistics@terminal-sur.com',
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
        print(f"\n--- Iniciando Crew para la Orden Maestra: {inputs['order_id']} ---")
        
        # Ejecución
        crew_instance = FuelTerminalSecurityLogisticsGatekeeperCrew()
        gatekeeper_crew = crew_instance.crew()
        result = gatekeeper_crew.kickoff(inputs=inputs)
        
        print(f"\n--- [RESULTADO FINAL DE LA OPERACIÓN] ---\n{result}")
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO EN EL FLUJO]: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()