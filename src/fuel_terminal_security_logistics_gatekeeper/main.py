#!/usr/bin/env python
import sys
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    ahora = datetime.now()
    
    # Mapeo homogeneizado para que coincida con Tools y Tasks
    inputs = {
        # Identificadores de Personas (Fases 1, 2 y 5)
        'driver_id': 'D-9876',
        'driver_name': 'Juan Pérez',
        'driver_email': 'juan.perez@transporte.com',
        'dispatcher_email': 'logistics@terminal-sur.com',
        'sender_email': 'logistics@terminal-sur.com',
        
        # Identificadores de Vehículo (Fases 2 y 3)
        'plate_id': 'ABC-1234', 
        'truck_plate': 'ABC-1234', # Mantenemos ambos por compatibilidad con los YAML
        
        # Datos de Tiempo y Ubicación (Fase 3)
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:00:00'), 
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        'terminal_location': 'Terminal Sur - Surquillo',
        
        # Datos de Orden (Fase 4)
        'fuel_volume': '5000', # Solo el número o texto, la Tool añade "Gallons" si lo pusiste en el encabezado
        'order_id': f"ORD-{ahora.strftime('%y%m%d%H%M')}",
        
        # Placeholders para que CrewAI gestione los datos que vienen del Calendario (Fase 3 -> Fase 4)
        'appointment_date': ahora.strftime('%Y-%m-%d'),
        'start_time': '', 
        'end_time': '',
        'assigned_island': ''
    }

    try:
        # Instanciamos el Crew con la configuración limpia
        gatekeeper_crew = FuelTerminalSecurityLogisticsGatekeeperCrew().crew()
        
        # Ejecución del proceso secuencial
        result = gatekeeper_crew.kickoff(inputs=inputs)
        
        print(f"\n--- [RESULTADO FINAL DE LA OPERACIÓN] ---\n{result}")
        
    except Exception as e:
        # Captura de errores de importación o ejecución
        print(f"\n[ERROR CRÍTICO EN EL FLUJO]: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()