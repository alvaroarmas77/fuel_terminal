#!/usr/bin/env python
import sys
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    """
    Ejecuta la Crew de logística con validación estricta de Phase 1 a Phase 5.
    """
    ahora = datetime.now()
    
    print(f"\n--- [SISTEMA INICIADO] - {ahora.strftime('%Y-%m-%d %H:%M:%S')} ---")
    print("Ubicación: Terminal Sur - Surquillo")
    print("Protocolo: Validación de Usuario y Activos (Phase 1-5)\n")

    # Inputs normalizados para evitar fallos en las Tools
    inputs = {
        'dispatcher_email': 'logistics@terminal-sur.com', # <--- Fase 1
        'truck_plate': 'ABC-1234',                       # <--- Fase 2
        'driver_name': 'Juan Pérez',                     # <--- Fase 2
        'driver_id': 'D-9876',                           # <--- Fase 3 (SCTR)
        'fuel_volume': '5000 Gallons',
        'assigned_island': 'Island 4',
        'location': 'Terminal Sur - Surquillo',
        'start_time': ahora.strftime('%H:%M'),
        'end_time': (ahora).strftime('%H:%M'), # Puedes ajustar esto
        'current_date': ahora.strftime('%Y-%m-%d')
    }

    try:
        # Instancia de la Crew
        gatekeeper_crew = FuelTerminalSecurityLogisticsGatekeeperCrew().crew()
        
        # Inicio de la ejecución
        result = gatekeeper_crew.kickoff(inputs=inputs)

        print("\n--- [EJECUCIÓN FINALIZADA CON ÉXITO] ---")
        print(f"Resultado Final:\n{result}")

    except Exception as e:
        print(f"\n[ERROR CRÍTICO DURANTE LA EJECUCIÓN]:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()