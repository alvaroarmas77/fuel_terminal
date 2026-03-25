#!/usr/bin/env python
import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Configuración de rutas
current_file_path = Path(__file__).resolve()
root_path = current_file_path.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

# 1. FUNCIÓN DE LIMPIEZA DE CACHÉ
def clean_cache():
    """Elimina archivos .pyc y carpetas __pycache__."""
    print("DEBUG: Limpiando caché de Python (__pycache__)...")
    for root, dirs, files in os.walk('.', topdown=False):
        for name in files:
            if name.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, name))
                except:
                    pass
        for name in dirs:
            if name == '__pycache__':
                try:
                    shutil.rmtree(os.path.join(root, name))
                except:
                    pass

# 2. CONFIGURACIÓN DE ENTORNO
load_dotenv()
os.environ["OTEL_SDK_DISABLED"] = "true"

def run():
    print("DEBUG: Iniciando Gatekeeper System...")
    ahora = datetime.now()
    
    # Configuración de argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", help="Email del despachador")
    parser.add_argument("--plate", help="Placa del camión")
    parser.add_argument("--name", help="Nombre del conductor")
    parser.add_argument("--volume", help="Volumen de combustible")
    parser.add_argument("--model", default="gemini/gemini-3.1-pro-preview")
    args = parser.parse_args()

    # --- LÓGICA DE CAPTURA DE DATOS ---
    # Prioridad 1: Argumentos (GitHub Actions)
    # Prioridad 2: Inputs manuales (Solo si no hay argumentos Y hay una terminal activa)
    
    if args.email and args.plate:
        d_email = args.email
        t_plate = args.plate
        d_name  = args.name or "Conductor Registrado"
        f_vol   = args.volume or "5000"
        print(f"MODO AUTOMÁTICO: Procesando {t_plate} para {d_email}")
    else:
        # Si no hay argumentos y NO hay terminal (como en GitHub), fallar explícitamente
        if not sys.stdin.isatty():
            print("ERROR: No se proporcionaron argumentos y no hay terminal interactiva.")
            sys.exit(1)
            
        print("\n--- CONFIGURACIÓN MANUAL DE SOLICITUD ---")
        d_email = input("Email del Despachador [cliente_prueba@empresa.com]: ") or 'cliente_prueba@empresa.com'
        t_plate = input("Placa del Camión [ABC-1234]: ") or 'ABC-1234'
        d_name  = input("Nombre del Conductor [Juan Perez]: ") or 'Juan Perez'
        f_vol   = input("Volumen de Combustible [5000]: ") or '5000'

    # 3. CONSTRUCCIÓN DE INPUTS PARA EL AGENTE
    inputs = {
        'dispatcher_email': d_email,
        'driver_email': d_email,
        'driver_name': d_name,
        'truck_plate': t_plate,
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:00:00'), 
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        'fuel_volume': f_vol,
        'order_id': f"ORD-{ahora.strftime('%y%m%d-%H%M')}"
    }

    try:
        # Ejecución del agente
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"ERROR DURANTE LA EJECUCIÓN: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_cache()
    run()