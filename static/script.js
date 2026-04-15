/* ============================================
   WellMindAI — Chat Application Logic
   ============================================ */

(function () {
  'use strict';

  // ========== STATE ==========
  let sessionId = null;
  let messageCount = 0;
  let startTime = Date.now();
  let isSending = false;
  let currentMood = null;

  // ========== DOM ELEMENTS ==========
  const chatMessages = document.getElementById('chat-messages');
  const msgInput = document.getElementById('msg-input');
  const btnSend = document.getElementById('btn-send');
  const headerStatus = document.getElementById('header-status');
  const moodValue = document.getElementById('mood-value');
  const messagesValue = document.getElementById('messages-value');
  const durationValue = document.getElementById('duration-value');
  const userInfo = document.getElementById('user-info');
  const welcomeMsg = document.getElementById('welcome-msg');

  // ========== INITIALIZATION ==========

  async function initializeChat() {
    try {
      // Load user info
      const userRes = await fetch('/api/user/info');
      const userData = await userRes.json();

      if (userData.success && userData.user) {
        userInfo.textContent = `👤 ${userData.user.username}`;
      }

      // Create new session
      const sessionRes = await fetch('/api/session/new', { method: 'POST' });
      const sessionData = await sessionRes.json();

      if (sessionData.success) {
        sessionId = sessionData.session_id;
        console.log(`Session started: ${sessionId}`);
      } else {
        showError('Failed to create session');
      }
    } catch (error) {
      console.error('Initialization error:', error);
      showError('Failed to initialize chat');
    }
  }

  // ========== UTILITIES ==========

  function getTimeString() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function escapeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    });
  }

  function updateStats() {
    // Update message count
    messagesValue.textContent = `Messages: ${messageCount}`;

    // Update duration
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    if (elapsed < 60) {
      durationValue.textContent = `Duration: ${elapsed}s`;
    } else {
      const minutes = Math.floor(elapsed / 60);
      const seconds = elapsed % 60;
      durationValue.textContent = `Duration: ${minutes}m ${seconds}s`;
    }

    // Update mood
    if (currentMood) {
      const moodEmoji = {
        'Stress': '😰',
        'Sadness': '😔',
        'Neutral': '😊'
      }[currentMood] || '😊';

      moodValue.textContent = `Mood: ${moodEmoji} ${currentMood}`;
    }
  }

  function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message message--ai';
    errorDiv.innerHTML = `
      <div class="message__avatar">🌿</div>
      <div class="message__content">
        <div class="message__text" style="background: rgba(220, 38, 38, 0.1); color: #dc2626;">
          ⚠️ ${escapeHTML(message)}
        </div>
      </div>
    `;
    chatMessages.appendChild(errorDiv);
    scrollToBottom();
  }

  function removeWelcome() {
    if (welcomeMsg) {
      welcomeMsg.style.opacity = '0';
      welcomeMsg.style.transform = 'translateY(-10px)';
      welcomeMsg.style.transition = 'all 0.3s ease';
      setTimeout(() => welcomeMsg?.remove(), 300);
    }
  }

  // ========== MESSAGE HANDLING ==========

  function addMessage(text, isUser, mood = null) {
    const messageEl = document.createElement('div');
    messageEl.className = `message message--${isUser ? 'user' : 'ai'}`;

    const avatar = isUser ? '👤' : '🌿';
    const avatarClass = isUser ? 'message--user' : 'message--ai';

    messageEl.innerHTML = `
      <div class="message__avatar">${avatar}</div>
      <div class="message__content">
        <div class="message__text">${escapeHTML(text)}</div>
        <div class="message__time">${getTimeString()}</div>
      </div>
    `;

    chatMessages.appendChild(messageEl);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const typingEl = document.createElement('div');
    typingEl.className = 'message message--ai';
    typingEl.id = 'typing-indicator';
    typingEl.innerHTML = `
      <div class="message__avatar">🌿</div>
      <div class="message__content">
        <div class="typing-bubble">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    `;

    chatMessages.appendChild(typingEl);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    const typing = document.getElementById('typing-indicator');
    if (typing) {
      typing.style.opacity = '0';
      typing.style.transition = 'opacity 0.2s ease';
      setTimeout(() => typing.remove(), 200);
    }
  }

  // ========== SEND MESSAGE ==========

  async function sendMessage() {
    const message = msgInput.value.trim();

    if (!message || isSending || !sessionId) {
      return;
    }

    isSending = true;
    msgInput.disabled = true;
    btnSend.disabled = true;

    try {
      // Add user message to UI
      removeWelcome();
      addMessage(message, true);
      msgInput.value = '';
      msgInput.focus();
      messageCount++;

      // Show typing indicator
      showTypingIndicator();

      // Send to backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        })
      });

      removeTypingIndicator();

      if (!response.ok) {
        const errorData = await response.json();
        showError(errorData.response || 'Error sending message');
        isSending = false;
        msgInput.disabled = false;
        btnSend.disabled = false;
        return;
      }

      const data = await response.json();

      if (!data.success) {
        showError(data.response || 'Failed to get response');
      } else {
        // Add AI response
        addMessage(data.response, false);
        currentMood = data.mood;
        messageCount++;
      }

      updateStats();
    } catch (error) {
      console.error('Send error:', error);
      removeTypingIndicator();
      showError('Network error. Please check your connection.');
    } finally {
      isSending = false;
      msgInput.disabled = false;
      btnSend.disabled = false;
      msgInput.focus();
    }
  }

  // ========== EVENT LISTENERS ==========

  btnSend.addEventListener('click', sendMessage);

  msgInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Update stats every second
  setInterval(updateStats, 1000);

  // ========== STARTUP ==========
  document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
    updateStats();
  });

  // If DOM is already loaded
  if (document.readyState === 'loading') {
    console.log('Waiting for DOM...');
  } else {
    initializeChat();
    updateStats();
  }
})();


