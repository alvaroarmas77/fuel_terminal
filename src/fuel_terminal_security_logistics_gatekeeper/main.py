#!/usr/bin/env python
import os
import sys
from datetime import datetime

# --- BYPASS PARA FORZAR GEMINI 3.1 Y EVITAR ERROR DE OPENAI ---
# CrewAI 0.28.0 busca esta variable antes de iniciar, incluso si usas Gemini.
os.environ["OPENAI_API_KEY"] = "fake-key-to-bypass-openai-check-for-gemini-3.1"
# Deshabilitamos telemetría para evitar warnings adicionales en el log de GitHub
os.environ["OTEL_SDK_DISABLED"] = "true"

def prepare_microsoft_token():
    """
    Reconstruye el archivo o365_token.txt desde un Secret de GitHub.
    Esto evita que el script pida autenticación manual en el servidor.
    """
    token_json = os.getenv("O365_TOKEN_JSON")
    if token_json:
        try:
            with open("o365_token.txt", "w") as f:
                f.write(token_json)
            print("DEBUG: Archivo o365_token.txt generado exitosamente desde variable de entorno.")
        except Exception as e:
            print(f"DEBUG: Error al escribir o365_token.txt: {e}")
    else:
        print("DEBUG: [!] Advertencia: No se detectó O365_TOKEN_JSON. Las herramientas podrían fallar.")

# --- BLOQUE DE SEGURIDAD DE LIBRERÍAS ---
try:
    import O365
    import msal
    print(f"DEBUG: Versión de O365 cargada: {getattr(O365, '__version__', 'Desconocida')}")
except ImportError:
    print("\n[!] ERROR CRÍTICO: Librerías no encontradas.")
    print("Por favor, asegúrate de que 'requirements.txt' contenga 'O365' y 'msal'.")
    sys.exit(1)

# Importación del Crew
try:
    # Asegúrate de que la ruta del paquete sea correcta según tu estructura de carpetas
    from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
except ImportError as e:
    print(f"\n[!] ERROR DE IMPORTACIÓN: No se encuentra el paquete del Crew. {e}")
    sys.exit(1)

def run():
    # --- PREPARACIÓN DE ENTORNO ---
    prepare_microsoft_token()
    
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
        
        # Instanciamos la clase del Crew
        crew_instance = FuelTerminalSecurityLogisticsGatekeeperCrew()
        
        # Obtenemos el objeto Crew mediante el método decorado con @crew
        gatekeeper_crew = crew_instance.crew()
        
        # Ejecutamos el flujo
        result = gatekeeper_crew.kickoff(inputs=inputs)
        
        print(f"\n--- [RESULTADO FINAL DE LA OPERACIÓN] ---\n{result}")
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO EN EL FLUJO]: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()