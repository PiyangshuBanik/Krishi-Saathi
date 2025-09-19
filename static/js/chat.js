document.addEventListener('DOMContentLoaded', () => {
    // --- DOM ELEMENTS ---
    const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-button');
    const suggestionsContainer = document.querySelector('.suggestions');
    const welcomeMessage = document.querySelector('.welcome-message');
    const themeToggle = document.querySelector('.theme-toggle');
    const themeText = document.querySelector('.theme-text');

    // --- GEMINI API CONFIG ---
    const apiKey = "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU"; // IMPORTANT: Add your Gemini API Key here
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;

    const systemInstruction = {
        parts: [{ text: "You are an expert agricultural assistant named KrishiBot. Provide detailed, accurate and helpful responses about farming, crops, weather impact, soil health, pest control, and sustainable agriculture practices. Format your answers with clear paragraphs. If asked about something outside agriculture, except for greetings, politely decline and refocus on farming topics." }]
    };
    
    let history = [];

    // --- THEME MANAGEMENT ---
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (themeText) {
            themeText.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
        }
    };

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    }

    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    
    // --- CHAT FUNCTIONALITY ---
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatResponse(text) {
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    function displayMessage(messageContent, sender) {
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const name = sender === 'user' ? 'You' : 'Krishi-Saathi';

        messageElement.innerHTML = `
            <div class="message-header">
                <i class="fas fa-${sender === 'user' ? 'user-alt' : 'robot'}"></i>
                <span>${name}</span>
            </div>
            <div class="message-text">${formatResponse(escapeHtml(messageContent))}</div>
            <div class="timestamp">${time}</div>
        `;
        
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    if (suggestionsContainer) {
        suggestionsContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion')) {
                chatInput.value = e.target.textContent;
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = chatInput.value.trim();
        if (!input) return;

        displayMessage(input, 'user');
        chatInput.value = '';
        const typingIndicator = showTyping();
        toggleInput(true);
        
        history.push({ role: "user", parts: [{ text: input }] });

        try {
            if (!apiKey) {
                throw new Error("API_KEY_MISSING");
            }
            const payload = {
                contents: history,
                systemInstruction: systemInstruction,
                generationConfig: { 
                    temperature: 0.7, 
                    maxOutputTokens: 1000,
                    topP: 0.8,
                    topK: 40
                }
            };

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || "I'm sorry, I couldn't process that. Please try again.";
            
            displayMessage(reply, 'bot');
            history.push({ role: "model", parts: [{ text: reply }] });

        } catch (error) {
            console.error('Error:', error);
            let errorMessage = "I'm having trouble connecting right now. Please try again later.";
            if (error.message === "API_KEY_MISSING") {
                errorMessage = "The API key is missing. Please configure it in chat.js to enable the AI assistant.";
            }
            displayMessage(errorMessage, 'bot');
        } finally {
            typingIndicator.remove();
            toggleInput(false);
        }
    });

    function showTyping() {
        const typing = document.createElement('div');
        typing.className = 'typing-indicator';
        typing.innerHTML = `<div>Krishi-Saathi is typing</div><span></span><span></span><span></span>`;
        chatWindow.appendChild(typing);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return typing;
    }

    function toggleInput(disable) {
        sendBtn.disabled = disable;
        chatInput.disabled = disable;
        if (!disable) chatInput.focus();
    }
    
    chatInput.focus();
});
