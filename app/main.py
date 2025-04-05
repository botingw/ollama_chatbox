from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
from typing import Optional, List, Dict, Any
import os
import subprocess
import shlex
import re # <--- Add re for regex substitution
import datetime
import uuid # For unique filenames
import shutil # For renaming files

app = FastAPI(title="Ollama Chatbox API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

class ChatRequest(BaseModel):
    message: str
    model: str = "smollm2:135m"  # default model
    stream: bool = False

class ChatResponse(BaseModel):
    response: str
    model: str

class ResearchRequest(BaseModel):
    topic: str
    model: str # Model selected in UI
    backend: str # Backend selected in UI ('ollama' or 'gemini')

class ResearchResponse(BaseModel):
    stdout_result: Optional[str] = None
    report_content: Optional[str] = None
    report_filename: Optional[str] = None
    error: Optional[str] = None
    model: str # Will reflect the requested model/backend

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
# Set base URL for Ollama client (if still needed elsewhere, otherwise handled by research module)
# Check if this is still required or if research/llm_init.py handles it sufficiently
# os.environ["OLLAMA_BASE_URL"] = OLLAMA_API_URL.replace("/api/generate", "")

@app.get("/")
async def read_root():
    return FileResponse("app/static/index.html")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"Sending request to Ollama: {OLLAMA_API_URL}")
            try:
                response = await client.post(
                    OLLAMA_API_URL,
                    json={
                        "model": request.model,
                        "prompt": request.message,
                        "stream": request.stream
                    }
                )
                
                if response.status_code != 200:
                    error_detail = f"Ollama API error: Status {response.status_code} - {response.text}"
                    print(error_detail)
                    raise HTTPException(status_code=response.status_code, detail=error_detail)
                
                data = response.json()
                return ChatResponse(
                    response=data.get("response", ""),
                    model=request.model
                )
            except httpx.RequestError as e:
                error_detail = f"Error communicating with Ollama: {str(e)}"
                print(error_detail)
                raise HTTPException(status_code=503, detail=error_detail)
            except httpx.TimeoutException as e:
                error_detail = f"Timeout while waiting for Ollama response: {str(e)}"
                print(error_detail)
                raise HTTPException(status_code=504, detail=error_detail)
            
    except Exception as e:
        error_detail = f"Error in chat endpoint: {str(e)}, Type: {type(e)}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

def update_env_model(env_file_path: str, model_name: str, backend: str):
    """Reads a .env file, updates MODEL, prepends backend prefix, and writes it back."""
    try:
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            print(f"Warning: .env file not found at {env_file_path}. Creating one.")
            lines = []

        # --- Construct the correct model string with prefix ---
        # Ensure backend is lowercase for comparison
        backend_lower = backend.lower()
        prefixed_model_name = model_name # Default to original name if backend unknown

        if backend_lower == "ollama":
            # Prepend 'ollama/' unless it's already there (just in case)
            if not model_name.startswith("ollama/"):
                 prefixed_model_name = f"ollama/{model_name}"
        elif backend_lower == "gemini":
             # Prepend 'gemini/' unless it's already there
            if not model_name.startswith("gemini/"):
                prefixed_model_name = f"gemini/{model_name}"
        else:
            print(f"Warning: Unknown backend '{backend}' provided for .env update. Using model name as is.")
        # ---

        updated_lines = []
        model_updated = False
        # Use regex to find and replace or add the MODEL line
        model_line = f"MODEL={prefixed_model_name}\n" # <--- Target MODEL=

        for line in lines:
            # Match lines starting with optional whitespace, then MODEL, optional space, '=', any value
            if re.match(r"^\s*MODEL\s*=", line): # <--- Target MODEL=
                updated_lines.append(model_line)
                model_updated = True
                print(f"Updating existing MODEL line in {env_file_path}")
            else:
                # Keep other lines, ensuring they end with a newline if not empty
                stripped_line = line.strip()
                if stripped_line: # Avoid adding extra newlines for empty lines
                    updated_lines.append(line.rstrip() + '\n')


        if not model_updated:
            print(f"Adding MODEL line to {env_file_path}")
            updated_lines.append(model_line)

        # Write updated content back
        final_content = "".join(updated_lines)
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        print(f"Set MODEL in {env_file_path} to: {prefixed_model_name}")
        return True, None # Success

    except Exception as e:
        error_msg = f"Error updating .env file ({env_file_path}): {str(e)}"
        print(error_msg)
        return False, error_msg # Failure

@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    # --- Determine Crew Project Path ---
    base_research_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "research"))
    agent_dir_name = ""
    response_model_str = f"{request.backend}:{request.model}" # Use requested info for response clarity

    if request.backend.lower() == "ollama":
        agent_dir_name = "test_ollama_agent"
    elif request.backend.lower() == "gemini":
        agent_dir_name = "test_gemini_agent"
    else:
        # Handle unsupported backend - return an error response
        error_detail = f"Unsupported backend specified: {request.backend}"
        print(error_detail)
        # Return error via the response model, not HTTP exception directly
        return ResearchResponse(error=error_detail, model=response_model_str)

    crew_project_path = os.path.join(base_research_path, agent_dir_name)
    print(f"Selected crew project path: {crew_project_path} for backend: {request.backend}")

    if not os.path.isdir(crew_project_path):
         error_detail = f"Crew project directory not found for backend '{request.backend}' at: {crew_project_path}"
         print(error_detail)
         return ResearchResponse(error=error_detail, model=response_model_str)

    # --- Update .env file in the selected project ---
    env_file_path = os.path.join(crew_project_path, ".env")
    env_updated, env_error = update_env_model(env_file_path, request.model, request.backend)

    if not env_updated:
        # Return error if .env update failed
        return ResearchResponse(error=env_error, model=response_model_str)

    # --- Prepare Subprocess Environment ---
    subprocess_env = os.environ.copy()
    subprocess_env["RESEARCH_TOPIC"] = request.topic
    # Propagate API keys if needed by the crew's .env setup
    if "GOOGLE_API_KEY" in os.environ:
        subprocess_env["GOOGLE_API_KEY"] = os.environ["GOOGLE_API_KEY"]
    # Note: Ollama base URL is often set via OPENAI_API_BASE in the crew's .env file

    # --- Execute Subprocess ---
    command = shlex.split("crewai run")
    print(f"Running command: {' '.join(command)} in {crew_project_path}")

    try:
        process = subprocess.run(
            command,
            cwd=crew_project_path,
            capture_output=True,
            text=True,
            env=subprocess_env,
            check=True,
            timeout=300
        )

        print(f"Subprocess stdout:\n{process.stdout}")
        if process.stderr: # Only print stderr if it's not empty
             print(f"Subprocess stderr:\n{process.stderr}")

        stdout_result = process.stdout.strip()
        report_content = None
        read_error = None
        report_final_filename = None # Variable for the unique filename

        # --- Attempt to read and RENAME the report file ---
        default_report_name = "report.md"
        report_file_path = os.path.join(crew_project_path, default_report_name)
        print(f"Checking for default report file: {report_file_path}")

        if os.path.exists(report_file_path):
            try:
                # 1. Generate unique filename (timestamp + uuid + topic slug)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                topic_slug = re.sub(r'\W+', '_', request.topic)[:50] # Basic slugify
                unique_id = str(uuid.uuid4())[:8]
                report_final_filename = f"research_{topic_slug}_{timestamp}_{unique_id}.md"
                new_report_path = os.path.join(crew_project_path, report_final_filename)

                # 2. Read the content BEFORE renaming
                with open(report_file_path, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                print(f"Successfully read {default_report_name}")

                # 3. Rename the file
                shutil.move(report_file_path, new_report_path)
                print(f"Renamed {default_report_name} to {report_final_filename}")

            except Exception as file_error:
                read_error = f"Error processing report file: {str(file_error)}"
                print(read_error)
                # Reset potentially partially set variables if error occurred
                report_content = None
                report_final_filename = None
        else:
            read_error = f"{default_report_name} not found in {crew_project_path} after crew execution."
            print(read_error)

        # --- Log before returning ---
        print(f"Returning ResearchResponse:")
        print(f"  stdout_result: {'Present' if stdout_result else 'None'}")
        print(f"  report_content: {'Present' if report_content else 'None'}")
        print(f"  report_filename: {report_final_filename}") # <--- Check this value
        print(f"  error: {read_error}")
        print(f"  model: {response_model_str}")
        # --- End Log ---

        return ResearchResponse(
            stdout_result=stdout_result,
            report_content=report_content,
            report_filename=report_final_filename,
            error=read_error,
            model=response_model_str
        )

    # --- Handle Subprocess Errors ---
    except subprocess.CalledProcessError as e:
        error_detail = f"Crew execution failed (Exit Code {e.returncode}). Stderr: {e.stderr.strip()}"
        print(error_detail)
        print(f"Stdout: {e.stdout.strip()}") # Also log stdout on error
        return ResearchResponse(error=error_detail, model=response_model_str)
    except subprocess.TimeoutExpired as e:
        error_detail = f"Crew execution timed out after {e.timeout} seconds."
        print(error_detail)
        return ResearchResponse(error=error_detail, model=response_model_str)
    except Exception as e:
        error_detail = f"Unexpected error running crewai subprocess: {str(e)}"
        print(error_detail)
        return ResearchResponse(error=error_detail, model=response_model_str)

@app.get("/api/models")
async def list_models() -> Dict[str, List[Dict[str, Any]]]:
    ollama_models = []
    gemini_models = [
        {"name": "gemini-1.5-pro-latest", "backend": "gemini"},
        {"name": "gemini-1.5-flash-latest", "backend": "gemini"},
        {"name": "gemini-2.5-pro-exp-03-25", "backend": "gemini"},
    ]
    all_models = []

    # Try to get models from Ollama
    try:
        ollama_base_url = OLLAMA_API_URL.replace('/api/generate', '')
        ollama_tags_url = f"{ollama_base_url}/api/tags"
        print(f"Fetching Ollama models from: {ollama_tags_url}")

        async with httpx.AsyncClient() as client:
            response = await client.get(ollama_tags_url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                ollama_raw_models = data.get('models', [])
                if isinstance(ollama_raw_models, list):
                   ollama_models = [{"name": model.get("name"), "backend": "ollama"}
                                    for model in ollama_raw_models if model.get("name")]
                else:
                    print("Warning: Ollama /api/tags did not return a list of models.")
            else:
                 print(f"Warning: Ollama API error fetching models: Status {response.status_code}")

    except httpx.RequestError as e:
        print(f"Warning: Error communicating with Ollama to fetch models: {str(e)}")
    except Exception as e:
        print(f"Warning: Unexpected error fetching Ollama models: {str(e)}")

    # Combine lists (Ollama first, then Gemini)
    all_models.extend(ollama_models)
    all_models.extend(gemini_models)

    # Return the combined list
    return {"models": all_models}

# --- ADD Download Endpoint ---
from fastapi import Path as FastApiPath # Avoid conflict with os.path

# Define base path for security (reports should stay within research dirs)
BASE_REPORTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "research"))

