import sys
import os
import warnings
from datetime import datetime

# --- PATH FIX: Esto permite que GitHub Actions encuentre tus archivos ---
# Agregamos la carpeta 'src' al camino de búsqueda de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)
# -----------------------------------------------------------------------

try:
    from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
except ModuleNotFoundError:
    # Fallback si el nombre del módulo falla: importar directamente
    from crew import FuelTerminalSecurityLogisticsGatekeeperCrew

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

def run():
    """Ejecuta la tripulación de la Terminal."""
    inputs = {
        'current_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    print(f"### Iniciando Operaciones con Gemini 3.1 Pro Preview ###")
    try:
        # Ejecución del Crew
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
        print("### Proceso completado con éxito ###")
    except Exception as e:
        print(f"Error en ejecución: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()