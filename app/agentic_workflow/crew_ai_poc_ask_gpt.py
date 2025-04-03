import requests
# from crewai.tools import BaseTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.agents import BaseAgent       # From crewAI (see: https://github.com/crewAIInc/crewAI)
from crewai.tasks import Task               # A simple task abstraction
from crewai.llm import LLMBase              # Base class for LLM integrations from crewAI-tools

# Custom LLM adapter that wraps Ollama's REST API
class OllamaLLM(LLMBase):
    def __init__(self, base_url="http://localhost:11434", model="llama3.2"):
        super().__init__()
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 100) -> str:
        """
        Calls the Ollama REST API to generate a response for a given prompt.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,  # You can later add support for streaming if needed
            "options": {"max_tokens": max_tokens}
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        # Expecting the generated text to be in the "text" field
        return result.get("text", "")

# Custom agent using CrewAI that leverages our OllamaLLM adapter
class OllamaAgent(BaseAgent):
    def __init__(self, name: str, llm: OllamaLLM):
        super().__init__(name=name)
        self.llm = llm

    def execute(self, task: Task) -> str:
        """
        Processes a task by sending its prompt to the LLM and logging the result.
        """
        prompt = task.data.get("prompt", "")
        self.logger.info(f"[{self.name}] Received task with prompt: {prompt}")
        response = self.llm.generate(prompt)
        self.logger.info(f"[{self.name}] Generated response: {response}")
        return response

# --- Example CrewAI Workflow ---
if __name__ == "__main__":
    # Instantiate the custom Ollama LLM adapter
    ollama_llm = OllamaLLM(base_url="http://localhost:11434", model="llama3.2")

    # Create an agent using CrewAI's BaseAgent subclass
    agent = OllamaAgent(name="OllamaAgent", llm=ollama_llm)

    # Create a sample task – in a real workflow, tasks could be part of a larger Crew (see https://docs.crewai.com/examples/example)
    sample_task = Task(data={"prompt": "Write a haiku about technology and nature."})

    # Execute the task via the agent
    result = agent.execute(sample_task)
    print("Agent response:", result)
