/**
 * Gemini-Style Chat Interface
 * A modern AI chat application with theme switching, chat history, and dynamic user profiles
 */

// ===== Configuration =====
const CONFIG = {
  // Replace these with your actual API endpoints
  API_ENDPOINTS: {
    USER_PROFILE: '/api/user/profile', // GET - Returns { name, avatar }
    CHAT_SEND: '/api/chat/send',       // POST - Sends message, returns AI response
    CHAT_HISTORY: '/api/chat/history'  // GET - Returns array of chat sessions
  },
  
  // Local storage keys
  STORAGE_KEYS: {
    THEME: 'drishti-theme',
    CHATS: 'drishti-chats',
    CURRENT_CHAT: 'drishti-current-chat'
  },
  
  // Default user (placeholder)
  DEFAULT_USER: {
    name: 'User',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'
  }
};

// ===== State Management =====
const state = {
  user: { ...CONFIG.DEFAULT_USER },
  currentChatId: null,
  chats: [],
  isTyping: false,
  sidebarOpen: true
};

// ===== DOM Elements =====
const elements = {
  sidebar: document.getElementById('sidebar'),
  sidebarToggle: document.getElementById('sidebarToggle'),
  themeSwitcher: document.getElementById('themeSwitcher'),
  userProfile: document.getElementById('userProfile'),
  profileAvatar: document.getElementById('profileAvatar'),
  userName: document.getElementById('userName'),
  welcomeScreen: document.getElementById('welcomeScreen'),
  messagesContainer: document.getElementById('messagesContainer'),
  chatInput: document.getElementById('chatInput'),
  charCount: document.getElementById('charCount'),
  sendBtn: document.getElementById('sendBtn'),
  newChatBtn: document.getElementById('newChatBtn'),
  chatHistory: document.getElementById('chatHistory'),
  scrollToBottom: document.getElementById('scrollToBottom'),
  chatArea: document.getElementById('chatArea'),
  toolsBtn: document.getElementById('toolsBtn'),
  quickActions: document.querySelectorAll('.quick-action-btn'),
  sectionHeaders: document.querySelectorAll('.section-header')
};

// ===== Theme Management =====
const ThemeManager = {
  init() {
    const savedTheme = localStorage.getItem(CONFIG.STORAGE_KEYS.THEME) || 'dark';
    this.setTheme(savedTheme);
    this.bindEvents();
  },
  
  setTheme(theme) {
    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
      document.documentElement.setAttribute('data-theme', theme);
    }
    
    localStorage.setItem(CONFIG.STORAGE_KEYS.THEME, theme);
    this.updateActiveButton(theme);
  },
  
  updateActiveButton(theme) {
    elements.themeSwitcher.querySelectorAll('.theme-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.theme === theme);
    });
  },
  
  bindEvents() {
    elements.themeSwitcher.addEventListener('click', (e) => {
      const btn = e.target.closest('.theme-btn');
      if (btn) {
        this.setTheme(btn.dataset.theme);
      }
    });
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      const currentTheme = localStorage.getItem(CONFIG.STORAGE_KEYS.THEME);
      if (currentTheme === 'system') {
        this.setTheme('system');
      }
    });
  }
};

// ===== User Profile Management =====
const UserManager = {
  async init() {
    await this.fetchUserProfile();
    this.updateUI();
  },
  
  async fetchUserProfile() {
    try {
      // Replace with actual API call
      const response = await fetch(CONFIG.API_ENDPOINTS.USER_PROFILE);
      if (response.ok) {
        const data = await response.json();
        state.user = { ...CONFIG.DEFAULT_USER, ...data };
      }
    } catch (error) {
      console.log('Using default user profile (API not available)');
      // Use mock data for demo
      state.user = {
        name: 'Alex',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=alex'
      };
    }
  },
  
  updateUI() {
    elements.userName.textContent = state.user.name;
    elements.profileAvatar.src = state.user.avatar;
    elements.profileAvatar.alt = `${state.user.name}'s profile`;
  }
};

