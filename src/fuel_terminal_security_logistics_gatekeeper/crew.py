import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task






@CrewBase
class FuelTerminalSecurityLogisticsGatekeeperCrew:
    """FuelTerminalSecurityLogisticsGatekeeper crew"""

    
    @agent
    def security_authentication_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["security_authentication_specialist"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    
    @agent
    def registry_validation_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["registry_validation_specialist"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    
    @agent
    def intelligent_scheduling_coordinator(self) -> Agent:
        
        return Agent(
            config=self.agents_config["intelligent_scheduling_coordinator"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    
    @agent
    def order_logging_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["order_logging_specialist"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    
    @agent
    def multi_channel_communications_manager(self) -> Agent:
        
        return Agent(
            config=self.agents_config["multi_channel_communications_manager"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                
            ),
            
        )
    

    
    @task
    def phase_1___user_authentication(self) -> Task:
        return Task(
            config=self.tasks_config["phase_1___user_authentication"],
            markdown=False,
            
            
        )
    
    @task
    def phase_2___registry_validation(self) -> Task:
        return Task(
            config=self.tasks_config["phase_2___registry_validation"],
            markdown=False,
            
            
        )
    
    @task
    def phase_3___intelligent_scheduling(self) -> Task:
        return Task(
            config=self.tasks_config["phase_3___intelligent_scheduling"],
            markdown=False,
            
            
        )
    
    @task
    def phase_4___order_logging(self) -> Task:
        return Task(
            config=self.tasks_config["phase_4___order_logging"],
            markdown=False,
            
            
        )
    
    @task
    def excel_order_database_management(self) -> Task:
        return Task(
            config=self.tasks_config["excel_order_database_management"],
            markdown=False,
            
            
        )
    
    @task
    def phase_5___multi_channel_communications(self) -> Task:
        return Task(
            config=self.tasks_config["phase_5___multi_channel_communications"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the FuelTerminalSecurityLogisticsGatekeeper crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            chat_llm=LLM(model="openai/gpt-4o-mini"),
        )


