// ============================================
// Upload Page - JavaScript
// ============================================

// ============================================
// Navigation: Handle redirect to ADHD/Deaf if coming from signup/login
// ============================================

/**
 * Check if we should redirect to ADHD or Deaf page
 * This is called when redirected from signup/login for ADHD or Deaf modes
 * HOWEVER: We should NOT auto-redirect on page load because we need to capture the upload!
 * The redirect will happen AFTER form submission
 */
document.addEventListener('DOMContentLoaded', () => {
    const nextMode = sessionStorage.getItem('nextMode');
    console.log('Upload.html loaded, nextMode from sessionStorage:', nextMode);

    if (nextMode) {
        // DO NOT redirect immediately - we need the user to upload/enter data first
        // The sessionStorage value will be used after form submission
        console.log('User came from signup/login with mode:', nextMode);
    } else {
        console.log('No nextMode found, user may have navigated directly or is continuing a session');
    }
});

// State Management
const state = {
    selectedFile: null,
    currentChatId: null,
    sessionId: null
};

// DOM Elements
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const selectedFileDiv = document.getElementById('selectedFile');
const fileNameSpan = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFileBtn');
const promptInput = document.getElementById('promptInput');
const submitBtn = document.getElementById('submitBtn');
const chatsList = document.getElementById('chatsList');

// ============================================
// File Upload Handling
// ============================================

/**
 * Triggers file input click when upload button is clicked
 */
uploadBtn.addEventListener('click', () => {
    fileInput.click();
});

/**
 * Handles file selection
 */
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        state.selectedFile = file;
        displaySelectedFile(file);
    }
});

/**
 * Displays the selected file name
 */
function displaySelectedFile(file) {
    fileNameSpan.textContent = file.name;
    selectedFileDiv.style.display = 'flex';
}

/**
 * Removes the selected file
 */
removeFileBtn.addEventListener('click', () => {
    state.selectedFile = null;
    fileInput.value = '';
    selectedFileDiv.style.display = 'none';
    fileNameSpan.textContent = '';
});

// ============================================
// Prompt Input Handling
// ============================================

/**
 * Auto-resize textarea as user types
 */
promptInput.addEventListener('input', () => {
    promptInput.style.height = 'auto';
    promptInput.style.height = promptInput.scrollHeight + 'px';

    // Enable/disable submit button based on input
    updateSubmitButton();
});

/**
 * Handle Enter key to submit (Shift+Enter for new line)
 */
promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitPrompt();
    }
});

/**
 * Updates submit button state
 */
function updateSubmitButton() {
    const hasContent = promptInput.value.trim().length > 0 || state.selectedFile !== null;
    submitBtn.disabled = !hasContent;
}

// ============================================
// Submit Handling
// ============================================

/**
 * Handles submit button click
 */
submitBtn.addEventListener('click', submitPrompt);

/**
 * Submits the prompt and/or file to backend
 */
async function submitPrompt() {
    const prompt = promptInput.value.trim();

    // Validate input
    if (!prompt && !state.selectedFile) {
        console.log('No prompt or file to submit');
        return;
    }

    // Check authentication
    if (!requireAuth()) {
        return;
    }

    try {
        // Disable submit button during processing
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<svg class="submit-icon spinning" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/></svg>';

        const userId = getUserId();
        if (!userId) {
            throw new Error('User not authenticated. Please login.');
        }

        // Get or create session
        if (!state.sessionId) {
            const session = await startSession();
            state.sessionId = session.id;
            setSessionId(session.id);
        }

        console.log('Submitting:', {
            prompt: prompt,
            file: state.selectedFile ? state.selectedFile.name : 'No file',
            sessionId: state.sessionId
        });

        // Show processing message
        submitBtn.innerHTML = '⏳ Uploading...';

        // Handle file upload if file is selected
        if (state.selectedFile) {
            const formData = new FormData();
            formData.append('file', state.selectedFile);
            formData.append('user_id', userId);
            formData.append('session_id', state.sessionId);
            if (prompt) {
                formData.append('description', prompt);
            }

            // Upload file to context endpoint
            const uploadResponse = await apiCall(
                CONFIG.ENDPOINTS.CONTEXT_UPLOAD,
                {
                    method: 'POST',
                    body: formData
                },
                true // useFormData = true
            );

            console.log('File uploaded:', uploadResponse);
            submitBtn.innerHTML = '✓ File uploaded';
        }

        // If there's a prompt, just store it for the ADHD/Deaf page to load
        if (prompt) {
            // Store the topic/prompt for the learning page
            localStorage.setItem('current_topic', prompt);
            console.log('Topic stored for learning page:', prompt);
        }

        // Show preparing message
        submitBtn.innerHTML = '🔄 Preparing your learning experience...';

        // Wait for data to reach the AI model (buffer time)
        // This ensures the uploaded file is available when the next page loads
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Clear form
        clearForm();

        // Final message before redirect
        submitBtn.innerHTML = '🚀 Ready! Redirecting...';

        // Small delay to show the message
        await new Promise(resolve => setTimeout(resolve, 500));

        // Redirect based on user mode (the ADHD/Deaf page will load content)
        const userMode = localStorage.getItem('user_mode') || 'adhd';

        if (userMode === 'adhd') {
            window.location.href = '/Html/ADHD.html';
        } else if (userMode === 'deaf') {
            window.location.href = '/Html/Deaf.html';
        } else if (userMode === 'blind') {
            window.location.href = '/Html/Blind.html';
        } else {
            // Default fallback
            window.location.href = '/Html/ADHD.html';
        }

    } catch (error) {
        console.error('Error submitting:', error);
        alert(`Error: ${error.message}`);
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<svg class="submit-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" /></svg>';
        updateSubmitButton();
    }
}