// ===== Chat Management =====
const ChatManager = {
  init() {
    this.loadChats();
    this.renderChatHistory();
    this.bindEvents();
  },
  
  loadChats() {
    const saved = localStorage.getItem(CONFIG.STORAGE_KEYS.CHATS);
    state.chats = saved ? JSON.parse(saved) : [];
    state.currentChatId = localStorage.getItem(CONFIG.STORAGE_KEYS.CURRENT_CHAT);
  },
  
  saveChats() {
    localStorage.setItem(CONFIG.STORAGE_KEYS.CHATS, JSON.stringify(state.chats));
    if (state.currentChatId) {
      localStorage.setItem(CONFIG.STORAGE_KEYS.CURRENT_CHAT, state.currentChatId);
    }
  },
  
  createNewChat() {
    const chat = {
      id: Date.now().toString(),
      title: 'New chat',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    state.chats.unshift(chat);
    state.currentChatId = chat.id;
    this.saveChats();
    this.renderChatHistory();
    this.showChat(chat.id);
    
    return chat;
  },
  
  getCurrentChat() {
    return state.chats.find(c => c.id === state.currentChatId);
  },
  
  updateChatTitle(chatId, message) {
    const chat = state.chats.find(c => c.id === chatId);
    if (chat && chat.title === 'New chat') {
      chat.title = message.substring(0, 50) + (message.length > 50 ? '...' : '');
      this.saveChats();
      this.renderChatHistory();
    }
  },
  
  addMessage(chatId, role, content) {
    const chat = state.chats.find(c => c.id === chatId);
    if (chat) {
      chat.messages.push({
        id: Date.now().toString(),
        role,
        content,
        timestamp: new Date().toISOString()
      });
      chat.updatedAt = new Date().toISOString();
      this.saveChats();
    }
  },
  
  showChat(chatId) {
    state.currentChatId = chatId;
    this.saveChats();
    
    const chat = this.getCurrentChat();
    if (chat && chat.messages.length > 0) {
      elements.welcomeScreen.style.display = 'none';
      elements.messagesContainer.classList.add('active');
      this.renderMessages(chat.messages);
    } else {
      elements.welcomeScreen.style.display = 'flex';
      elements.messagesContainer.classList.remove('active');
      elements.messagesContainer.innerHTML = '';
    }
    
    this.updateActiveChat();
  },
  
  renderMessages(messages) {
    elements.messagesContainer.innerHTML = messages.map(msg => this.createMessageHTML(msg)).join('');
    this.scrollToBottom();
  },
  
  createMessageHTML(message) {
    const isAI = message.role === 'assistant';
    const time = new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    return `
      <div class="message ${message.role}">
        <div class="message-avatar ${isAI ? 'ai' : 'user'}">
          ${!isAI ? `<img src="${state.user.avatar}" alt="User" style="width:100%;height:100%;border-radius:50%;">` : ''}
        </div>
        <div class="message-content">
          <div class="message-header">
            <span class="message-sender">${isAI ? 'Gemini' : state.user.name}</span>
            <span class="message-time">${time}</span>
          </div>
          <div class="message-text">${this.formatMessage(message.content)}</div>
          <div class="message-actions">
            <button class="message-action-btn copy-btn" title="Copy" aria-label="Copy message">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
            </button>
            ${isAI ? `
              <button class="message-action-btn" title="Like" aria-label="Like response">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                </svg>
              </button>
              <button class="message-action-btn" title="Dislike" aria-label="Dislike response">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path>
                </svg>
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    `;
  },
  
  formatMessage(content) {
    // Basic markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  },
  
  appendMessage(message) {
    const html = this.createMessageHTML(message);
    elements.messagesContainer.insertAdjacentHTML('beforeend', html);
    this.scrollToBottom();
  },
  
  showTypingIndicator() {
    state.isTyping = true;
    const html = `
      <div class="message assistant typing-message">
        <div class="message-avatar ai"></div>
        <div class="message-content">
          <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      </div>
    `;
    elements.messagesContainer.insertAdjacentHTML('beforeend', html);
    this.scrollToBottom();
  },
  
  hideTypingIndicator() {
    state.isTyping = false;
    const typingMessage = elements.messagesContainer.querySelector('.typing-message');
    if (typingMessage) {
      typingMessage.remove();
    }
  },
  
  scrollToBottom() {
    elements.chatArea.scrollTo({
      top: elements.chatArea.scrollHeight,
      behavior: 'smooth'
    });
  },
  
  renderChatHistory() {
    if (state.chats.length === 0) {
      elements.chatHistory.innerHTML = '<p class="empty-state" style="padding:12px;color:var(--text-muted);font-size:13px;">No chats yet</p>';
      return;
    }
    
    elements.chatHistory.innerHTML = state.chats.map(chat => {
      const time = new Date(chat.updatedAt).toLocaleDateString();
      return `
        <div class="chat-item ${chat.id === state.currentChatId ? 'active' : ''}" data-chat-id="${chat.id}">
          <svg class="chat-item-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <span class="chat-item-title">${chat.title}</span>
          <span class="chat-item-time">${time}</span>
        </div>
      `;
    }).join('');
  },
  
  updateActiveChat() {
    elements.chatHistory.querySelectorAll('.chat-item').forEach(item => {
      item.classList.toggle('active', item.dataset.chatId === state.currentChatId);
    });
  },
  
  bindEvents() {
    // New chat button
    elements.newChatBtn.addEventListener('click', () => {
      this.createNewChat();
    });
    
    // Chat history click
    elements.chatHistory.addEventListener('click', (e) => {
      const chatItem = e.target.closest('.chat-item');
      if (chatItem) {
        this.showChat(chatItem.dataset.chatId);
      }
    });
    
    // Copy message
    elements.messagesContainer.addEventListener('click', (e) => {
      const copyBtn = e.target.closest('.copy-btn');
      if (copyBtn) {
        const messageText = copyBtn.closest('.message-content').querySelector('.message-text').textContent;
        navigator.clipboard.writeText(messageText);
        // Visual feedback
        copyBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        `;
        setTimeout(() => {
          copyBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          `;
        }, 2000);
      }
    });
  }
};

// ===== AI Communication =====
const AIManager = {
  async sendMessage(content) {
    let chat = ChatManager.getCurrentChat();
    
    if (!chat) {
      chat = ChatManager.createNewChat();
    }
    
    // Show chat interface
    elements.welcomeScreen.style.display = 'none';
    elements.messagesContainer.classList.add('active');
    
    // Add user message
    ChatManager.addMessage(chat.id, 'user', content);
    ChatManager.appendMessage({
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    });
    
    // Update chat title if first message
    ChatManager.updateChatTitle(chat.id, content);
    
    // Show typing indicator
    ChatManager.showTypingIndicator();
    
    try {
      const response = await this.callAI(content);
      
      // Hide typing indicator
      ChatManager.hideTypingIndicator();
      
      // Add AI response
      ChatManager.addMessage(chat.id, 'assistant', response);
      ChatManager.appendMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      ChatManager.hideTypingIndicator();
      console.error('AI Error:', error);
      
      // Show error message
      const errorMsg = 'Sorry, I encountered an error. Please try again.';
      ChatManager.addMessage(chat.id, 'assistant', errorMsg);
      ChatManager.appendMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content: errorMsg,
        timestamp: new Date().toISOString()
      });
    }
  },
  
  async callAI(message) {
    try {
      // Replace with your actual AI API endpoint
      const response = await fetch(CONFIG.API_ENDPOINTS.CHAT_SEND, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.response || data.message || data.content;
      }
      throw new Error('API request failed');
    } catch (error) {
      // Mock response for demo
      console.log('Using mock AI response (API not available)');
      await this.simulateDelay(1000 + Math.random() * 1000);
      return this.getMockResponse(message);
    }
  },
  
  simulateDelay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  },
  
  getMockResponse(message) {
    const responses = [
      `I understand you're asking about "${message.substring(0, 30)}...". This is a demo response since the AI backend isn't connected yet.\n\nTo connect your own AI backend, update the **CONFIG.API_ENDPOINTS.CHAT_SEND** endpoint in app.js with your API URL.`,
      `That's an interesting question! In a real implementation, I would process your message through your AI backend.\n\n**Quick tip:** The API endpoint expects a POST request with a JSON body containing a "message" field.`,
      `Great question! This is a placeholder response.\n\nYour message was: *"${message}"*\n\nConnect your AI backend to get real responses.`
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }
};

// ===== Input Management =====
const InputManager = {
  init() {
    this.bindEvents();
  },
  
  bindEvents() {
    // Input change
    elements.chatInput.addEventListener('input', () => {
      this.autoResize();
      this.updateCharCount();
      this.updateSendButton();
    });
    
    // Send on Enter (Ctrl/Cmd + Enter for new line)
    elements.chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.send();
      }
    });
    
    // Send button click
    elements.sendBtn.addEventListener('click', () => {
      this.send();
    });
    
    // Quick actions
    elements.quickActions.forEach(btn => {
      btn.addEventListener('click', () => {
        const prompt = btn.dataset.prompt;
        if (prompt) {
          elements.chatInput.value = prompt;
          this.autoResize();
          this.updateCharCount();
          this.updateSendButton();
          elements.chatInput.focus();
        }
      });
    });
  },
  
  autoResize() {
    elements.chatInput.style.height = 'auto';
    elements.chatInput.style.height = Math.min(elements.chatInput.scrollHeight, 200) + 'px';
  },
  
  updateCharCount() {
    elements.charCount.textContent = elements.chatInput.value.length;
  },
  
  updateSendButton() {
    const hasContent = elements.chatInput.value.trim().length > 0;
    elements.sendBtn.disabled = !hasContent;
    elements.sendBtn.classList.toggle('pulse', hasContent);
  },
  
  send() {
    const content = elements.chatInput.value.trim();
    if (content && !state.isTyping) {
      AIManager.sendMessage(content);
      elements.chatInput.value = '';
      this.autoResize();
      this.updateCharCount();
      this.updateSendButton();
    }
  }
};

