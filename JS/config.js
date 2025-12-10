// Configuration for Drishtikosh Frontend
const CONFIG = {
    API_BASE_URL: 'http://localhost:8080',
    ENDPOINTS: {
        // Health Check
        HEALTH: '/health',

        // Chat Endpoints
        CHAT_TEXT: '/chat/text',
        CHAT_AUDIO: '/chat/audio',

        // File Management
        FILES_UPLOAD: '/files/upload',
        FILES_LIST: '/files/list',

        // Translation
        TRANSLATE: '/translate'
    }
};

// Export for module usage if needed, otherwise global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
