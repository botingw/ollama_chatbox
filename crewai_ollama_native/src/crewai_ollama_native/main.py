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
    return ResearchCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    # try:
    result = run()
    print("\n=== Research Results ===")
    print(result)
    # except Exception as e:
    #     print(f"Error during research: {str(e)}", file=sys.stderr)
    #     sys.exit(1)
