(function () {
  'use strict';

  // ===== STATE =====
  let messageCount = 0;
  let startTime = Date.now();
  let isSending = false;
  let currentMood = null;

  // ===== DOM =====
  const chatMessages = document.getElementById('chat-messages');
  const msgInput = document.getElementById('msg-input');
  const btnSend = document.getElementById('btn-send');
  const moodValue = document.getElementById('mood-value');
  const messagesValue = document.getElementById('messages-value');
  const durationValue = document.getElementById('duration-value');

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
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
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
        addMessage(data.reply, 'ai');
        currentMood = data.mood;
        messageCount++;
      }

      updateStats();

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

  // ===== INIT =====
  setInterval(updateStats, 1000);
  msgInput?.focus();

})();
