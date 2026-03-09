import os
from datetime import datetime
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# Importación de herramientas con nombres de archivo exactos (Case-Sensitive)
try:
    from fuel_terminal_security_logistics_gatekeeper.tools.AccessControlTool import AccessControlTool
    from fuel_terminal_security_logistics_gatekeeper.tools.VehicleRegistryTool import VehicleRegistryTool
    from fuel_terminal_security_logistics_gatekeeper.tools.OutlookCalendarTool import OutlookCalendarTool
    from fuel_terminal_security_logistics_gatekeeper.tools.OrderManagementTool import OrderManagementTool
except ImportError:
    # Fallback para ejecución local
    from tools.AccessControlTool import AccessControlTool
    from tools.VehicleRegistryTool import VehicleRegistryTool
    from tools.OutlookCalendarTool import OutlookCalendarTool
    from tools.OrderManagementTool import OrderManagementTool

@CrewBase
class FuelTerminalSecurityLogisticsGatekeeperCrew():
    """Tripulación para la Gestión de Seguridad y Logística de la Terminal de Combustible"""

    # Las rutas a los archivos de configuración se asumen en la carpeta 'config/' 
    # relativa a este archivo, gracias al decorador @CrewBase.
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        # Configuración del Modelo de Lenguaje (LLM)
        self.gemini_llm = LLM(
            model="gemini/gemini-3.1-pro-preview",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.2,
            verbose=True
        )

    # --- DEFINICIÓN DE AGENTES ---

    @agent
    def security_authentication_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['security_authentication_specialist'],
            tools=[AccessControlTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def registry_validation_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['registry_validation_specialist'],
            tools=[VehicleRegistryTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def intelligent_scheduling_coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config['intelligent_scheduling_coordinator'],
            tools=[OutlookCalendarTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def order_logging_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['order_logging_specialist'],
            tools=[OrderManagementTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def multi_channel_communications_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['multi_channel_communications_manager'],
            tools=[], # Este agente usa sus habilidades nativas de redacción
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    # --- DEFINICIÓN DE TAREAS ---

    @task
    def phase_1___user_authentication(self) -> Task:
        return Task(
            config=self.tasks_config['phase_1___user_authentication']
        )

    @task
    def phase_2___registry_validation(self) -> Task:
        return Task(
            config=self.tasks_config['phase_2___registry_validation']
        )

    @task
    def phase_3___intelligent_scheduling(self) -> Task:
        return Task(
            config=self.tasks_config['phase_3___intelligent_scheduling']
        )

    @task
    def phase_4___order_logging(self) -> Task:
        return Task(
            config=self.tasks_config['phase_4___order_logging']
        )

    @task
    def phase_5___multi_channel_communications(self) -> Task:
        return Task(
            config=self.tasks_config['phase_5___multi_channel_communications']
        )

    # --- ENSAMBLAJE DE LA TRIPULACIÓN ---

    @crew
    def crew(self) -> Crew:
        """Crea y organiza la tripulación siguiendo un proceso secuencial"""
        return Crew(
            agents=self.agents, # CrewAI detecta automáticamente los agentes decorados con @agent
            tasks=self.tasks,   # CrewAI detecta automáticamente las tareas decoradas con @task
            process=Process.sequential,
            verbose=True
        )