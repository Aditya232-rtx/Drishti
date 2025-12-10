/**
 * Chat Application - Main Logic
 * Handles file uploads, message display, and chat interactions
 */

// State management
const chatState = {
    uploadedFile: null,
    messages: []
};

// DOM Elements
const elements = {
    uploadBtn: null,
    fileInput: null,
    selectedFile: null,
    fileName: null,
    removeFileBtn: null,
    promptInput: null,
    submitBtn: null,
    welcomeSection: null,
    chatMessages: null,
    loadingIndicator: null
};

/**
 * Initialize chat application
 */
function initChat() {
    // Get DOM elements
    elements.uploadBtn = document.getElementById('uploadBtn');
    elements.fileInput = document.getElementById('fileInput');
    elements.selectedFile = document.getElementById('selectedFile');
    elements.fileName = document.getElementById('fileName');
    elements.removeFileBtn = document.getElementById('removeFileBtn');
    elements.promptInput = document.getElementById('promptInput');
    elements.submitBtn = document.getElementById('submitBtn');
    elements.welcomeSection = document.getElementById('welcomeSection');
    elements.chatMessages = document.getElementById('chatMessages');
    elements.loadingIndicator = document.getElementById('loadingIndicator');

    // Setup event listeners
    setupEventListeners();

    // Update submit button state
    updateSubmitButton();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // File upload
    elements.uploadBtn.addEventListener('click', () => {
        elements.fileInput.click();
    });

    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.removeFileBtn.addEventListener('click', removeFile);

    // Text input
    elements.promptInput.addEventListener('input', () => {
        autoResizeTextarea();
        updateSubmitButton();
    });

    elements.promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    });

    // Submit button
    elements.submitBtn.addEventListener('click', handleSubmit);
}

/**
 * Handle file selection
 */
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    chatState.uploadedFile = file;
    elements.fileName.textContent = file.name;
    elements.selectedFile.style.display = 'flex';
    updateSubmitButton();
}

/**
 * Remove selected file
 */
function removeFile() {
    chatState.uploadedFile = null;
    elements.fileInput.value = '';
    elements.selectedFile.style.display = 'none';
    elements.fileName.textContent = '';
    updateSubmitButton();
}

/**
 * Auto-resize textarea
 */
function autoResizeTextarea() {
    elements.promptInput.style.height = 'auto';
    elements.promptInput.style.height = elements.promptInput.scrollHeight + 'px';
}

/**
 * Update submit button state
 */
function updateSubmitButton() {
    const hasContent = elements.promptInput.value.trim().length > 0 || chatState.uploadedFile !== null;
    elements.submitBtn.disabled = !hasContent;
}

/**
 * Handle submit
 */
async function handleSubmit() {
    const prompt = elements.promptInput.value.trim();

    if (!prompt && !chatState.uploadedFile) return;

    try {
        // Disable inputs
        setInputsEnabled(false);

        // Upload file if present
        if (chatState.uploadedFile) {
            await handleFileUpload(chatState.uploadedFile);
        }

        // Send text message if present
        if (prompt) {
            await handleTextMessage(prompt);
        }

        // Clear input
        clearInput();

    } catch (error) {
        console.error('Error:', error);
        showErrorMessage(error.message);
    } finally {
        setInputsEnabled(true);
    }
}

/**
 * Handle file upload
 */
async function handleFileUpload(file) {
    showLoading(true);

    try {
        const response = await uploadFile(file);

        // Show file upload message
        addMessage({
            type: 'system',
            text: `📎 File uploaded: ${response.filename} (${response.chunks} chunks processed)`,
            time: new Date()
        });

        // Clear uploaded file state
        chatState.uploadedFile = null;
        elements.selectedFile.style.display = 'none';

    } catch (error) {
        throw new Error('Failed to upload file: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Handle text message
 */
async function handleTextMessage(text) {
    // Add user message
    addMessage({
        type: 'user',
        text: text,
        time: new Date()
    });

    showLoading(true);

    try {
        const response = await sendTextChat(text);

        // Add assistant message
        addMessage({
            type: 'assistant',
            text: response.assistant_text,
            time: new Date()
        });

    } catch (error) {
        throw new Error('Failed to send message: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Handle audio response from voice input
 */
window.handleAudioResponse = function (response) {
    // Add user message (transcription)
    addMessage({
        type: 'user',
        text: response.user_text,
        time: new Date()
    });

    // Add assistant message with audio
    addMessage({
        type: 'assistant',
        text: response.assistant_text,
        audio: response.audio_base64,
        time: new Date()
    });
};

/**
 * Add message to chat
 */
function addMessage(message) {
    // Hide welcome section, show chat
    if (elements.welcomeSection) {
        elements.welcomeSection.classList.add('hidden');
    }
    elements.chatMessages.style.display = 'flex';

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.type}`;

    if (message.type === 'system') {
        messageDiv.innerHTML = `
            <div class="message-content">
                ${message.text}
            </div>
        `;
    } else {
        const avatar = message.type === 'user' ? 'U' : 'AI';

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div>
                <div class="message-content">
                    ${message.text}
                </div>
                ${message.audio ? `
                    <div class="message-audio">
                        <audio controls>
                            <source src="data:audio/wav;base64,${message.audio}" type="audio/wav">
                        </audio>
                    </div>
                ` : ''}
                <div class="message-time">${formatTime(message.time)}</div>
            </div>
        `;
    }

    elements.chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;

    // Store message
    chatState.messages.push(message);
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    elements.loadingIndicator.style.display = show ? 'flex' : 'none';

    if (show) {
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }
}

/**
 * Clear input
 */
function clearInput() {
    elements.promptInput.value = '';
    elements.promptInput.style.height = 'auto';
    updateSubmitButton();
}

/**
 * Enable/disable inputs
 */
function setInputsEnabled(enabled) {
    elements.promptInput.disabled = !enabled;
    elements.submitBtn.disabled = !enabled;
    elements.uploadBtn.disabled = !enabled;
}

/**
 * Show error message
 */
function showErrorMessage(message) {
    addMessage({
        type: 'system',
        text: `❌ Error: ${message}`,
        time: new Date()
    });
}

/**
 * Format time
 */
function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Initialize when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChat);
} else {
    initChat();
}
