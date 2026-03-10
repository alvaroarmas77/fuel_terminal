from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_google_genai import ChatGoogleGenerativeAI
import os

from fuel_terminal_security_logistics_gatekeeper.tools.AccessControlTool import AccessControlTool
from fuel_terminal_security_logistics_gatekeeper.tools.VehicleRegistryTool import VehicleRegistryTool
from fuel_terminal_security_logistics_gatekeeper.tools.OutlookCalendarTool import OutlookCalendarTool
from fuel_terminal_security_logistics_gatekeeper.tools.OrderManagementTool import OrderManagementTool

@CrewBase
class FuelTerminalSecurityLogisticsGatekeeperCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", # Actualizado a la versión estable más reciente
            verbose=True,
            temperature=0.1, # Menos temperatura para mayor rigor en seguridad
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    @agent
    def security_authentication_specialist(self) -> Agent:
        # FASE 1: Usa VehicleRegistryTool para validar dispatcher_email
        return Agent(
            config=self.agents_config['security_authentication_specialist'],
            tools=[VehicleRegistryTool()], 
            llm=self.gemini_llm,
            verbose=True
        )

    @agent
    def registry_validation_specialist(self) -> Agent:
        # FASE 2: Usa VehicleRegistryTool para validar truck_plate y driver_name
        return Agent(
            config=self.agents_config['registry_validation_specialist'],
            tools=[VehicleRegistryTool()],
            llm=self.gemini_llm,
            verbose=True
        )

    @agent
    def access_control_specialist(self) -> Agent:
        # FASE 3: Usa AccessControlTool para SCTR y Bloqueos
        return Agent(
            config=self.agents_config['access_control_specialist'],
            tools=[AccessControlTool()],
            llm=self.gemini_llm,
            verbose=True
        )

    @agent
    def order_logging_specialist(self) -> Agent:
        # FASE 4: Registro físico en Excel
        return Agent(
            config=self.agents_config['order_logging_specialist'],
            tools=[OrderManagementTool()],
            llm=self.gemini_llm,
            verbose=True
        )

    @task
    def phase_1___user_authentication(self) -> Task:
        return Task(config=self.tasks_config['phase_1___user_authentication'], agent=self.security_authentication_specialist())

    @task
    def phase_2___registry_validation(self) -> Task:
        return Task(config=self.tasks_config['phase_2___registry_validation'], agent=self.registry_validation_specialist())

    @task
    def phase_3___access_control(self) -> Task:
        return Task(config=self.tasks_config['phase_3___access_control'], agent=self.access_control_specialist())

    @task
    def phase_4___order_logging(self) -> Task:
        return Task(config=self.tasks_config['phase_4___order_logging'], agent=self.order_logging_specialist())

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential, # Mantenemos secuencial para el flujo de seguridad
            verbose=True
        )