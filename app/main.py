from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
from typing import Optional
import os

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

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

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

@app.get("/api/models")
async def list_models():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_API_URL.replace('/generate', '/tags')}")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Ollama API error")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 