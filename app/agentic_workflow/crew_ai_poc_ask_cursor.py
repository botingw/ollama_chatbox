from crewai import Agent, Task, Crew, Process
import os
import ollama
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ollama client setup
def get_ollama_client():
    """Create and return an Ollama client using environment variables."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ollama.Client(host=base_url)

def create_research_agent(role, goal, backstory, model_name="smollm2:135m"):
    """Create a CrewAI agent with the specified parameters using Ollama."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        verbose=True,
        allow_delegation=False,
        llm_config={
            "config_list": [{
                "model": model_name,
                "api_base": base_url,
                "api_key": "ollama",  # Required by CrewAI but not used by Ollama
                "provider": "ollama"
            }],
            "temperature": 0.7,
            "max_tokens": 1000
        }
    )

def create_research_task(agent, description):
    """Create a task for an agent with the given description."""
    return Task(
        description=description,
        agent=agent,
        expected_output="Detailed and well-structured information",
        async_execution=False
    )

def run_research_crew(topic, model_name="smollm2:135m"):
    """Create and run a research crew with two agents."""
    try:
        logger.info(f"Creating research crew for topic: {topic} using model: {model_name}")
        
        # Create agents
        researcher = create_research_agent(
            role='Research Analyst',
            goal='Conduct thorough research on the given topic',
            backstory='Expert in gathering and analyzing information from various sources',
            model_name=model_name
        )
        logger.info(f"Researcher agent created: {researcher}")
        
        writer = create_research_agent(
            role='Content Writer',
            goal='Create well-structured content based on research',
            backstory='Experienced in writing clear and engaging content',
            model_name=model_name
        )
        logger.info(f"Writer agent created: {writer}")
        
        # Create tasks
        research_task = create_research_task(
            agent=researcher,
            description=f'Research the following topic thoroughly: {topic}. Focus on key points, trends, and important details.'
        )
        
        writing_task = create_research_task(
            agent=writer,
            description='Based on the research, create a comprehensive summary. Include main points, key findings, and recommendations.'
        )
        
        # Create crew with manager configuration
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, writing_task],
            verbose=True,
            process=Process.sequential,
            manager_llm_config={
                "config_list": [{
                    "model": model_name,
                    "api_base": base_url,
                    "api_key": "ollama",  # Required by CrewAI but not used by Ollama
                    "provider": "ollama"
                }],
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )
        
        # Run the crew
        result = crew.kickoff()
        logger.info("Research completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error in research crew: {str(e)}")
        return f"An error occurred during research: {str(e)}"

# Function to verify Ollama connectivity
def check_ollama_available(model_name="smollm2:135m"):
    """Check if Ollama is available and the specified model exists."""
    try:
        client = get_ollama_client()
        
        # Get list of models
        response = client.list()
        logger.info(f"Ollama response: {response}")
        
        # Check if models attribute exists
        if not hasattr(response, 'models'):
            logger.error(f"Unexpected response format from Ollama: {response}")
            return False, "Invalid response format from Ollama server"
            
        # Extract model names from the response
        model_names = [model.model for model in response.models]
        logger.info(f"Available models: {model_names}")
        
        # Check if the requested model exists
        if model_name not in model_names:
            logger.warning(f"Model {model_name} not found in Ollama. Available models: {model_names}")
            return False, f"Model {model_name} not found in Ollama. Available models: {model_names}"
        
        # Model exists, return success
        return True, "Ollama is available and model is working"
    
    except Exception as e:
        logger.error(f"Error connecting to Ollama: {str(e)}")
        return False, f"Error connecting to Ollama: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Verify Ollama is available
    available, message = check_ollama_available()
    if not available:
        print(f"Ollama is not available: {message}")
        exit(1)
    
    # Run a research task
    topic = "The impact of artificial intelligence on healthcare in 2024"
    result = run_research_crew(topic)
    print("\nFinal Result:")
    print(result) 