// --- Add a message bubble ---
function addMessage(text, sender) {
  const time = getTimeString();
  const isUser = sender === 'user';

  const row = document.createElement('div');
  row.className = `message-row message-row--${sender}`;

  const avatar = document.createElement('div');
  avatar.className = `message-avatar message-avatar--${sender}`;
  avatar.textContent = isUser ? '🙂' : '🌿';

  const contentWrap = document.createElement('div');

  const bubble = document.createElement('div');
  bubble.className = `message-bubble message-bubble--${sender}`;
  bubble.innerHTML = escapeHTML(text);

  const timeEl = document.createElement('div');
  timeEl.className = 'message-time';
  timeEl.textContent = time;

  contentWrap.appendChild(bubble);
  contentWrap.appendChild(timeEl);

  row.appendChild(avatar);
  row.appendChild(contentWrap);

  chatMessages.appendChild(row);
  scrollToBottom();
}

// --- Typing indicator ---
function showTyping() {
  headerStatus.innerHTML = '<span style="color: var(--color-text-muted);">typing...</span>';

  const typingEl = document.createElement('div');
  typingEl.className = 'typing-indicator';
  typingEl.id = 'typing-indicator';

  typingEl.innerHTML = `
      <div class="message-avatar message-avatar--ai">🌿</div>
      <div class="typing-bubble">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    `;

  chatMessages.appendChild(typingEl);
  scrollToBottom();
}

function hideTyping() {
  headerStatus.innerHTML = '● Online';
  headerStatus.style.color = '#4ade80';
  const el = document.getElementById('typing-indicator');
  if (el) {
    el.style.transition = 'opacity 0.2s ease';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 200);
  }
}

// --- Update stats chips ---
function updateStats(data) {
  if (data.mood) {
    const moodEmoji = getMoodEmoji(data.mood);
    moodValue.textContent = `Mood: ${moodEmoji} ${capitalize(data.mood)}`;
  }

  if (data.session) {
    messagesValue.textContent = `Messages: ${data.session.messages}`;
    durationValue.textContent = `Duration: ${formatDuration(data.session.duration_sec)}`;
  }
}

function getMoodEmoji(mood) {
  const map = {
    'happy': '😊', 'joy': '😄', 'neutral': '😌', 'calm': '🧘',
    'sad': '😢', 'sadness': '😢', 'stressed': '😰', 'stress': '😰',
    'angry': '😠', 'anxious': '😟', 'anxiety': '😟',
    'fear': '😨', 'love': '❤️', 'surprise': '😲'
  };
  return map[mood.toLowerCase()] || '🙂';
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function formatDuration(sec) {
  if (sec < 60) return `${sec}s`;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return s > 0 ? `${m}m ${s}s` : `${m}m`;
}

// --- Send message ---
async function sendMessage() {
  const text = msgInput.value.trim();
  if (!text || isSending) return;

  isSending = true;
  btnSend.disabled = true;

  // Hide welcome on first message
  hideWelcome();

  // Show user message
  addMessage(text, 'user');
  messageCount++;
  msgInput.value = '';

  // Show typing
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    const data = await res.json();

    // Small delay for natural feel
    await new Promise(r => setTimeout(r, 400));

    hideTyping();

    if (data.error) {
      addMessage('Sorry, something went wrong. Please try again.', 'ai');
    } else {
      addMessage(data.reply, 'ai');
      updateStats(data);
    }

  } catch (err) {
    console.error('Chat error:', err);
    hideTyping();
    addMessage('Unable to connect. Please check your connection and try again.', 'ai');
  }

  isSending = false;
  btnSend.disabled = false;
  msgInput.focus();
}

// --- Event listeners ---
btnSend.addEventListener('click', sendMessage);

msgInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Focus input on load
msgInput.focus();
