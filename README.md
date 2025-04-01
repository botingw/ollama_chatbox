# Ollama Chatbox

A modern web-based chat interface for interacting with Ollama's LLM models. This application provides a clean, user-friendly interface to chat with various LLM models supported by Ollama.

## Features

- Modern, responsive UI using Tailwind CSS
- Support for multiple Ollama models
- Real-time chat interface
- API endpoints for programmatic access
- Comprehensive test coverage

## Prerequisites

- Docker installed
- Docker Compose installed

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ollama_chatbox.git
cd ollama_chatbox
```

2. Create and activate a conda environment:
```bash
conda create -n ollama_chatbox python=3.8
conda activate ollama_chatbox
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Run the tests:
```bash
pytest
```

## Running the Application

1. Start the Ollama service using the official Docker image:
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

2. Pull and test a model (e.g., smollm2:135m):
```bash
docker exec -it ollama ollama pull smollm2:135m
docker exec -it ollama ollama run smollm2:135m "Hello, how are you?"
```

3. Start the chatbox application:
```bash
docker-compose up --build
```

4. Open your browser and navigate to:
```
http://localhost:8000
```

## API Endpoints

- `POST /api/chat`: Send a message to the LLM
  ```json
  {
    "message": "Your message here",
    "model": "smollm2:135m",
    "stream": false
  }
  ```

- `GET /api/models`: List available Ollama models

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 