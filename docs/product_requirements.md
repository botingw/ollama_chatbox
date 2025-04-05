# Ollama Chatbox: Product Requirements Document

## 1. Introduction

### 1.1 Purpose
Ollama Chatbox is an open-source web application that provides a user-friendly interface for interacting with Ollama's large language models (LLMs). It allows users to chat with various models through a clean, responsive web interface, and to generate research reports using CrewAI agents powered by both Ollama and Gemini models.

### 1.2 Scope
This document outlines the requirements, features, and specifications for the Ollama Chatbox application, including its user interface, backend API, infrastructure, integration with Ollama, and the research capabilities powered by CrewAI.

### 1.3 Definitions
- **Ollama**: An open-source platform for running large language models locally
- **LLM**: Large Language Model, an AI model capable of understanding and generating text
- **API**: Application Programming Interface
- **Docker**: A platform for developing, shipping, and running applications in containers
- **CrewAI**: A framework for orchestrating AI agents to perform complex tasks like research
- **Gemini**: Google's large language model accessed through Google AI Studio API

## 2. Target Audience

### 2.1 Primary Users
- Developers experimenting with LLMs
- AI researchers working with open-source models
- Hobbyists interested in deploying AI chatbots locally
- Users seeking privacy-focused AI chat solutions
- Researchers and students looking for AI-assisted research reports

### 2.2 User Needs
- Simple, intuitive chat interface
- Low-resource model options for limited hardware
- Self-hosted solution that doesn't require cloud services
- Easy installation and setup process
- Automated research report generation on various topics

## 3. Product Goals

### 3.1 Primary Goals
1. Provide a simple, intuitive interface for interacting with Ollama models
2. Enable easy deployment with minimal configuration
3. Support various Ollama models with easy switching between them
4. Ensure responsive performance on different devices
5. Maintain minimal resource requirements
6. Generate comprehensive research reports using AI agents

### 3.2 Success Metrics
1. Successful message exchange with LLMs
2. Support for multiple models
3. Ease of installation (measured by number of steps and prerequisites)
4. System resource usage
5. Quality and completeness of generated research reports

## 4. Features and Requirements

### 4.1 User Interface Requirements
1. **Chat Interface**
   - Clean, modern design using Tailwind CSS
   - Message history display with clear distinction between user and AI messages
   - Text input field for user messages
   - Send button for submitting messages
   - Auto-scroll to most recent messages
   - [TODO] Visual indication when the AI is responding

2. **Model Selection**
   - Dropdown menu for selecting different Ollama models
   - [TODO] Dynamic display of currently available models from API
   - Default model selection (smollm2:135m)
   - [TODO] Model metadata display (size, capabilities)

3. **Responsive Design**
   - Support for desktop and mobile devices
   - Appropriate sizing and spacing for different screen sizes

4. **Research Interface**
   - Topic input field for specifying research subjects
   - Model selection dropdown for choosing research backends (Ollama/Gemini)
   - "Start Research" button for initiating research tasks
   - Results display area showing process output and report content
   - Download button for saving generated research reports as Markdown files
   - Visual indication of research in progress

### 4.2 Backend API Requirements
1. **Chat Endpoint**
   - POST `/api/chat` for sending messages to the LLM
   - Support for model selection in the request
   - Proper error handling and timeout management
   - Structured response format
   - [TODO] Support for streaming responses

2. **Models Endpoint**
   - GET `/api/models` for listing available Ollama models
   - Integration with Ollama's API for model discovery
   - [TODO] Model pull endpoint for installing new models

3. **Research Endpoints**
   - POST `/api/research` for initiating research tasks
   - Support for specifying topic, model, and backend (Ollama/Gemini)
   - Dynamic configuration of research agents based on selected backend
   - Return of both process output and generated report content
   - Creation and storage of report files with unique filenames
   - GET `/api/research/report/{backend}/{filename}` for downloading reports
   - Appropriate error handling for research process failures

4. **Error Handling**
   - Clear error messages for users
   - Detailed logging for debugging
   - [TODO] Frontend error handling improvements
   - [TODO] Retry logic for failed requests

### 4.3 LLM & Agent Integration
1. **API Communication**
   - Integration with Ollama's REST API for chat functionality
   - Support for various models hosted by Ollama
   - Integration with CrewAI for research agent orchestration
   - Support for multiple backend providers (Ollama, Gemini)
   - Dynamic agent selection based on user preferences
   - [TODO] Better dynamic discovery of available models

2. **Research Agents**
   - Self-contained CrewAI agent directories (`test_gemini_agent`, `test_ollama_agent`)
   - Dynamic environment configuration based on user input
   - Support for multiple research roles (e.g., researcher, writer)
   - Generation of comprehensive Markdown reports

3. **Deployment**
   - Docker container for the application
   - Connection to a standalone Ollama container
   - Volume mounting for model persistence
   - Secure handling of API keys for external services

