#!/usr/bin/env python
import os
import sys
import shutil
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 1. FUNCIÓN DE LIMPIEZA DE CACHÉ
def clean_cache():
    """Elimina archivos .pyc y carpetas __pycache__ para evitar errores de versiones viejas."""
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

from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

def run():
    print("DEBUG: Iniciando Gatekeeper System...")
    ahora = datetime.now()
    
    # Configuración de argumentos para GitHub Actions
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", help="Email del despachador")
    parser.add_argument("--plate", help="Placa del camión")
    parser.add_argument("--name", help="Nombre del conductor", default="Conductor Registrado")
    parser.add_argument("--volume", help="Volumen de combustible", default="5000")
    parser.add_argument("--model", default="gemini/gemini-3.1-pro-preview")
    args = parser.parse_args()

    # --- LÓGICA HÍBRIDA (CONSOLA O ARGUMENTOS) ---
    if args.email and args.plate:
        # Si viene de GitHub Actions
        d_email = args.email
        t_plate = args.plate
        d_name  = args.name
        f_vol   = args.volume
        print(f"MODO AUTOMÁTICO: Procesando {t_plate} para {d_email}")
    else:
        # Modo Manual en PC (Consola)
        print("\n--- CONFIGURACIÓN MANUAL DE SOLICITUD ---")
        d_email = input("Email del Despachador [cliente_prueba@empresa.com]: ") or 'cliente_prueba@empresa.com'
        t_plate = input("Placa del Camión [ABC-1234]: ") or 'ABC-1234'
        d_name  = input("Nombre del Conductor [Juan Perez]: ") or 'Juan Perez'
        f_vol   = input("Volumen de Combustible [5000]: ") or '5000'

    # 3. INPUTS (DINÁMICOS) - Se eliminó el bloque repetido que causaba el SyntaxError
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
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"ERROR DURANTE LA EJECUCIÓN: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_cache()
    run()