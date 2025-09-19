document.addEventListener('DOMContentLoaded', () => {
  // --- DOM ELEMENTS ---
  const chatWindow = document.getElementById('chat-window');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-button');
  const voiceBtn = document.getElementById('voice-button');
  const suggestionsContainer = document.querySelector('.suggestions');
  const welcomeMessage = document.querySelector('.welcome-message');
  const themeToggle = document.querySelector('.theme-toggle');
  const themeText = document.querySelector('.theme-text');

  // --- GEMINI API CONFIG ---
  const apiKey = "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU";
  const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;

  const systemInstruction = {
    parts: [{ text: "You are an expert agricultural assistant named KrishiBot. Provide detailed, accurate and helpful responses about farming, crops, weather, soil health, pest control, and sustainable agriculture practices. Format answers in clear paragraphs. Politely decline if outside agriculture." }]
  };

  let history = [];

  // --- THEME ---
  const applyTheme = (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    if (themeText) themeText.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
  };

  themeToggle?.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
  });

  applyTheme(localStorage.getItem('theme') || 'light');

  // --- CHAT HELPERS ---
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  function formatResponse(text) {
    return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>');
  }
  function displayMessage(content, sender) {
    if (welcomeMessage) welcomeMessage.remove();
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const name = sender === 'user' ? 'You' : 'Krishi-Saathi';
    msg.innerHTML = `
      <div class="message-header"><i class="fas fa-${sender === 'user' ? 'user-alt' : 'robot'}"></i> <span>${name}</span></div>
      <div class="message-text">${formatResponse(escapeHtml(content))}</div>
      <div class="timestamp">${time}</div>
    `;
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    if (sender === 'bot') speak(content); // <-- text-to-speech
  }
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

  // --- HANDLE SUGGESTIONS ---
  suggestionsContainer?.addEventListener('click', (e) => {
    if (e.target.classList.contains('suggestion')) {
      chatInput.value = e.target.textContent;
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  // --- CHAT SUBMIT ---
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = chatInput.value.trim();
    if (!input) return;
    displayMessage(input, 'user');
    chatInput.value = '';
    const typing = showTyping();
    toggleInput(true);

    history.push({ role: "user", parts: [{ text: input }] });

    try {
      if (!apiKey) throw new Error("API_KEY_MISSING");
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: history,
          systemInstruction,
          generationConfig: { temperature: 0.7, maxOutputTokens: 800 }
        })
      });
      if (!response.ok) throw new Error(`HTTP error ${response.status}`);
      const data = await response.json();
      const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || "Sorry, I couldn't process that.";
      displayMessage(reply, 'bot');
      history.push({ role: "model", parts: [{ text: reply }] });
    } catch (err) {
      console.error(err);
      displayMessage("⚠️ Error: Unable to connect right now.", 'bot');
    } finally {
      typing.remove();
      toggleInput(false);
    }
  });

  // --- VOICE RECOGNITION (Speech-to-Text) ---
  let recognition;
  if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => voiceBtn.classList.add('recording');
    recognition.onend = () => voiceBtn.classList.remove('recording');
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      chatInput.value = transcript;
      chatForm.dispatchEvent(new Event('submit'));
    };
  }

  voiceBtn.addEventListener('click', () => {
    if (recognition) recognition.start();
    else alert("Speech recognition not supported in this browser.");
  });

  // --- TEXT TO SPEECH ---
  function speak(text) {
    if ('speechSynthesis' in window) {
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = 'en-IN';
      utter.rate = 1;
      window.speechSynthesis.speak(utter);
    }
  }

  chatInput.focus();
});
