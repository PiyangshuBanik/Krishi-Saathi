document.addEventListener('DOMContentLoaded', () => {
    // =================================================================
    // --- ⚠️ SECURITY WARNING & CONFIGURATION ---
    // =================================================================

    // IMPORTANT: NEVER expose your API key in client-side JavaScript.
    // Anyone can view your page source, steal your key, and use your API quota.
    // For production, you MUST hide this key on a backend server and have your
    // website talk to your server, which then securely calls the Google API.
    //
    // How to get a key: Visit https://aistudio.google.com/app/apikey
    const GEMINI_API_KEY = "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU";

    const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${GEMINI_API_KEY}`;

    const SYSTEM_INSTRUCTION = {
        parts: [{
            text: "You are an expert agricultural assistant named KrishiBot. Your purpose is to provide detailed, accurate, and helpful responses about farming, crops, weather, soil health, pest control, and sustainable agriculture practices. Format your answers in clear, easy-to-read paragraphs. Use bold text for key terms. If a question is outside the scope of agriculture, you must politely decline to answer and state your purpose as an agricultural assistant."
        }]
    };

    // =================================================================
    // --- DOM ELEMENT SELECTION ---
    // =================================================================
    const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-button');
    const voiceBtn = document.getElementById('voice-button');
    const suggestionsContainer = document.querySelector('.suggestions');
    const welcomeMessage = document.querySelector('.welcome-message');
    const themeToggle = document.querySelector('.theme-toggle');
    const themeText = document.querySelector('.theme-text');

    // =================================================================
    // --- STATE MANAGEMENT ---
    // =================================================================
    let conversationHistory = [];
    let recognition; // For speech recognition

    // =================================================================
    // --- UI HELPER FUNCTIONS ---
    // =================================================================

    /** Sanitizes text to prevent XSS attacks */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /** Formats bot responses with basic markdown */
    function formatResponse(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italics
            .replace(/\n/g, '<br>'); // Newlines
    }

    /** Displays a message in the chat window */
    function displayMessage(content, sender) {
        welcomeMessage?.remove();
        const timestamp = new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
        const senderName = sender === 'user' ? 'You' : 'KrishiBot';
        const icon = sender === 'user' ? 'fa-user' : 'fa-robot';

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = `
            <div class="message-header">
                <i class="fas ${icon}"></i>
                <span>${senderName}</span>
            </div>
            <div class="message-text">${formatResponse(escapeHtml(content))}</div>
            <div class="timestamp">${timestamp}</div>
        `;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        if (sender === 'bot') {
            speak(content);
        }
    }

    /** Shows the "typing..." indicator */
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.className = 'message bot';
        indicator.innerHTML = `
            <div class="message-header">
                <i class="fas fa-robot"></i>
                <span>KrishiBot</span>
            </div>
            <div class="typing-dots"><span></span><span></span><span></span></div>
        `;
        chatWindow.appendChild(indicator);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return indicator;
    }

    /** Enables or disables the input form */
    function toggleInput(disabled) {
        chatInput.disabled = disabled;
        sendBtn.disabled = disabled;
        voiceBtn.disabled = disabled;
        if (!disabled) {
            chatInput.focus();
        }
    }

    // =================================================================
    // --- CORE CHAT LOGIC ---
    // =================================================================

    async function handleChatSubmit(event) {
        event.preventDefault();
        const userInput = chatInput.value.trim();
        if (!userInput) return;

        // Immediately display user's message
        displayMessage(userInput, 'user');
        conversationHistory.push({
            role: "user",
            parts: [{
                text: userInput
            }]
        });
        chatInput.value = '';

        toggleInput(true);
        const typingIndicator = showTypingIndicator();

        try {
            if (!GEMINI_API_KEY || GEMINI_API_KEY === "PASTE_YOUR_GEMINI_API_KEY_HERE") {
                throw new Error("API_KEY_MISSING");
            }

            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contents: conversationHistory,
                    systemInstruction: SYSTEM_INSTRUCTION,
                    generationConfig: {
                        temperature: 0.7,
                        maxOutputTokens: 1000,
                    },
                    safetySettings: [{
                            category: "HARM_CATEGORY_HARASSMENT",
                            threshold: "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            category: "HARM_CATEGORY_HATE_SPEECH",
                            threshold: "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold: "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            category: "HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold: "BLOCK_MEDIUM_AND_ABOVE"
                        }
                    ]
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            const botReply = data?.candidates?.[0]?.content?.parts?.[0]?.text || "Sorry, I encountered an issue. Please try again.";

            displayMessage(botReply, 'bot');
            conversationHistory.push({
                role: "model",
                parts: [{
                    text: botReply
                }]
            });

        } catch (error) {
            console.error("Chat Error:", error);
            const errorMessage = (error.message === "API_KEY_MISSING") ?
                "⚠️ Configuration Error: The API key is missing. Please contact the site administrator." :
                // "⚠️ Connection Error: I'm unable to connect to the server right now. Please check your internet connection and try again.";
            displayMessage(errorMessage, 'bot');
        } finally {
            typingIndicator.remove();
            toggleInput(false);
        }
    }

    // =================================================================
    // --- WEB APIS (THEME, SPEECH RECOGNITION, TEXT-TO-SPEECH) ---
    // =================================================================

    // --- Theme ---
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (themeText) themeText.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
    }

    // --- Speech-to-Text (Voice Recognition) ---
    function setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.lang = 'en-IN'; // Set to English (India)
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = () => voiceBtn.classList.add('recording');
            recognition.onend = () => voiceBtn.classList.remove('recording');
            recognition.onerror = (event) => console.error('Speech recognition error:', event.error);
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                chatInput.value = transcript;
                // Automatically submit the form
                chatForm.dispatchEvent(new Event('submit', {
                    cancelable: true
                }));
            };
        } else {
            voiceBtn.style.display = 'none'; // Hide button if not supported
            console.warn("Speech recognition not supported in this browser.");
        }
    }

    // --- Text-to-Speech ---
    // function speak(text) {
    //     if ('speechSynthesis' in window) {
    //         // Cancel any previous speech
    //         window.speechSynthesis.cancel();

    //         // Create a new utterance
    //         const utterance = new SpeechSynthesisUtterance(text.replace(/<[^>]*>/g, '')); // Strip HTML tags
    //         utterance.lang = 'en-IN'; // English (India)
    //         utterance.rate = 1.0;
    //         utterance.pitch = 1.0;
    //         window.speechSynthesis.speak(utterance);
    //     }
    // }

    // =================================================================
    // --- EVENT LISTENERS & INITIALIZATION ---
    // =================================================================
    chatForm.addEventListener('submit', handleChatSubmit);

    suggestionsContainer?.addEventListener('click', (e) => {
        if (e.target.classList.contains('suggestion')) {
            chatInput.value = e.target.textContent;
            handleChatSubmit(new Event('submit'));
        }
    });

    themeToggle?.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    });

    voiceBtn.addEventListener('click', () => {
        if (recognition && !voiceBtn.classList.contains('recording')) {
            recognition.start();
        }
    });

    // --- Initialize ---
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    setupSpeechRecognition();
    chatInput.focus();
});