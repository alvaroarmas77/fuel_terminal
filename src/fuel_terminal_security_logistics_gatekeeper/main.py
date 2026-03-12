#!/usr/bin/env python
import os
import sys
from datetime import datetime

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
    from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
except ImportError as e:
    print(f"\n[!] ERROR DE IMPORTACIÓN: No se encuentra el paquete del Crew. {e}")
    sys.exit(1)

def run():
    ahora = datetime.now()
    
    # --- CONFIGURACIÓN DE ENTRADAS (INPUTS) ---
    # Nota: Para probar la multi-unidad, enviamos strings separados por comas.
    # El Security Specialist validará el dispatcher_email (Fase 1).
    # El Registry Specialist validará las placas y conductores (Fase 2).
    inputs = {
        # Identificadores de Personas (Fases 1, 2 y 5)
        'dispatcher_email': 'logistics@terminal-sur.com', # Debe estar en 'Authorized_Users'
        'driver_name': 'Juan Pérez, Ricardo Gómez',      # Dos conductores
        'driver_email': 'juan.perez@transporte.com, ricardo.g@transporte.com',
        
        # Identificadores de Vehículo (Fases 2 y 3)
        'plate_id': 'ABC-1234, XYZ-9876',                 # Dos placas
        'truck_plate': 'ABC-1234, XYZ-9876', 
        
        # Datos de Tiempo y Ubicación (Fase 3)
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:00:00'), 
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        
        # Datos de Orden (Fase 4)
        'fuel_volume': '5000, 3000',                     # Volúmenes para cada camión
        'order_id': f"ORD-{ahora.strftime('%y%m%d%H%M')}",
        
        # Placeholders que serán llenados por los agentes durante el flujo
        'assigned_island': '',
        'appointment_date': ahora.strftime('%Y-%m-%d'),
        'start_time': '', 
        'end_time': ''
    }

    try:
        print(f"\n--- Iniciando Crew para la Orden Maestra: {inputs['order_id']} ---")
        
        # Instanciamos y ejecutamos
        gatekeeper_crew = FuelTerminalSecurityLogisticsGatekeeperCrew().crew()
        result = gatekeeper_crew.kickoff(inputs=inputs)
        
        print(f"\n--- [RESULTADO FINAL DE LA OPERACIÓN] ---\n{result}")
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO EN EL FLUJO]: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()