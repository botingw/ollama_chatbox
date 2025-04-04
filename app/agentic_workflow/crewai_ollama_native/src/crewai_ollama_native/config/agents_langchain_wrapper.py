import os
import yaml
from crewai import Agent
# from crewai.llm import LLM

from langchain.llms import Ollama
# ollama_openhermes = Ollama(model="agent")


with open(os.path.join(os.path.dirname(__file__), "agents.yaml")) as f:
    raw_agents = yaml.safe_load(f)

agents = {}
for name, config in raw_agents.items():
    llm_data = config.pop("llm", None)
    if isinstance(llm_data, dict):
        provider = llm_data.get("provider")
        llm_config = llm_data.get("config", {})
        # config["llm"] = LLM(provider=provider, config=llm_config)
        ollama_openhermes = Ollama(model=llm_config.get("model"))
        config["llm"] = ollama_openhermes
    agents[name] = Agent(**config)

