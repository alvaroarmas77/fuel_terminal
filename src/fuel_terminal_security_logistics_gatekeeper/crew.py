from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_google_genai import ChatGoogleGenerativeAI
import os

from fuel_terminal_security_logistics_gatekeeper.tools.AccessControlTool import AccessControlTool
from fuel_terminal_security_logistics_gatekeeper.tools.VehicleRegistryTool import VehicleRegistryTool
from fuel_terminal_security_logistics_gatekeeper.tools.OutlookCalendarTool import OutlookCalendarTool
from fuel_terminal_security_logistics_gatekeeper.tools.OrderManagementTool import OrderManagementTool
from fuel_terminal_security_logistics_gatekeeper.tools.CommunicationsTool import CommunicationsTool

@CrewBase
class FuelTerminalSecurityLogisticsGatekeeperCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-pro-preview",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    @agent
    def security_authentication_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['security_authentication_specialist'], 
            tools=[VehicleRegistryTool()], 
            llm=self.gemini_llm, verbose=True)

    @agent
    def registry_validation_specialist(self) -> Agent:
        return Agent(config=self.agents_config['registry_validation_specialist'], tools=[VehicleRegistryTool(), AccessControlTool()], llm=self.gemini_llm, verbose=True)

    @agent
    def intelligent_scheduling_coordinator(self) -> Agent:
        return Agent(config=self.agents_config['intelligent_scheduling_coordinator'], tools=[OutlookCalendarTool()], llm=self.gemini_llm, verbose=True)

    @agent
    def order_logging_specialist(self) -> Agent:
        return Agent(config=self.agents_config['order_logging_specialist'], tools=[OrderManagementTool()], llm=self.gemini_llm, verbose=True)

    @agent
    def multi_channel_communications_manager(self) -> Agent:
        return Agent(
            
            config=self.agents_config['multi_channel_communications_manager'],
        tools=[CommunicationsTool()], # <--- ASIGNAR LA HERRAMIENTA AQUÍ
        verbose=True,
        llm=self.gemini_llm
        )
    

    @task
    def phase_1___user_authentication(self) -> Task:
        return Task(config=self.tasks_config['phase_1___user_authentication'], agent=self.security_authentication_specialist())

    @task
    def phase_2___registry_validation(self) -> Task:
        return Task(config=self.tasks_config['phase_2___registry_validation'], agent=self.registry_validation_specialist())

    @task
    def phase_3___access_control(self) -> Task:
        return Task(config=self.tasks_config['phase_3___access_control'], agent=self.intelligent_scheduling_coordinator())

    @task
    def phase_4___order_logging(self) -> Task:
        return Task(config=self.tasks_config['phase_4___order_logging'], agent=self.order_logging_specialist())

    @task
    def phase_5___multi_channel_communications(self) -> Task:
        return Task(config=self.tasks_config['phase_5___multi_channel_communications'], agent=self.multi_channel_communications_manager())

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)