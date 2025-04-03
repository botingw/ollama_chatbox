import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import CrewAI components
from crewai import Agent, Task, Crew, Process

# Import Gemini LLM
from langchain_google_genai import ChatGoogleGenerativeAI

# --- LLM Configuration ---
# Retrieve the API key from environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")
print(f"google_api_key: {google_api_key}")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. "
                     "Make sure to set it in the .env file.")

# Instantiate the Gemini model
# Common models: "gemini-pro", "gemini-1.0-pro", "gemini-1.5-flash-latest", "gemini-1.5-pro-latest"
# Check Google AI documentation for the latest available models.
# Note: llm provider in litellm package has bug, where model string always starts with model/, need hardcode replace it with gemini/
# also google_api_key is not passed to api_key in litellm request, also need hardcode it
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-pro-exp-03-25",
    verbose=True,
    temperature=0.6, # Controls creativity (0.0 = deterministic, 1.0 = max creativity)
    google_api_key=google_api_key
)

# --- Agent Definitions ---

# 1. Researcher Agent
researcher = Agent(
  role='Senior Technology Researcher',
  goal='Find the latest advancements and key players in {topic}',
  backstory="""You are an expert researcher at a leading tech think tank.
  Your goal is to identify groundbreaking developments, potential challenges,
  and major companies or research groups involved in a specific technology area.
  You are known for your thoroughness and ability to synthesize complex information.""",
  verbose=True,
  allow_delegation=False, # This agent does not delegate tasks
  llm=llm # Assign the Gemini model to this agent
  # Optional: Add tools like web search here if needed
  # tools=[search_tool]
)

# 2. Writer Agent
writer = Agent(
  role='Technology Content Strategist',
  goal='Craft a compelling and concise summary of technology advancements based on research findings.',
  backstory="""You are a skilled writer specializing in technology communication.
  You can take complex research findings and translate them into clear, engaging narratives
  suitable for a blog post or internal briefing. You focus on clarity, impact, and accuracy.""",
  verbose=True,
  allow_delegation=False,
  llm=llm # Assign the Gemini model to this agent
)

# --- Task Definitions ---

# Task 1: Research
research_task = Task(
  description="""Conduct comprehensive research on the latest advancements in {topic}.
  Focus on:
  - Key technological breakthroughs in the last 1-2 years.
  - Major companies or research institutions involved.
  - Potential future applications and impact.
  - Any significant challenges or limitations.""",
  expected_output="""A detailed report summarizing the findings.
  Include bullet points for key breakthroughs, players, applications, and challenges.""",
  agent=researcher # Assign task to the researcher agent
)

# Task 2: Writing
# This task depends on the output of the research_task. CrewAI handles this dependency
# implicitly when tasks are listed sequentially in the Crew definition.
write_summary_task = Task(
  description="""Based on the research report provided, write a concise and engaging summary
  (2-3 paragraphs) highlighting the most important advancements in {topic}.
  Make it suitable for a non-expert audience but retain technical accuracy.
  Focus on the 'so what?' - why these advancements matter.""",
  expected_output="""A well-written summary document (2-3 paragraphs long)
  that is clear, concise, and engaging for a general tech audience.""",
  agent=writer # Assign task to the writer agent
  # Optional: Specify context if needed explicitly, though sequential process handles it.
  # context=[research_task]
)

# --- Crew Definition ---

# Define the crew with agents and tasks
# The process will be sequential: researcher runs first, then writer.
tech_crew = Crew(
  agents=[researcher, writer],
  tasks=[research_task, write_summary_task],
  process=Process.sequential, # Tasks will be executed one after the other
  verbose=True # Set verbosity level (0, 1, or 2)
)

# --- Execute the Crew ---

# Define the input topic for the workflow
crew_input = {'topic': 'Quantum Computing'}

# Start the crew's work
print("#############################")
print(f"## Starting Crew for Topic: {crew_input['topic']}")
print("#############################\n")

result = tech_crew.kickoff(inputs=crew_input)

print("\n\n#############################")
print("## Crew Execution Finished ##")
print("#############################\n")
for task in tech_crew.tasks:
    print(f"Task: {task.description}")
    print(f"Output: {task.output}")
print("Final Result:")
print(result)