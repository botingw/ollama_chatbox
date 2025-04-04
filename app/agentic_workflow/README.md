
# Agentic Workflow Examples

This repository showcases various implementations of agent-based workflows using CrewAI with different LLM backends (Ollama and Google Gemini). It demonstrates how to create multi-agent systems that can perform complex tasks like research and content creation.

## Repository Structure

```
agentic_workflow/
├── crewai_ollama_native/
│   └── src/
│       └── crewai_ollama_native/
│           ├── config/
│           │   ├── agents.yaml
│           │   └── tasks.yaml
│           ├── crew.py
│           └── main.py
├── crew_ai_gemini/
│   └── src/
│       └── crew_ai_gemini/
│           ├── config/
│           │   ├── agents.yaml
│           │   └── tasks.yaml
│           └── crew_ai_poc_ask_gemini2_5_pro_decorator.py
│           └── crew_ai_poc_ask_gemini2_5_pro.py
├── experiments/
│   └── [various experimental implementations]
└── README.md
```

## Agent Example Implementations

### CrewAI with Ollama

The `crewai_ollama_native` example demonstrates:
- Integration with locally-hosted Ollama models
- A research workflow using a sequential agent process
- Configuration-driven agent and task setup via YAML
- Two different integration methods (direct API and LangChain wrapper)

Key features:
- Local model deployment with smaller open-source models
- No API costs
- Full control over the model infrastructure

### CrewAI with Google Gemini (Direct Integration)

The `crew_ai_gemini` example demonstrates:
- Direct integration with Google's Gemini 2.5 Pro model
- CrewAI's decorator pattern for agent and task definition
- YAML-based configuration for reusable agent and task definitions
- Research and content creation workflow

Key features:
- Higher reasoning capabilities using Gemini's sophisticated model
- Direct integration without additional wrappers
- Maintained consistent architecture with the Ollama example

### CrewAI with Google Gemini (Functional Pattern)
The crew_ai_gemini_functional example demonstrates:
- Integration with Google's Gemini model using a functional approach
- Non-decorator based implementation (traditional function-based approach)
- Direct agent and task creation without the @CrewBase pattern
- Alternative pattern for those who prefer functional programming styles

Key features:
- More traditional functional programming approach
- Potentially more straightforward for simple use cases
- Less abstraction than the decorator pattern
- Manual creation and configuration of agents and tasks

## How to Test the Examples

### Prerequisites
- Python 3.11+
- Ollama installed locally (for Ollama examples)
- Google API key (for Gemini examples)
- Required packages: `crewai`, `ollama`, `langchain`, `langchain_google_genai`

### Installation

1. Clone the repository:
```bash
git clone [repository URL]
cd agentic_workflow
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# For Gemini examples
export GOOGLE_API_KEY="your_google_api_key"

# For Ollama examples (if not using default URL)
export OLLAMA_BASE_URL="http://localhost:11434"
```

### Running the Ollama Example

1. Ensure Ollama is running locally and has the required models:
```bash
ollama pull smollm2:135m  # or your preferred model
```

2. Run the example:
```bash
cd crewai_ollama_native/src
python -m crewai_ollama_native.main
```

### Running the Gemini Direct Integration Example

```bash
cd crew_ai_gemini/src
python -m crew_ai_gemini.crew_ai_poc_ask_gemini2_5_pro_decorator
```

### Running the Gemini LangChain Example

```bash
cd crew_ai_gemini/src
python -m crew_ai_gemini.crew_ai_poc_ask_gemini2_5_pro
```

## Customization

Each example can be customized by modifying:

1. The config YAML files to change agent roles and task descriptions
2. The input parameters in main scripts to change research topics
3. The LLM configuration to use different models or parameters

## Experiments

The `experiments` directory contains personal explorations of different agent configurations, task structures, and model comparisons. These implementations serve as a playground for developing and testing new approaches to agent-based systems.

## Conclusion

These examples demonstrate different approaches to implementing agentic workflows using CrewAI with various LLM backends. By comparing the implementations, you can evaluate:

- Local vs. cloud-based models
- Different architectural patterns (decorator vs. functional)
- Performance and capability differences between models
- Various architecture and configuration approaches

The examples provide different implementation styles that can be chosen based on your preference for class-based vs. functional programming, offering flexibility for different development styles and use cases.