@app.get("/api/research/report/{backend}/{filename}")
async def download_report(
    backend: str = FastApiPath(..., description="The backend used ('ollama' or 'gemini')"),
    filename: str = FastApiPath(..., description="The unique report filename to download")
    ):
    """Serves the generated research report file."""

    # Basic validation on filename to prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    # Determine the correct subdirectory based on backend
    if backend.lower() == "ollama":
        agent_dir_name = "test_ollama_agent"
    elif backend.lower() == "gemini":
        agent_dir_name = "test_gemini_agent"
    else:
         raise HTTPException(status_code=400, detail="Invalid backend specified.")

    # Construct the full path and ensure it's within the allowed base path
    full_path = os.path.abspath(os.path.join(BASE_REPORTS_PATH, agent_dir_name, filename))

    if not full_path.startswith(os.path.join(BASE_REPORTS_PATH, agent_dir_name)):
         # Security check failed!
         print(f"Attempted path traversal: {full_path}")
         raise HTTPException(status_code=400, detail="Invalid filename path.")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Report file not found.")

    print(f"Serving report file: {full_path}")
    
    # Use FileResponse to serve the file with a forced filename
    # The attachement_filename parameter forces the Content-Disposition
    return FileResponse(
        path=full_path,
        filename=filename, # This becomes the suggested download name
        media_type='text/markdown', # Set appropriate media type
        headers={
            # Force download with the specified filename - critical for correct download name
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 