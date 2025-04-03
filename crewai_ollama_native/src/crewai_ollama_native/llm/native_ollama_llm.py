# from crewai.llm.base_llm import BaseLLM
from crewai import BaseLLM # problem:     from crewai import BaseLLM
# ImportError: cannot import name 'BaseLLM' from 'crewai' (/Users/wangbo-ting/miniconda3/envs/ollama_chatbox_4/lib/python3.8/site-packages/crewai/__init__.py)
# it means crewai doesn't expose BaseLLM at top level yet (also not expose as crewai.llm.BaseLLM    )

import ollama

class NativeOllamaLLM(BaseLLM):
    def __init__(self, model='smollm2', system_prompt='You are a helpful assistant.'):
        self.model = model
        self.system_prompt = system_prompt

    def __call__(self, prompt: str, **kwargs) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        response = ollama.chat(model=self.model, messages=messages)
        return response['message']['content']
