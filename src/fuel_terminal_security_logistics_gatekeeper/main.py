import sys
import os
import warnings
from datetime import datetime

# --- FIX DE RUTAS PARA GITHUB ACTIONS ---
# Esto obliga a Python a reconocer la carpeta 'src' como raíz de módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importación segura de tu lógica
try:
    from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
except ImportError:
    import src.fuel_terminal_security_logistics_gatekeeper.crew as crew_mod
    FuelTerminalSecurityLogisticsGatekeeperCrew = crew_mod.FuelTerminalSecurityLogisticsGatekeeperCrew

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

def run():
    """Punto de entrada para el Agente Gatekeeper"""
    inputs = {
        'current_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'terminal_location': 'Terminal Sur - Surquillo'
    }
    
    print(f"--- [SISTEMA INICIADO] - Modelo: Gemini 3.1 Pro Preview ---")
    try:
        # Iniciamos la tripulación
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
        print("--- [OPERACIÓN FINALIZADA] ---")
    except Exception as e:
        print(f"--- [ERROR CRÍTICO]: {e} ---")
        sys.exit(1)

if __name__ == "__main__":
    run()