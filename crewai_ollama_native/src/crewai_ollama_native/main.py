import sys
from src.crewai_ollama_native.crew import ResearchCrew

def run():
    # Define the inputs for the research crew
    print("run crew")
    inputs = {
        'topic': 'AI trends',
    }
    
    # Create and run the crew with the inputs
    # return ResearchCrew().crew().kickoff(inputs=inputs)
    crew = ResearchCrew().crew()
    result = crew.kickoff(inputs=inputs)

    # Print individual task outputs
    for task in crew.tasks:
        print(f"Task: {task.description}")
        print(f"Output: {task.output}")
    print("\n=== Research Results ===")
    print(f"result: {result}")

    return result

if __name__ == "__main__":
    # try:
    result = run()
    # print("\n=== Research Results ===")
    # print(result)
    # except Exception as e:
    #     print(f"Error during research: {str(e)}", file=sys.stderr)
    #     sys.exit(1)
