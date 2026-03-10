#!/usr/bin/env python
import sys
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    """
    Ejecuta la Crew de logística de la terminal con mapeo completo de variables.
    """
    ahora = datetime.now()
    
    print(f"\n--- [SISTEMA INICIADO] - {ahora.strftime('%Y-%m-%d %H:%M:%S')} ---")
    print("Ubicación: Terminal Sur - Surquillo")
    print("Motor: Gemini 3.1 Pro Preview\n")

    # Mapeo exhaustivo para evitar KeyErrors en los archivos YAML
    inputs = {
        'driver_id': 'D-9876',
        'driver_name': 'Juan Pérez',
        'truck_plate': 'ABC-1234',
        'plate_id': 'ABC-1234',
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:%M:%S'),
        'current_date': ahora.strftime('%Y-%m-%d'),
        'fuel_volume': '5000 Gallons',
        'dispatcher_email': 'logistics@terminal-sur.com',
        'location': 'Terminal Sur - Surquillo',
        'terminal_location': 'Terminal Sur - Surquillo', # <--- Crucial para Fase 3
        'terminal_id': 'TERM-01',
        'order_id': f"ORD-{ahora.strftime('%y%m%d%H%M')}" # <--- Crucial para Fase 4
    }

    try:
        # Instancia de la Crew corregida
        gatekeeper_crew = FuelTerminalSecurityLogisticsGatekeeperCrew().crew()
        
        # Inicio de la ejecución
        result = gatekeeper_crew.kickoff(inputs=inputs)

        print("\n--- [EJECUCIÓN FINALIZADA CON ÉXITO] ---")
        print(f"Resultado Final:\n{result}")

    except Exception as e:
        # Captura de errores para el runner de GitHub
        print(f"\n[ERROR CRÍTICO DURANTE LA EJECUCIÓN]:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()
# Prueba de ejecución holística 01