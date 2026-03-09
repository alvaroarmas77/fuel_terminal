import sys
import os

print("--- [INICIANDO DIAGNÓSTICO DE DESPLIEGUE] ---")

# 1. Verificar Rutas
print(f"Directorio actual: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'No definido')}")

# 2. Intentar importar CrewAI
try:
    import crewai
    import crewai_tools
    print(f"✅ CrewAI instalado (Versión: {crewai.__version__})")
    print(f"✅ CrewAI Tools instalado")
except ImportError as e:
    print(f"❌ Error de librerías: {e}")

# 3. Verificar acceso a los archivos del proyecto
try:
    from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew
    print("✅ Módulos del proyecto: Localizados y cargados")
except ImportError as e:
    print(f"❌ Error de rutas del proyecto: {e}")

# 4. Verificar BaseTool (El error que tuvimos antes)
try:
    from crewai_tools import BaseTool
    print("✅ BaseTool: Importación correcta")
except ImportError:
    print("❌ BaseTool: No se pudo importar desde crewai_tools")

print("--- [FIN DEL DIAGNÓSTICO] ---")