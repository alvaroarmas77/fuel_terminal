import sys
import warnings
from datetime import datetime
# Importamos tu clase desde el archivo crew.py
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

def run():
    """Ejecuta la tripulación de la Terminal."""
    inputs = {
        'current_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    print(f"### Iniciando Operaciones con Gemini 3.1 Pro Preview ###")
    try:
        # Aquí lanzamos la lógica definida en crew.py
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
        print("### Proceso completado con éxito ###")
    except Exception as e:
        print(f"Error en ejecución: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()