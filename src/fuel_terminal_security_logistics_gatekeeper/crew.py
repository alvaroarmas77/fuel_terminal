from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from fuel_terminal_security_logistics_gatekeeper.tools.AccessControlTool import AccessControlTool
from fuel_terminal_security_logistics_gatekeeper.tools.VehicleRegistryTool import VehicleRegistryTool
from fuel_terminal_security_logistics_gatekeeper.tools.OutlookCalendarTool import OutlookCalendarTool
from fuel_terminal_security_logistics_gatekeeper.tools.OrderManagementTool import OrderManagementTool

@CrewBase
class FuelTerminalSecurityLogisticsGatekeeperCrew():
    """FuelTerminalSecurityLogisticsGatekeeper crew"""
    
    # Rutas a los archivos de configuración
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        # Motor solicitado: Gemini 3.1 Pro Preview
        self.gemini_llm = "gemini/gemini-3.1-pro-preview"

    @agent
    def security_authentication_specialist(self) -> Agent:
        # Extraemos la configuración manualmente para evitar el error de validación de dict a BaseModel
        config = self.agents_config['security_authentication_specialist']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[AccessControlTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def registry_validation_specialist(self) -> Agent:
        config = self.agents_config['registry_validation_specialist']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[VehicleRegistryTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def intelligent_scheduling_coordinator(self) -> Agent:
        config = self.agents_config['intelligent_scheduling_coordinator']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[OutlookCalendarTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def order_logging_specialist(self) -> Agent:
        config = self.agents_config['order_logging_specialist']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[OrderManagementTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @task
    def phase_1___user_authentication(self) -> Task:
        return Task(
            config=self.tasks_config['phase_1___user_authentication'],
            agent=self.security_authentication_specialist()
        )

    @task
    def phase_2___registry_validation(self) -> Task:
        return Task(
            config=self.tasks_config['phase_2___registry_validation'],
            agent=self.registry_validation_specialist()
        )

    @task
    def phase_3___intelligent_scheduling(self) -> Task:
        return Task(
            config=self.tasks_config['phase_3___intelligent_scheduling'],
            agent=self.intelligent_scheduling_coordinator()
        )

    @task
    def phase_4___order_logging(self) -> Task:
        return Task(
            config=self.tasks_config['phase_4___order_logging'],
            agent=self.order_logging_specialist()
        )

    @crew
    def crew(self) -> Crew:
        """Crea la Crew de logística de terminal"""
        return Crew(
            agents=self.agents, # Los agentes creados por los decoradores @agent
            tasks=self.tasks,   # Las tareas creadas por los decoradores @task
            process=Process.sequential,
            verbose=True
        )