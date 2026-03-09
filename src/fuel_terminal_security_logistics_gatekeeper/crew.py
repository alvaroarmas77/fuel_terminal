import os
from datetime import datetime
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importación de herramientas
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
    """FuelTerminalSecurityLogisticsGatekeeper crew"""

    # Definimos el modelo como un string directo (Gemini 3.1 Pro Preview)
    # Esto evita el error de importación de la clase LLM
    llm_terminal = "gemini/gemini-3.1-pro-preview"

    @agent
    def security_authentication_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['security_authentication_specialist'],
            llm=self.llm_terminal,
            tools=[AccessControlTool()],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def registry_validation_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['registry_validation_specialist'],
            llm=self.llm_terminal,
            tools=[VehicleRegistryTool()],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def intelligent_scheduling_coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config['intelligent_scheduling_coordinator'],
            llm=self.llm_terminal,
            tools=[OutlookCalendarTool()],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def order_logging_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['order_logging_specialist'],
            llm=self.llm_terminal,
            tools=[OrderManagementTool()],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def multi_channel_communications_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['multi_channel_communications_manager'],
            llm=self.llm_terminal,
            verbose=True,
            allow_delegation=False
        )

    # --- TAREAS ---
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

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )