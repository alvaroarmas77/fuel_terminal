import sys
import os
import warnings
from datetime import datetime

# Desactivar advertencias innecesarias que ensucian el log de GitHub Actions
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# --- GESTIÓN DE RUTAS ---
# Usamos una ruta absoluta simple basada en la ubicación de este archivo
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subimos un nivel para llegar a 'src'
src_path = os.path.abspath(os.path.join(current_dir, ".."))

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importación única y directa
# Al haber instalado el paquete con 'pip install -e .' en el workflow, 
# esta ruta siempre será válida.
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    """Ejecución principal del Gatekeeper"""
    
    # Datos de contexto para el inicio de la operación
    inputs = {
        'current_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'terminal_location': 'Terminal Sur - Surquillo'
    }
    
    print(f"\n--- [SISTEMA INICIADO] - {inputs['current_date']} ---")
    print(f"Ubicación: {inputs['terminal_location']}")
    print(f"Motor: Gemini 3.1 Pro Preview\n")

    try:
        # Instanciamos la Crew y ejecutamos
        # Usamos kickoff() directamente sobre la instancia de la crew
        gatekeeper_crew = FuelTerminalSecurityLogisticsGatekeeperCrew().crew()
        result = gatekeeper_crew.kickoff(inputs=inputs)
        
        print("\n--- [OPERACIÓN FINALIZADA CON ÉXITO] ---")
        return result

    except Exception as e:
        # El error de Pydantic suele ser capturado aquí
        print(f"\n--- [ERROR CRÍTICO DURANTE LA EJECUCIÓN]:\n{e}\n---")
        sys.exit(1)

if __name__ == "__main__":
    run()