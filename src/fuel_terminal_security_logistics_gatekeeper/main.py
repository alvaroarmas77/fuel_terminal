#!/usr/bin/env python
import sys
import os
from datetime import datetime
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    """
    Ejecuta la Crew de logística de la terminal.
    """
    print(f"\n--- [SISTEMA INICIADO] - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    print("Ubicación: Terminal Sur - Surquillo")
    print("Motor: Gemini 3.1 Pro Preview\n")

    # Definición de inputs de forma explícita
    # Estos valores alimentan las variables {driver_id}, {truck_plate}, etc. en tasks.yaml
    inputs = {
        'driver_id': 'D-9876',
        'truck_plate': 'ABC-1234',
        'driver_name': 'Juan Pérez',
        'requested_datetime': datetime.now().isoformat(),
        'fuel_volume': '5000 Gallons',
        'dispatcher_email': 'logistics@terminal-sur.com'
    }

    try:
        # Instanciamos la clase de la Crew
        # El método .crew() retorna la instancia de CrewAI ya validada
        gatekeeper_crew = FuelTerminalSecurityLogisticsGatekeeperCrew().crew()
        
        # Iniciamos el proceso
        result = gatekeeper_crew.kickoff(inputs=inputs)

        print("\n--- [EJECUCIÓN FINALIZADA CON ÉXITO] ---")
        print(f"Resultado Final:\n{result}")

    except Exception as e:
        print(f"\n[ERROR CRÍTICO DURANTE LA EJECUCIÓN]:\n{str(e)}")
        # Forzamos la salida con error para que GitHub Actions lo marque como fallido
        sys.exit(1)

def train():
    """
    Entrena la crew para mejorar la precisión (opcional).
    """
    inputs = {
        'driver_id': 'D-9876',
        'truck_plate': 'ABC-1234',
        'driver_name': 'Juan Pérez',
        'requested_datetime': datetime.now().isoformat(),
        'fuel_volume': '5000 Gallons',
        'dispatcher_email': 'logistics@terminal-sur.com'
    }
    try:
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().train(
            n_iterations=int(sys.argv[1]) if len(sys.argv) > 1 else 5, 
            filename='training_data.pkl', 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"Error durante el entrenamiento: {e}")

if __name__ == "__main__":
    run()