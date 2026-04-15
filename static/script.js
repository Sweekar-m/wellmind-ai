(function () {
  'use strict';

  // ===== STATE =====
  let messageCount = 0;
  let startTime = Date.now();
  let isSending = false;
  let currentMood = null;
  let currentSessionId = null;

  // ===== DOM =====
  const chatMessages = document.getElementById('chat-messages');
  const msgInput = document.getElementById('msg-input');
  const btnSend = document.getElementById('btn-send');
  const moodValue = document.getElementById('mood-value');
  const messagesValue = document.getElementById('messages-value');
  const durationValue = document.getElementById('duration-value');
  const welcomeMsg = document.getElementById('welcome-msg');
  const sessionList = document.getElementById('session-list');
  const btnMenu = document.getElementById('btn-menu');
  const chatMenu = document.getElementById('chat-menu');
  const btnNewChatMenu = document.getElementById('btn-new-chat-menu');
  const btnLoadHistory = document.getElementById('btn-load-history');

  // ===== UTIL =====
  function getTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function escapeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function scrollBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function updateStats() {
    messagesValue.textContent = `Messages: ${messageCount}`;

    const sec = Math.floor((Date.now() - startTime) / 1000);
    durationValue.textContent =
      sec < 60 ? `Duration: ${sec}s` : `Duration: ${Math.floor(sec / 60)}m ${sec % 60}s`;

    if (currentMood) {
      const emoji = {
        Stress: '😰',
        Sadness: '😔',
        Neutral: '😌'
      }[currentMood] || '🙂';

      moodValue.textContent = `Mood: ${emoji} ${currentMood}`;
    }
  }

  function addMessage(text, sender) {
    const el = document.createElement('div');
    el.className = `message message--${sender}`;

    el.innerHTML = `
      <div class="message__avatar">${sender === 'user' ? '👤' : '🌿'}</div>
      <div class="message__content">
        <div class="message__text">${escapeHTML(text)}</div>
        <div class="message__time">${getTime()}</div>
      </div>
    `;

    chatMessages.appendChild(el);
    scrollBottom();
  }

  function showTyping() {
    const el = document.createElement('div');
    el.id = 'typing';
    el.className = 'message message--ai';
    el.innerHTML = `
      <div class="message__avatar">🌿</div>
      <div class="message__content">
        <div>Typing...</div>
      </div>
    `;
    chatMessages.appendChild(el);
    scrollBottom();
  }

  function hideTyping() {
    const el = document.getElementById('typing');
    if (el) el.remove();
  }

  function showError(msg) {
    addMessage(`⚠️ ${msg}`, 'ai');
  }

  // ===== SEND MESSAGE =====
  async function sendMessage() {
    const text = msgInput.value.trim();
    if (!text || isSending) return;

    isSending = true;
    btnSend.disabled = true;

    addMessage(text, 'user');
    msgInput.value = '';
    messageCount++;

    showTyping();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: currentSessionId })
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const raw = await res.text();
      if (!raw) throw new Error("Empty response");

      const data = JSON.parse(raw);

      hideTyping();

      if (data.error) {
        showError(data.error);
      } else {
        addMessage(data.response, 'ai');
        currentMood = data.mood;
        messageCount++;
      }

      updateStats();
      loadSidebar();

    } catch (err) {
      console.error("Chat error:", err);
      hideTyping();
      showError("Server error. Try again.");
    }

    isSending = false;
    btnSend.disabled = false;
    msgInput.focus();
  }

  // ===== EVENTS =====
  btnSend?.addEventListener('click', sendMessage);

  msgInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // ===== DROPDOWN MENU =====
  btnMenu?.addEventListener('click', (e) => {
      e.stopPropagation();
      chatMenu.style.display = chatMenu.style.display === 'block' ? 'none' : 'block';
  });

  document.addEventListener('click', () => {
      if (chatMenu) chatMenu.style.display = 'none';
  });

  // ===== SIDEBAR SESSIONS =====
  async function loadSidebar() {
      if (!sessionList) return;
      try {
          const res = await fetch('/api/sessions');
          const data = await res.json();
          if (data.success && data.sessions) {
              sessionList.innerHTML = '';
              data.sessions.forEach(s => {
                  const item = document.createElement('div');
                  item.className = `session-item ${s.id === currentSessionId ? 'active' : ''}`;
                  item.onclick = () => loadSession(s.id);

                  item.innerHTML = `
                      <div class="session-icon">💬</div>
                      <div class="session-details" style="display:flex; flex-direction:column;">
                         <div class="session-title">${escapeHTML(s.title || 'New Chat')}</div>
                         <div class="session-mood" style="font-size:0.75rem; opacity:0.8;">Mood: ${s.mood || 'Neutral'}</div>
                      </div>
                  `;
                  sessionList.appendChild(item);
              });
          }
      } catch (e) { console.error("Sidebar load error", e); }
  }

  // ===== SESSION LOGIC =====
  async function loadSession(sessionId) {
    try {
      const res = await fetch(`/api/session/history?session_id=${sessionId}`);
      const data = await res.json();
      if (data.success && data.data) {
        currentSessionId = sessionId;
        localStorage.setItem('wellmind_session_id', currentSessionId);
        
        chatMessages.innerHTML = '';
        messageCount = 0;
        currentMood = null;
        startTime = Date.now();
        
        if(data.data.messages && data.data.messages.length > 0) {
            data.data.messages.forEach(msg => {
                addMessage(msg.user_message, 'user');
                addMessage(msg.ai_response, 'ai');
                messageCount += 2;
                currentMood = msg.mood;
            });
        } else {
            if (welcomeMsg) chatMessages.appendChild(welcomeMsg);
        }
        
        updateStats();
        loadSidebar();
      } else {
        // If session loading failed, create new
        startNewSession();
      }
    } catch (e) {
        console.error("Failed to load session", e);
        startNewSession();
    }
  }
  
  async function startNewSession() {
      try {
          const res = await fetch('/api/session/new', { method: 'POST' });
          const data = await res.json();
          if (data.success) {
              currentSessionId = data.session_id;
              localStorage.setItem('wellmind_session_id', currentSessionId);
              
              chatMessages.innerHTML = '';
              if (welcomeMsg) chatMessages.appendChild(welcomeMsg);
              messageCount = 0;
              currentMood = null;
              startTime = Date.now();
              updateStats();
              loadSidebar();
          }
      } catch (e) { console.error("Failed to start new session", e); }
  }

  // ===== MENU ACTIONS =====
  btnNewChatMenu?.addEventListener('click', () => {
      startNewSession();
  });

  btnLoadHistory?.addEventListener('click', () => {
      const savedSessionId = localStorage.getItem('wellmind_session_id');
      if (savedSessionId) {
          loadSession(savedSessionId);
      } else {
          startNewSession();
      }
  });

  // ===== INIT =====
  async function initSession() {
      const savedSessionId = localStorage.getItem('wellmind_session_id');
      if (savedSessionId) {
          loadSession(savedSessionId);
      } else {
          startNewSession();
      }
  }
  
  initSession();
  setInterval(updateStats, 1000);
  msgInput?.focus();

})();