// ===== UI Utilities =====
const UIManager = {
  init() {
    this.bindSidebarToggle();
    this.bindSectionToggles();
    this.bindToolsDropdown();
    this.bindScrollToBottom();
  },
  
  bindSidebarToggle() {
    elements.sidebarToggle.addEventListener('click', () => {
      state.sidebarOpen = !state.sidebarOpen;
      elements.sidebar.classList.toggle('collapsed', !state.sidebarOpen);
    });
  },
  
  bindSectionToggles() {
    elements.sectionHeaders.forEach(header => {
      header.addEventListener('click', () => {
        const section = header.dataset.section;
        const content = document.getElementById(`${section}-content`);
        const isCollapsed = content.classList.toggle('collapsed');
        header.setAttribute('aria-expanded', !isCollapsed);
      });
    });
  },
  
  bindToolsDropdown() {
    const dropdown = elements.toolsBtn.closest('.tools-dropdown');
    
    elements.toolsBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('open');
    });
    
    document.addEventListener('click', () => {
      dropdown.classList.remove('open');
    });
  },
  
  bindScrollToBottom() {
    elements.chatArea.addEventListener('scroll', () => {
      const { scrollTop, scrollHeight, clientHeight } = elements.chatArea;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 200;
      elements.scrollToBottom.classList.toggle('visible', !isNearBottom);
    });
    
    elements.scrollToBottom.addEventListener('click', () => {
      ChatManager.scrollToBottom();
    });
  }
};

// ===== Keyboard Shortcuts =====
const KeyboardManager = {
  init() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K: Focus search/input
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        elements.chatInput.focus();
      }
      
      // Ctrl/Cmd + B: Toggle sidebar
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        elements.sidebarToggle.click();
      }
      
      // Ctrl/Cmd + N: New chat
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        ChatManager.createNewChat();
      }
      
      // Escape: Close dropdowns
      if (e.key === 'Escape') {
        document.querySelectorAll('.open').forEach(el => el.classList.remove('open'));
      }
    });
  }
};

// ===== Initialize Application =====
async function init() {
  ThemeManager.init();
  await UserManager.init();
  ChatManager.init();
  InputManager.init();
  UIManager.init();
  KeyboardManager.init();
  
  console.log('Drishti AI Chat Interface initialized');
  console.log('Keyboard shortcuts:');
  console.log('  Ctrl/Cmd + K: Focus input');
  console.log('  Ctrl/Cmd + B: Toggle sidebar');
  console.log('  Ctrl/Cmd + N: New chat');
}

// Start the app
document.addEventListener('DOMContentLoaded', init);
