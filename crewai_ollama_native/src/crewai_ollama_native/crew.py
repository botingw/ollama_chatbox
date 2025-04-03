from crewai import Agent, Crew, Process, Task
# from crewai.decorators import agent, task, crew
# from crewai.project import CrewBase, agent, crew, task
from crewai.project import CrewBase, agent, crew, task

# from .config.agents_ollama import agents # llm use ollama package
# from .config.agents_langchain_wrapper import agents # llm use langchain wrapper
# from .config.tasks import tasks

from langchain.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
import os

google_api_key = os.getenv("GOOGLE_API_KEY")
google_llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-pro-exp-03-25",
    verbose=True,
    temperature=0.6, # Controls creativity (0.0 = deterministic, 1.0 = max creativity)
    google_api_key=google_api_key
)

@CrewBase
class ResearchCrew:
    """Research crew for analyzing topics and creating content"""
    print("ResearchCrew init")
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    # note: for ollama, seems need add ollama/ in front of the model name
    # ollama_llm = Ollama(model="ollama/smollm2:135m", base_url="http://localhost:11434")
    print("ResearchCrew init")
    
    @agent
    def research_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            llm=self.google_llm,
            allow_delegation=False,
            verbose=True
        )
    
    @agent
    def content_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            llm=self.google_llm,
            allow_delegation=False,
            verbose=True
        )
    
    @task
    def conduct_research(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.research_analyst_agent() 
        )
    
    @task
    def write_content(self) -> Task:
        return Task(
            config=self.tasks_config['summary_task'],
            agent=self.content_writer_agent(),
            context=[self.conduct_research()] # get context from previous task
        )
    
    @crew
    def crew(self) -> Crew:
        print("return crew")
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

