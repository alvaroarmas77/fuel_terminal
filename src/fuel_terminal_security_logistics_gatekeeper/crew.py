import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importación robusta de herramientas
# Asegúrate de que todas tus clases en /tools/ hereden de 'from crewai_tools import BaseTool'
try:
    from fuel_terminal_security_logistics_gatekeeper.tools.AccessControlTool import AccessControlTool
    from fuel_terminal_security_logistics_gatekeeper.tools.VehicleRegistryTool import VehicleRegistryTool
    from fuel_terminal_security_logistics_gatekeeper.tools.OutlookCalendarTool import OutlookCalendarTool
    from fuel_terminal_security_logistics_gatekeeper.tools.OrderManagementTool import OrderManagementTool
except ImportError:
    from tools.AccessControlTool import AccessControlTool
    from tools.VehicleRegistryTool import VehicleRegistryTool
    from tools.OutlookCalendarTool import OutlookCalendarTool
    from tools.OrderManagementTool import OrderManagementTool

@CrewBase
class FuelTerminalSecurityLogisticsGatekeeperCrew():
    """Lógica completa para el Gatekeeper de la Terminal de Combustible"""

    # Rutas automáticas a los archivos YAML dentro de la carpeta config/
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        # Configuración del modelo Gemini 3.1 Pro Preview
        # Se pasa como string para evitar errores de importación de la clase LLM
        self.gemini_llm = "gemini/gemini-3.1-pro-preview"

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
            tools=[], # Este agente redacta basándose en la salida de los anteriores
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    # --- DEFINICIÓN DE TAREAS ---

    @task
    def phase_1___user_authentication(self) -> Task:
        return Task(config=self.tasks_config['phase_1___user_authentication'])

    @task
    def phase_2___registry_validation(self) -> Task:
        return Task(config=self.tasks_config['phase_2___registry_validation'])

    @task
    def phase_3___intelligent_scheduling(self) -> Task:
        return Task(config=self.tasks_config['phase_3___intelligent_scheduling'])

    @task
    def phase_4___order_logging(self) -> Task:
        return Task(config=self.tasks_config['phase_4___order_logging'])

    @task
    def phase_5___multi_channel_communications(self) -> Task:
        return Task(config=self.tasks_config['phase_5___multi_channel_communications'])

    # --- ENSAMBLAJE ---

    @crew
    def crew(self) -> Crew:
        """Organiza la ejecución secuencial de los 5 especialistas"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )