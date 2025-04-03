import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from langchain_google_genai import ChatGoogleGenerativeAI

# --- LLM Configuration ---
# Retrieve the API key from environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")
print(f"google_api_key: {google_api_key}")

# if not google_api_key:
#     raise ValueError("GOOGLE_API_KEY not found in environment variables. "
#                      "Make sure to set it in the .env file.")

# Instantiate the Gemini model
# Common models: "gemini-pro", "gemini-1.0-pro", "gemini-1.5-flash-latest", "gemini-1.5-pro-latest"
# Check Google AI documentation for the latest available models.
# Note: llm provider in litellm package has bug, where model string always starts with model/, need hardcode replace it with gemini/
# also google_api_key is not passed to api_key in litellm request, also need hardcode it
google_llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-pro-exp-03-25",
    verbose=True,
    temperature=0.6, # Controls creativity (0.0 = deterministic, 1.0 = max creativity)
    google_api_key=google_api_key
)

@CrewBase
class GeminiResearchCrew:
    """Research crew using Gemini Pro for analysis and content creation"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def senior_researcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_researcher'],
            llm=google_llm,
            allow_delegation=False,
            verbose=True
        )
    
    @agent
    def senior_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_writer'],
            llm=google_llm,
            allow_delegation=False,
            verbose=True
        )
    
    @task
    def conduct_research(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.senior_researcher_agent()
        )
    
    @task
    def write_summary(self) -> Task:
        return Task(
            config=self.tasks_config['summary_task'],
            agent=self.senior_writer_agent(),
            context=[self.conduct_research()]
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

def run_gemini_research(topic: str) -> str:
    """
    Run research using Gemini Pro agents
    
    Args:
        topic (str): The research topic to analyze
        
    Returns:
        str: The research results
    """
    try:
        # Initialize the crew
        research_crew = GeminiResearchCrew()
        
        # Execute the research process
        result = research_crew.crew().kickoff(
            inputs={
                "topic": topic,
            }
        )
        
        return result
    except Exception as e:
        return f"An error occurred during research: {str(e)}"

if __name__ == "__main__":
    # Make sure GOOGLE_API_KEY is set in environment variables
    topic = "The future of quantum computing and its impact on cryptography"
    result = run_gemini_research(topic)
    print("\n=== Research Results ===")
    print(result)

# if __name__ == "__main__":
#     print("test_gemini_credential")
#     print(f"google_api_key: {google_api_key}")
#     print(f"llm: {llm}")
