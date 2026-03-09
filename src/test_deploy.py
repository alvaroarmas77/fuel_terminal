import sys
import os

print("--- [INICIANDO DIAGNÓSTICO DE DESPLIEGUE] ---")

# 1. Verificar Directorio y Path
print(f"Directorio actual: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'No definido')}")

# 2. Intentar importar CrewAI y Tools
try:
    import crewai
    import crewai_tools
    from crewai_tools import BaseTool
    print("✅ CrewAI y CrewAI-Tools: Cargados correctamente")
except ImportError as e:
    print(f"❌ Error de librerías: {e}")
    sys.exit(1)

# 3. Verificar acceso a los archivos del proyecto
try:
    # Intentamos una importación relativa al PYTHONPATH configurado
    from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
    print("✅ Módulos del proyecto: Localizados y cargados")
except Exception as e:
    print(f"❌ Error de rutas del proyecto o código: {e}")
    sys.exit(1)

print("--- [DIAGNÓSTICO COMPLETADO EXITOSAMENTE] ---")