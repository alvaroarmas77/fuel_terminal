#!/usr/bin/env python
import sys
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    ahora = datetime.now()
    
    # Mapeo exhaustivo de variables según tus archivos de configuración
    inputs = {
        # Para Phase 1 y 2
        'driver_id': 'D-9876',
        'driver_name': 'Juan Pérez',
        'driver_email': 'juan.perez@transporte.com',
        'dispatcher_email': 'logistics@terminal-sur.com',
        'sender_email': 'logistics@terminal-sur.com',
        
        # Para Phase 2 y 3 (Se incluyen ambos nombres por consistencia en los YAML)
        'plate_id': 'ABC-1234',
        'truck_plate': 'ABC-1234',
        
        # Datos de tiempo y ubicación
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:%00:00'), # Slots de 30 min aprox
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        'terminal_location': 'Terminal Sur - Surquillo',
        
        # Datos de Orden
        'fuel_volume': '5000 Gallons',
        'order_id': f"ORD-{ahora.strftime('%y%m%d%H%M')}"
    }

    try:
        gatekeeper_crew = FuelTerminalSecurityLogisticsGatekeeperCrew().crew()
        result = gatekeeper_crew.kickoff(inputs=inputs)
        print(f"\n--- [RESULTADO FINAL] ---\n{result}")
    except Exception as e:
        print(f"\n[ERROR CRÍTICO]: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()