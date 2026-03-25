#!/usr/bin/env python
import os
import sys
import shutil
import argparse
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Configuración de rutas para asegurar importación correcta del paquete
current_file_path = Path(__file__).resolve()
root_path = current_file_path.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from fuel_terminal_security_logistics_gatekeeper.crew import FuelTerminalSecurityLogisticsGatekeeperCrew

# 1. FUNCIÓN DE LIMPIEZA DE CACHÉ Y ARCHIVOS TEMPORALES
def clean_cache():
    """Elimina archivos .pyc y carpetas __pycache__ de forma recursiva."""
    print("DEBUG: Limpiando caché de Python y archivos temporales...")
    for root, dirs, files in os.walk('.', topdown=False):
        for name in files:
            if name.endswith('.pyc') or name.endswith('.pyo'):
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
os.environ["OTEL_SDK_DISABLED"] = "true" # Deshabilitar telemetría para evitar logs innecesarios

def run():
    print("DEBUG: Iniciando Gatekeeper System - Versión de Resiliencia 2.0...")
    ahora = datetime.now()
    
    # Configuración de argumentos para integración con GitHub Actions
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", help="Email del despachador que solicita el acceso")
    parser.add_argument("--plate", help="Placa del vehículo para validar en el registro")
    parser.add_argument("--name", help="Nombre completo del conductor del vehículo")
    parser.add_argument("--volume", help="Volumen de combustible en galones")
    parser.add_argument("--model", default="gemini/gemini-3.1-pro-preview")
    args = parser.parse_args()

    # --- LÓGICA DE CAPTURA DE DATOS ---
    # Prioridad 1: Argumentos de línea de comandos (Uso en CI/CD o Scripts)
    # Prioridad 2: Inputs manuales (Solo si hay terminal interactiva activa)
    
    if args.email and args.plate:
        d_email = args.email
        t_plate = args.plate
        d_name  = args.name or "Conductor Registrado"
        f_vol   = args.volume or "5000"
        print(f"MODO AUTOMÁTICO: Procesando solicitud para placa {t_plate} por {d_email}")
    else:
        # Si no hay argumentos y NO hay terminal (como en GitHub Actions), fallar explícitamente
        if not sys.stdin.isatty():
            print("ERROR: Faltan argumentos requeridos (--email, --plate) y no se detectó terminal interactiva.")
            sys.exit(1)
            
        print("\n--- CONFIGURACIÓN MANUAL DE SOLICITUD DE ACCESO ---")
        d_email = input("Email del Despachador [cliente_prueba@empresa.com]: ") or 'cliente_prueba@empresa.com'
        t_plate = input("Placa del Camión [ABC-1234]: ") or 'ABC-1234'
        d_name  = input("Nombre del Conductor [Juan Perez]: ") or 'Juan Perez'
        f_vol   = input("Volumen de Combustible [5000]: ") or '5000'

    # 3. CONSTRUCCIÓN DE INPUTS PARA EL FLUJO DE AGENTES (CREW)
    inputs = {
        'dispatcher_email': d_email,
        'driver_email': d_email, # Fallback inicial, será sobreescrito en Fase 2
        'driver_name': d_name,
        'truck_plate': t_plate.upper(),
        'requested_datetime': ahora.strftime('%Y-%m-%dT%H:00:00'), 
        'current_date': ahora.strftime('%Y-%m-%d'),
        'location': 'Terminal Sur - Surquillo',
        'fuel_volume': f_vol,
        'order_id': f"ORD-{ahora.strftime('%y%m%d-%H%M')}"
    }

    try:
        # Ejecución del sistema multi-agente
        print(f"DEBUG: Generando Orden ID: {inputs['order_id']}")
        FuelTerminalSecurityLogisticsGatekeeperCrew().crew().kickoff(inputs=inputs)
        print("DEBUG: Ejecución finalizada exitosamente.")
    except Exception as e:
        print(f"ERROR CRÍTICO DURANTE LA EJECUCIÓN DEL CREW: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    clean_cache()
    run()