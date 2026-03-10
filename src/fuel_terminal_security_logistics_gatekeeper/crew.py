from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importación de las herramientas simplificadas (sin args_schema)
from fuel_terminal_security_logistics_gatekeeper.tools.AccessControlTool import AccessControlTool
from fuel_terminal_security_logistics_gatekeeper.tools.VehicleRegistryTool import VehicleRegistryTool
from fuel_terminal_security_logistics_gatekeeper.tools.OutlookCalendarTool import OutlookCalendarTool
from fuel_terminal_security_logistics_gatekeeper.tools.OrderManagementTool import OrderManagementTool

@CrewBase
class FuelTerminalSecurityLogisticsGatekeeperCrew():
    """FuelTerminalSecurityLogisticsGatekeeper crew - Versión Estabilizada"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        # Motor solicitado por defecto
        self.gemini_llm = "gemini/gemini-3.1-pro-preview"

    @agent
    def security_authentication_specialist(self) -> Agent:
        conf = self.agents_config['security_authentication_specialist']
        return Agent(
            role=conf['role'],
            goal=conf['goal'],
            backstory=conf['backstory'],
            tools=[AccessControlTool()], # Instancia limpia
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def registry_validation_specialist(self) -> Agent:
        conf = self.agents_config['registry_validation_specialist']
        return Agent(
            role=conf['role'],
            goal=conf['goal'],
            backstory=conf['backstory'],
            tools=[VehicleRegistryTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def intelligent_scheduling_coordinator(self) -> Agent:
        conf = self.agents_config['intelligent_scheduling_coordinator']
        return Agent(
            role=conf['role'],
            goal=conf['goal'],
            backstory=conf['backstory'],
            tools=[OutlookCalendarTool()],
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def order_logging_specialist(self) -> Agent:
        conf = self.agents_config['order_logging_specialist']
        return Agent(
            role=conf['role'],
            goal=conf['goal'],
            backstory=conf['backstory'],
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
        """Crea la Crew final con proceso secuencial"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )