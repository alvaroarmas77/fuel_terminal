#!/usr/bin/env python
import sys
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    """
    Ejecuta la Crew de logística de la terminal.
    """
    ahora = datetime.now()
    
    print(f"\n--- [SISTEMA INICIADO] - {ahora.strftime('%Y-%m-%d %H:%M:%S')} ---")
    print("Ubicación: Terminal Sur - Surquillo")
    print("Motor: Gemini 3.1 Pro Preview\n")

    # SOLUCIÓN: Añadimos 'current_date' que es lo que pide el tasks.yaml
    inputs = {
        'driver_id': 'D-9876',
        'truck_plate': 'ABC-1234',
        'driver_name': 'Juan Pérez',
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:%M:%S'),
        'current_date': ahora.strftime('%Y-%m-%d'), # <--- ESTA ES LA KEY FALTANTE
        'fuel_volume': '5000 Gallons',
        'dispatcher_email': 'logistics@terminal-sur.com'
    }

    try:
        gatekeeper_crew = FuelTerminalSecurityLogisticsGatekeeperCrew().crew()
        result = gatekeeper_crew.kickoff(inputs=inputs)

        print("\n--- [EJECUCIÓN FINALIZADA CON ÉXITO] ---")
        print(f"Resultado Final:\n{result}")

    except Exception as e:
        # Imprimimos el error limpio para depuración técnica
        print(f"\n[ERROR CRÍTICO DURANTE LA EJECUCIÓN]:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()