document.addEventListener('DOMContentLoaded', () => {
    // Chat elements
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const chatContainer = document.getElementById('chatContainer');
    const modelSelect = document.getElementById('modelSelect');

    // Research elements
    const topicInput = document.getElementById('topicInput');
    const researchButton = document.getElementById('researchButton');
    const researchContainer = document.getElementById('researchContainer');
    const researchModelSelect = document.getElementById('researchModelSelect');

    // Load available models
    async function loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            const models = data.models || [];
            
            // Update both model selects
            [modelSelect, researchModelSelect].forEach(select => {
                select.innerHTML = '';
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = model.name;
                    select.appendChild(option);
                });
            });
        } catch (error) {
            console.error('Error loading models:', error);
        }
    }

    // Add message to chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Add research result
    function addResearchResult(content) {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'research-result p-4 mb-4 bg-gray-50 rounded-md';
        resultDiv.innerHTML = `<div class="whitespace-pre-wrap">${content}</div>`;
        researchContainer.appendChild(resultDiv);
        researchContainer.scrollTop = researchContainer.scrollHeight;
    }

    // Send message to API
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Disable input and button while processing
        messageInput.disabled = true;
        sendButton.disabled = true;

        // Add user message to chat
        addMessage(message, true);
        messageInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: modelSelect.value,
                    stream: false
                })
            });

            if (!response.ok) {
                throw new Error('API request failed');
            }

            const data = await response.json();
            addMessage(data.response);
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your request.');
        } finally {
            // Re-enable input and button
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        }
    }

    // Start research
    async function startResearch() {
        const topic = topicInput.value.trim();
        if (!topic) return;

        // Disable input and button while processing
        topicInput.disabled = true;
        researchButton.disabled = true;

        // Clear previous results
        researchContainer.innerHTML = '';

        try {
            const response = await fetch('/api/research', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic: topic,
                    model: researchModelSelect.value
                })
            });

            if (!response.ok) {
                throw new Error('Research request failed');
            }

            const data = await response.json();
            addResearchResult(data.result);
        } catch (error) {
            console.error('Error:', error);
            addResearchResult('Sorry, there was an error processing your research request.');
        } finally {
            // Re-enable input and button
            topicInput.disabled = false;
            researchButton.disabled = false;
            topicInput.focus();
        }
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    researchButton.addEventListener('click', startResearch);
    topicInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            startResearch();
        }
    });

    // Load models on startup
    loadModels();
}); 