/**
 * Get user info from backend (for interest_field, etc.)
 * TODO: Create a user info endpoint or use existing user endpoint
 */
async function getUserInfo() {
    // For now, return default values
    // In production, this would fetch from /users/{user_id}
    return {
        interest_field: 'general',
        preferred_language: 'en'
    };
}

/**
 * Clears the form after submission
 */
function clearForm() {
    promptInput.value = '';
    promptInput.style.height = 'auto';
    state.selectedFile = null;
    fileInput.value = '';
    selectedFileDiv.style.display = 'none';
    fileNameSpan.textContent = '';
    updateSubmitButton();
}

// ============================================
// Past Chats Management
// ============================================

/**
 * Fetches past chats from backend
 * 
 * TODO: Backend Integration
 * Endpoint: GET /api/chats
 * Query: user_id (from auth)
 * Returns: {
 *   chats: [
 *     {
 *       id: string,
 *       title: string,
 *       timestamp: string,
 *       preview: string
 *     }
 *   ]
 * }
 */
async function loadPastChats() {
    try {
        // TODO: Replace with actual API call
        // const response = await fetch('/api/chats?user_id=current_user_id');
        // const data = await response.json();

        // For now, no chats to display
        const data = { chats: [] };

        if (data.chats && data.chats.length > 0) {
            displayChats(data.chats);
        }

    } catch (error) {
        console.error('Error loading chats:', error);
    }
}

/**
 * Displays chats in the sidebar
 */
function displayChats(chats) {
    chatsList.innerHTML = '';

    chats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        chatItem.dataset.chatId = chat.id;

        chatItem.innerHTML = `
            <div class="chat-title">${chat.title}</div>
            <div class="chat-timestamp">${formatTimestamp(chat.timestamp)}</div>
        `;

        chatItem.addEventListener('click', () => loadChat(chat.id));
        chatsList.appendChild(chatItem);
    });
}

/**
 * Loads a specific chat
 * 
 * TODO: Backend Integration
 * Endpoint: GET /api/chats/:chatId
 * Returns: {
 *   messages: [
 *     {
 *       role: 'user' | 'assistant',
 *       content: string,
 *       timestamp: string
 *     }
 *   ]
 * }
 */
async function loadChat(chatId) {
    try {
        console.log('Loading chat:', chatId);
        state.currentChatId = chatId;

        // TODO: Replace with actual API call
        // const response = await fetch(`/api/chats/${chatId}`);
        // const data = await response.json();

        // TODO: Display chat messages in UI
        // TODO: Navigate to chat view

    } catch (error) {
        console.error('Error loading chat:', error);
    }
}

/**
 * Formats timestamp for display
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    // Less than 24 hours
    if (diff < 86400000) {
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    // Less than 7 days
    else if (diff < 604800000) {
        return date.toLocaleDateString('en-US', { weekday: 'short' });
    }
    // Older
    else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
}

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Upload page loaded');

    // Initialize submit button state
    updateSubmitButton();

    // Start a new session when page loads
    try {
        const session = await startSession();
        state.sessionId = session.id;
        setSessionId(session.id);
        console.log('Session started:', session.id);
    } catch (error) {
        console.error('Error starting session:', error);
    }

    // Load past chats (if endpoint exists)
    // loadPastChats();
});

// ============================================
// Backend Integration Guide for Developers
// ============================================

/*
BACKEND ENDPOINTS NEEDED:

1. POST /api/upload
   - Handles file upload and prompt submission
   - Request: FormData with file (optional), prompt, user_id
   - Response: { success, chat_id, response, message }

2. GET /api/chats
   - Fetches user's past chats
   - Query: user_id
   - Response: { chats: [{ id, title, timestamp, preview }] }

3. GET /api/chats/:chatId
   - Fetches messages for a specific chat
   - Response: { messages: [{ role, content, timestamp }] }

NOTES:
- All TODO comments mark places where backend integration is needed
- File upload supports images, PDFs, and documents
- User authentication should provide user_id
- Replace placeholder responses with actual API calls
*/
