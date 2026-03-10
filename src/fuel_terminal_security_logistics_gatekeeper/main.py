import sys
import os
import warnings
from datetime import datetime

# Desactivar advertencias de Pydantic v1/v2 para un log limpio
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# --- GESTIÓN DE RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, ".."))

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    """Ejecución principal del Gatekeeper con inputs completos"""
    
    # IMPORTANTE: Estos inputs deben coincidir con las variables {llave} en agents.yaml y tasks.yaml
    inputs = {
        'current_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'terminal_location': 'Terminal Sur - Surquillo',
        # Inputs dinámicos que los agentes necesitan para sus herramientas:
        'driver_id': 'D-9876', 
        'driver_name': 'Juan Perez',
        'truck_plate': 'ABC-1234',
        'requested_datetime': datetime.now().isoformat(),
        'fuel_volume': '5000 Gal'
    }
    
    print(f"\n--- [SISTEMA INICIADO] - {inputs['current_date']} ---")
    print(f"Ubicación: {inputs['terminal_location']}")
    print(f"Motor: Gemini 3.1 Pro Preview\n")

    try:
        # Instanciamos la clase de la Crew
        crew_instance = FuelTerminalSecurityLogisticsGatekeeperCrew()
        
        # Obtenemos el objeto Crew llamando al método .crew()
        gatekeeper_crew = crew_instance.crew()
        
        # Ejecutamos con los inputs validados
        result = gatekeeper_crew.kickoff(inputs=inputs)
        
        print("\n--- [OPERACIÓN FINALIZADA CON ÉXITO] ---")
        print(f"Resultado: {result}")
        return result

    except Exception as e:
        print(f"\n--- [ERROR CRÍTICO DURANTE LA EJECUCIÓN]:\n{str(e)}\n---")
        sys.exit(1)

if __name__ == "__main__":
    run()