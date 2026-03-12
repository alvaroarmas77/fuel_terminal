#!/usr/bin/env python
import os
import sys

# --- BLOQUE DE SEGURIDAD DE LIBRERÍAS ---
try:
    import O365
    import msal
    # Limpieza: se eliminó el '=' extra que causaba error de sintaxis
    print(f"DEBUG: Versión de O365 cargada: {getattr(O365, '__version__', 'Desconocida')}")
except ImportError:
    print("\n[!] ERROR CRÍTICO: Librerías no encontradas.")
    print("Por favor, asegúrate de que 'requirements.txt' contenga 'O365' (con O de Office) y no '0365'.")
    sys.exit(1)

from datetime import datetime
# Asegúrate de que esta ruta coincida con el nombre de tu paquete en el archivo pyproject.toml
from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    ahora = datetime.now()
    
    # --- CONFIGURACIÓN DE ENTRADAS (INPUTS) ---
    # Para órdenes con múltiples camiones, envía los datos como strings separados por comas.
    # La herramienta 'order_management_tool' ahora está preparada para separar estos valores 
    # y crear una fila independiente para cada uno manteniendo el mismo order_id.
    inputs = {
        # Identificadores de Personas (Fases 1, 2 y 5)
        'driver_id': 'D-9876, D-5432', # Ejemplo multi-unidad
        'driver_name': 'Juan Pérez, Ricardo Gómez', # Ejemplo multi-unidad
        'driver_email': 'juan.perez@transporte.com, ricardo.g@transporte.com',
        'dispatcher_email': 'logistics@terminal-sur.com',
        'sender_email': 'logistics@terminal-sur.com',
        
        # Identificadores de Vehículo (Fases 2 y 3)
        'plate_id': 'ABC-1234, XYZ-9876', # Ejemplo multi-unidad
        'truck_plate': 'ABC-1234, XYZ-9876', 
        
        # Datos de Tiempo y Ubicación (Fase 3)
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:00:00'), 
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        'terminal_location': 'Terminal Sur - Surquillo',
        
        # Datos de Orden (Fase 4)
        'fuel_volume': '5000, 3000', # Ejemplo multi-unidad
        'order_id': f"ORD-{ahora.strftime('%y%m%d%H%M')}",
        
        # Placeholders para la gestión dinámica de CrewAI
        'appointment_date': ahora.strftime('%Y-%m-%d'),
        'start_time': '', 
        'end_time': '',
        'assigned_island': ''
    }

    try:
        print(f"\n--- Iniciando Crew para la Orden Maestra: {inputs['order_id']} ---")
        
        # Instanciamos el Crew
        gatekeeper_crew = FuelTerminalSecurityLogisticsGatekeeperCrew().crew()
        
        # Ejecución del proceso secuencial blindado por los candados de seguridad
        result = gatekeeper_crew.kickoff(inputs=inputs)
        
        print(f"\n--- [RESULTADO FINAL DE LA OPERACIÓN] ---\n{result}")
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO EN EL FLUJO]: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()