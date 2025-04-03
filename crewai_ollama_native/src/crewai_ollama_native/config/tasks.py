import yaml
import os
from crewai import Task
from .agents_langchain_wrapper import agents

with open(os.path.join(os.path.dirname(__file__), 'tasks.yaml'), 'r') as f:
    raw_tasks = yaml.safe_load(f)

tasks = {}
for name, config in raw_tasks.items():
    agent_key = config.pop('agent')
    config['agent'] = agents[agent_key]
    tasks[name] = Task(**config)
