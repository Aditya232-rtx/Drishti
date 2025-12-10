// ============================================
// API Utility Module for Drishtikosh Frontend
// ============================================

/**
 * Get user ID from localStorage
 * @returns {string} User ID
 */
function getUserId() {
    let userId = localStorage.getItem('current_user_id');
    if (!userId) {
        userId = 'user_' + Date.now();
        localStorage.setItem('current_user_id', userId);
    }
    return userId;
}

/**
 * Get current session ID from localStorage
 * @returns {string} Session ID
 */
function getSessionId() {
    let sessionId = localStorage.getItem('current_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('current_session_id', sessionId);
    }
    return sessionId;
}

/**
 * Send text chat message to backend
 * @param {string} text - Message text
 * @returns {Promise<Object>} Chat response
 */
async function sendTextChat(text) {
    const response = await fetch(CONFIG.API_BASE_URL + CONFIG.ENDPOINTS.CHAT_TEXT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: getUserId(),
            session_id: getSessionId(),
            text: text,
            lang: 'auto'
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to send message');
    }

    return await response.json();
}

/**
 * Send audio chat message to backend
 * @param {Blob} audioBlob - Audio blob
 * @returns {Promise<Object>} Chat response with audio
 */
async function sendAudioChat(audioBlob) {
    const formData = new FormData();
    formData.append('user_id', getUserId());
    formData.append('session_id', getSessionId());
    formData.append('audio', audioBlob, 'audio.webm');

    const response = await fetch(CONFIG.API_BASE_URL + CONFIG.ENDPOINTS.CHAT_AUDIO, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to process audio');
    }

    return await response.json();
}

/**
 * Upload file to backend
 * @param {File} file - File to upload
 * @returns {Promise<Object>} Upload response
 */
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('user_id', getUserId());
    formData.append('file', file);

    const response = await fetch(CONFIG.API_BASE_URL + CONFIG.ENDPOINTS.FILES_UPLOAD, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload file');
    }

    return await response.json();
}

/**
 * Translate text
 * @param {string} text - Text to translate
 * @param {string} targetLang - Target language code
 * @returns {Promise<Object>} Translation response
 */
async function translateText(text, targetLang) {
    const response = await fetch(CONFIG.API_BASE_URL + CONFIG.ENDPOINTS.TRANSLATE, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: text,
            source_lang: 'en',
            target_lang: targetLang,
            tts: false
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Translation failed');
    }

    return await response.json();
}
