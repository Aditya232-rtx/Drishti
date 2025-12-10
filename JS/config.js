// Configuration for Drishtikosh Frontend
const CONFIG = {
    API_BASE_URL: 'http://localhost:8001',
    ENDPOINTS: {
        // Authentication
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        
        // Session Management
        SESSION_START: '/session/start',
        SESSION_END: '/session/end',
        SESSION_GET: '/session', // /session/{session_id}
        
        // Brain/Learning Endpoints
        BRAIN_EXPLANATION: '/brain/explanation',
        BRAIN_VIDEO_EXPLANATION: '/brain/video-explanation',
        BRAIN_IMAGE: '/brain/image',
        BRAIN_QUIZ: '/brain/quiz',
        
        // Context/File Upload
        CONTEXT_UPLOAD: '/context/upload',
        CONTEXT_LIST: '/context/list', // /context/list/{session_id}
        
        // Blind Mode
        BLIND_ASSISTANT: '/session' // /session/{session_id}/blind-assistant
    }
};

// Export for module usage if needed, otherwise global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