### 4.4 Performance Requirements
1. Response time for typical queries under 10 seconds
2. Support for multiple concurrent users
3. Handling of long-running research tasks (potentially minutes)
4. Progress indication for research operations
5. [TODO] Graceful handling of long-running model operations
6. [TODO] Progress indication for long-running operations

## 5. Technical Requirements

### 5.1 Software Requirements
1. **Backend**
   - Python 3.8+
   - FastAPI framework
   - Uvicorn ASGI server
   - HTTPX for async HTTP requests
   - CrewAI for agent orchestration

2. **Frontend**
   - HTML5
   - CSS3 with Tailwind CSS
   - Vanilla JavaScript (no framework)
   - [TODO] WebSocket support for real-time updates

3. **Infrastructure**
   - Docker and Docker Compose
   - Support for Linux, macOS, and Windows hosts

### 5.2 Dependencies
1. **External Services**
   - Ollama server running locally or in a container
   - At least one LLM model pulled in Ollama
   - CrewAI framework and its dependencies
   - Google AI API access (for Gemini models)
   - API keys configured in agent `.env` files

2. **System Requirements**
   - Minimum 4GB RAM (depends on chosen models)
   - Storage space for models (varies by model)
   - Internet connection for external API access (Gemini)

### 5.3 Security Requirements
1. No authentication required for local deployment
2. CORS protection for API endpoints
3. Input validation to prevent injection attacks
4. Secure handling of API keys
5. [TODO] Sanitization of model outputs

## 6. Future Enhancements

### 6.1 Potential Features
1. **Chat History Persistence**
   - [TODO] Ability to save and load chat histories
   - [TODO] Export chats to text files

2. **Model Management**
   - [TODO] Interface for pulling new models
   - [TODO] Model parameter adjustment

3. **Advanced UI Features**
   - [TODO] Markdown rendering in responses
   - [TODO] Syntax highlighting for code
   - [TODO] Message editing and deletion
   - [TODO] Theme switching (light/dark mode)

4. **Research Enhancements**
   - [TODO] Support for additional research backends
   - [TODO] Customizable research parameters
   - [TODO] Research history and saved reports
   - [TODO] Ability to continue or refine existing research

5. **Performance Improvements**
   - [TODO] Response streaming for better UX
   - [TODO] Progressive loading of chat history
   - [TODO] Optimized model selection for device capabilities
   - [TODO] Caching common responses

## 7. Limitations and Constraints

### 7.1 Known Limitations
1. Performance depends on host hardware capabilities
2. Limited to models supported by Ollama for chat functionality
3. No user authentication or multi-user support
4. Research with Gemini models requires API key and internet access
5. Research tasks may take several minutes to complete
6. Limited customization of research agent behavior
7. [TODO] No persistent storage of conversations

### 7.2 Dependencies
1. Requires Ollama to be running and accessible
2. Model availability depends on what's installed in Ollama
3. Response times vary by model size and complexity
4. Research with Gemini models is subject to Google API usage limits and terms
5. CrewAI agent configuration relies on properly set up agent directories

## 8. Appendix

### 8.1 API Specification
- `POST /api/chat`
  - Request Body:
    ```json
    {
      "message": "Your message here",
      "model": "smollm2:135m",
      "stream": false
    }
    ```
  - Response:
    ```json
    {
      "response": "AI response here",
      "model": "smollm2:135m"
    }
    ```

- `GET /api/models`
  - Response:
    ```json
    {
      "models": [
        {"name": "smollm2:135m"},
        {"name": "llama2"},
        {"name": "mistral"}
      ]
    }
    ```

- `POST /api/research`
  - Request Body:
    ```json
    {
      "topic": "Your research topic",
      "model": "gemini-pro",
      "backend": "gemini"
    }
    ```
  - Response:
    ```json
    {
      "stdout_result": "Raw output from the research process",
      "report_content": "Content of the generated markdown report",
      "report_filename": "research_topic_20250404_123456_abcdef12.md",
      "model": "gemini-pro",
      "error": null
    }
    ```

- `GET /api/research/report/{backend}/{filename}`
  - Response: File download (Markdown)

- [TODO] `POST /api/models/pull`
  - Request Body:
    ```json
    {
      "name": "model-name"
    }
    ```
  - Response:
    ```json
    {
      "status": "success",
      "message": "Model pulled successfully"
    }
    ```

### 8.2 Deployment Architecture
The application consists of three main components:
1. Ollama server container - Provides the LLM API and manages models
2. Chatbox container - Provides the web UI and API endpoints
3. CrewAI agent directories - Contains the research agent configurations and code

These communicate via HTTP, with the Chatbox server making API calls to the Ollama server and orchestrating the CrewAI agents for research tasks. The Gemini research backend communicates directly with Google's AI API. 