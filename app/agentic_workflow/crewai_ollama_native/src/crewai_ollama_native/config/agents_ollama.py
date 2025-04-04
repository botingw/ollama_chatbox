import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import yaml
import os
from crewai import Agent
from importlib import import_module

# Load the YAML config
with open(os.path.join(os.path.dirname(__file__), 'agents.yaml'), 'r') as f:
    raw_agents = yaml.safe_load(f)

agents = {}
for name, config in raw_agents.items():
    llm_path = config.pop('llm', None)
    if llm_path:
        module_path, class_name = llm_path.rsplit('.', 1)
        mod = import_module(module_path)
        cls = getattr(mod, class_name)
        config['llm'] = cls()

    agents[name] = Agent(**config)
