import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importaciones absolutas para evitar ambigüedad en el entorno del Runner
from fuel_terminal_security_logistics_gatekeeper.tools.AccessControlTool import AccessControlTool
from fuel_terminal_security_logistics_gatekeeper.tools.VehicleRegistryTool import VehicleRegistryTool
from fuel_terminal_security_logistics_gatekeeper.tools.OutlookCalendarTool import OutlookCalendarTool
from fuel_terminal_security_logistics_gatekeeper.tools.OrderManagementTool import OrderManagementTool

@CrewBase
class FuelTerminalSecurityLogisticsGatekeeperCrew():
    """Lógica completa para el Gatekeeper de la Terminal de Combustible"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        self.gemini_llm = "gemini/gemini-3.1-pro-preview"

    # --- AGENTES ---
    @agent
    def security_authentication_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['security_authentication_specialist'],
            tools=[AccessControlTool()], # Instancia aquí
            llm=self.gemini_llm,
            verbose=True
        )

    @agent
    def registry_validation_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['registry_validation_specialist'],
            tools=[VehicleRegistryTool()],
            llm=self.gemini_llm,
            verbose=True
        )

    @agent
    def intelligent_scheduling_coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config['intelligent_scheduling_coordinator'],
            tools=[OutlookCalendarTool()],
            llm=self.gemini_llm,
            verbose=True
        )

    @agent
    def order_logging_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['order_logging_specialist'],
            tools=[OrderManagementTool()],
            llm=self.gemini_llm,
            verbose=True
        )

    @agent
    def multi_channel_communications_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['multi_channel_communications_manager'],
            tools=[], 
            llm=self.gemini_llm,
            verbose=True
        )

    # --- TAREAS (Sin paréntesis en el agente) ---
    @task
    def phase_1___user_authentication(self) -> Task:
        return Task(
            config=self.tasks_config['phase_1___user_authentication'],
            agent=self.security_authentication_specialist # SIN PARENTESIS
        )

    @task
    def phase_2___registry_validation(self) -> Task:
        return Task(
            config=self.tasks_config['phase_2___registry_validation'],
            agent=self.registry_validation_specialist # SIN PARENTESIS
        )

    @task
    def phase_3___intelligent_scheduling(self) -> Task:
        return Task(
            config=self.tasks_config['phase_3___intelligent_scheduling'],
            agent=self.intelligent_scheduling_coordinator # SIN PARENTESIS
        )

    @task
    def phase_4___order_logging(self) -> Task:
        return Task(
            config=self.tasks_config['phase_4___order_logging'],
            agent=self.order_logging_specialist # SIN PARENTESIS
        )

    @task
    def phase_5___multi_channel_communications(self) -> Task:
        return Task(
            config=self.tasks_config['phase_5___multi_channel_communications'],
            agent=self.multi_channel_communications_manager # SIN PARENTESIS
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )