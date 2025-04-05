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
            if (!response.ok) {
                throw new Error(`API request failed with status ${response.status}`);
            }
            const data = await response.json();
            const models = data.models || [];

            // Clear existing options in both selects
            [modelSelect, researchModelSelect].forEach(select => {
                select.innerHTML = '';
            });

            if (models.length === 0) {
                console.warn("No models received from /api/models endpoint.");
                // Optionally add a placeholder option
                [modelSelect, researchModelSelect].forEach(select => {
                    const option = document.createElement('option');
                    option.textContent = "No models available";
                    option.disabled = true;
                    select.appendChild(option);
                });
                return; // Stop if no models
            }

            // Update both model selects
            models.forEach(model => {
                // Create option for the regular chat select
                const chatOption = document.createElement('option');
                chatOption.value = model.name;
                chatOption.textContent = model.name;
                // Only add Ollama models to the standard chat select
                if (model.backend === 'ollama') {
                    modelSelect.appendChild(chatOption);
                }

                // Create option for the research select
                const researchOption = document.createElement('option');
                researchOption.value = model.name;
                researchOption.textContent = `${model.name} (${model.backend})`; // Show backend in text
                researchOption.dataset.backend = model.backend; // Store backend in data attribute
                researchModelSelect.appendChild(researchOption);
            });
        } catch (error) {
            console.error('Error loading models:', error);
            [modelSelect, researchModelSelect].forEach(select => {
                select.innerHTML = ''; // Clear potentially partial list
                const option = document.createElement('option');
                option.textContent = "Error loading models";
                option.disabled = true;
                select.appendChild(option);
            });
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
    function addResearchResult(resultData) {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'research-result p-4 mb-4 bg-gray-50 rounded-md shadow';

        let contentHTML = '';
        let reportSectionHTML = '';

        if (resultData.report_filename && resultData.report_content) {
            const backend = resultData.model?.split(':')[0] || 'unknown';
            const downloadUrl = `/api/research/report/${encodeURIComponent(backend)}/${encodeURIComponent(resultData.report_filename)}`;

            reportSectionHTML = `
                <hr class="my-4">
                <div class="report-output mt-4">
                    <div class="flex justify-between items-center mb-1">
                        <b class="block">Report Content:</b>
                        <a href="${downloadUrl}" 
                           download="${resultData.report_filename}" 
                           class="inline-block bg-blue-500 hover:bg-blue-700 text-white text-sm font-bold py-1 px-3 rounded transition duration-150 ease-in-out"
                           onclick="this.download='${resultData.report_filename}'">
                            Download Report (.md)
                        </a>
                    </div>
                    <div class="prose max-w-none p-2 border rounded bg-white">
                         <pre class="whitespace-pre-wrap">${escapeHtml(resultData.report_content)}</pre>
                    </div>
                </div>`;
        } else if (resultData.report_content) {
             reportSectionHTML = `
                <hr class="my-4">
                <div class="report-output mt-4">
                    <b class="block mb-1">Report Content (Download Unavailable):</b>
                     <div class="prose max-w-none p-2 border rounded bg-white">
                        <pre class="whitespace-pre-wrap">${escapeHtml(resultData.report_content)}</pre>
                    </div>
                </div>`;
        }

        if (resultData.error && !resultData.stdout_result && !resultData.report_content) {
            contentHTML = `<div class="text-red-600"><b>Error:</b><br><pre class="whitespace-pre-wrap">${escapeHtml(resultData.error)}</pre></div>`;
        } else {
             if (resultData.stdout_result) {
                 contentHTML = `<div class="stdout-output"><b class="block mb-1">Crew Output (stdout):</b><pre class="whitespace-pre-wrap bg-gray-100 p-2 rounded">${escapeHtml(resultData.stdout_result)}</pre></div>`;
             } else {
                 contentHTML = `<div class="text-gray-500">Crew output (stdout) is empty.</div>`
             }
             contentHTML += reportSectionHTML;

             if (resultData.error) {
                  contentHTML += `<div class="text-orange-600 mt-2"><b>Note:</b> ${escapeHtml(resultData.error)}</div>`;
             }
        }

        resultDiv.innerHTML = contentHTML;
        researchContainer.appendChild(resultDiv);
        researchContainer.scrollTop = researchContainer.scrollHeight;
    }

    // Helper function to escape HTML
    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
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
        const selectedOption = researchModelSelect.options[researchModelSelect.selectedIndex];

        // Basic validation
        if (!topic) {
            alert("Please enter a research topic.");
            topicInput.focus();
            return;
        }
        if (!selectedOption || selectedOption.disabled) {
             alert("Please select a valid research model.");
             return;
        }

        const modelName = selectedOption.value;
        const backendName = selectedOption.dataset.backend;

        if (!backendName) {
            alert("Could not determine the backend for the selected model. Please reload.");
            return;
        }

        console.log(`Starting research on "${topic}" using model "${modelName}" with backend "${backendName}"`);

        // Disable input and button while processing
        topicInput.disabled = true;
        researchButton.disabled = true;

        // Clear previous results and show loading message
        researchContainer.innerHTML = '<div class="text-center p-4 text-gray-500">Running research...</div>';

        try {
            const response = await fetch('/api/research', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic: topic,
                    model: modelName,
                    backend: backendName
                })
            });

            // Check response status BEFORE trying to parse JSON
            if (!response.ok) {
                // Try to get error details from response body if possible
                let errorDetail = `Research request failed with status ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || JSON.stringify(errorData); // Use FastAPI 'detail' if available
                } catch (e) {
                    // Ignore if response body is not JSON or empty
                }
                throw new Error(errorDetail);
            }

            const data = await response.json();
            researchContainer.innerHTML = ''; // Clear loading message
            addResearchResult(data); // Pass the whole data object
        } catch (error) {
            console.error('Error in startResearch:', error);
            researchContainer.innerHTML = ''; // Clear loading message
            // Display the detailed error message from the catch block
            addResearchResult({ error: error.message || 'Sorry, there was an error processing your research request.' });
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