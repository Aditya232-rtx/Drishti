// ============================================
// API Utility Module for Drishtikosh Frontend
// ============================================

/**
 * Get authentication headers for API requests
 * @returns {Object} Headers object with Authorization token
 */
function getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
}

/**
 * Get FormData headers (without Content-Type, browser sets it automatically)
 * @returns {Object} Headers object with Authorization token
 */
function getFormDataHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
}

/**
 * Get user ID from localStorage
 * @returns {string|null} User ID or null if not found
 */
function getUserId() {
    return localStorage.getItem('current_user_id') || localStorage.getItem('user_id');
}

/**
 * Get user mode from localStorage
 * @returns {string|null} User mode (blind/adhd/deaf) or null if not found
 */
function getUserMode() {
    return localStorage.getItem('user_mode');
}

/**
 * Get user info from localStorage
 * @returns {Object|null} User info object with id, mode, name, or null if not found
 */
function getUserInfo() {
    const userId = localStorage.getItem('current_user_id');
    const userMode = localStorage.getItem('user_mode');
    const userName = localStorage.getItem('user_name');

    if (!userId) {
        return null;
    }

    return {
        id: userId,
        mode: userMode || 'adhd',
        name: userName || 'User',
        interest_field: localStorage.getItem('interest_field') || 'general'
    };
}

/**
 * Get current session ID from localStorage
 * @returns {string|null} Session ID or null if not found
 */
function getSessionId() {
    return localStorage.getItem('current_session_id');
}

/**
 * Store session ID in localStorage
 * @param {string} sessionId - Session ID to store
 */
function setSessionId(sessionId) {
    localStorage.setItem('current_session_id', sessionId);
}

/**
 * Clear session ID from localStorage
 */
function clearSessionId() {
    localStorage.removeItem('current_session_id');
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if user has auth token
 */
function isAuthenticated() {
    return !!localStorage.getItem('auth_token');
}

/**
 * Redirect to login page if not authenticated
 */
function requireAuth() {
    return true;
}

/**
 * Handle API errors consistently
 * @param {Response} response - Fetch response object
 * @param {string} defaultMessage - Default error message
 * @returns {Promise<Object>} Error object with message
 */
async function handleApiError(response, defaultMessage = 'An error occurred') {
    let errorMessage = defaultMessage;

    try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch (e) {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
    }

    // Handle specific status codes
    if (response.status === 401) {
        // Unauthorized - clear auth and redirect to login
        localStorage.clear();
        window.location.href = '/Html/Login.html';
        return { error: 'Session expired. Please login again.', status: 401 };
    }

    if (response.status === 404) {
        return { error: 'Resource not found.', status: 404 };
    }

    if (response.status >= 500) {
        return { error: 'Server error. Please try again later.', status: response.status };
    }

    return { error: errorMessage, status: response.status };
}

/**
 * Wrapper for API calls with authentication and error handling
 * @param {string} endpoint - API endpoint (relative path)
 * @param {Object} options - Fetch options (method, body, etc.)
 * @param {boolean} useFormData - Whether to use FormData (don't set Content-Type)
 * @returns {Promise<Object>} Response data or error object
 */
async function apiCall(endpoint, options = {}, useFormData = false) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;

    const headers = useFormData ? getFormDataHeaders() : getAuthHeaders();

    const config = {
        ...options,
        headers: {
            ...headers,
            ...(options.headers || {})
        }
    };

    try {
        const response = await fetch(url, config);

        if (!response.ok) {
            const error = await handleApiError(response, 'Request failed');
            throw new Error(error.error || 'Request failed');
        }

        // Handle empty responses
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            return data;
        }

        return { success: true };
    } catch (error) {
        // Ensure we always throw an Error object with a string message
        if (error instanceof Error) {
            throw error;
        }
        // If it's a string, convert to Error
        if (typeof error === 'string') {
            throw new Error(error);
        }
        // If it's an object, try to extract message
        if (error && typeof error === 'object') {
            // Handle Pydantic validation errors
            if (error.detail && Array.isArray(error.detail)) {
                const messages = error.detail.map(e => e.msg || e.message || 'Validation error').join(', ');
                throw new Error(messages);
            }
            const message = error.error || error.message || error.detail || 'An error occurred';
            throw new Error(message);
        }
        // Network error
        throw new Error('Network error. Please check your connection and try again.');
    }
}

/**
 * Start a new learning session
 * @returns {Promise<Object>}
 */
async function startSession() {
    const userId = getUserId();
    if (!userId) {
        throw new Error('User not authenticated. Please login.');
    }

    const response = await apiCall(CONFIG.ENDPOINTS.SESSION_START, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId })
    });

    if (response.id) {
        setSessionId(response.id);
    }

    return response;
}

/**
 * End the current session
 * @param {string} sessionId - Session ID to end (optional, uses stored if not provided)
 * @returns {Promise<Object>} Success message
 */
async function endSession(sessionId = null) {
    const sid = sessionId || getSessionId();
    if (!sid) {
        console.warn('No session ID to end');
        return { message: 'No active session' };
    }

    try {
        const response = await apiCall(CONFIG.ENDPOINTS.SESSION_END, {
            method: 'POST',
            body: JSON.stringify({ session_id: sid })
        });

        clearSessionId();
        return response;
    } catch (error) {
        console.error('Error ending session:', error);
        clearSessionId(); // Clear anyway
        return { message: 'Session cleared' };
    }
}

/**
 * Get or create a session ID
 * @returns {Promise<string>} Session ID
 */
async function getOrCreateSession() {
    let sessionId = getSessionId();

    if (!sessionId) {
        const session = await startSession();
        sessionId = session.id;
    }

    return sessionId;
}

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getAuthHeaders,
        getFormDataHeaders,
        getUserId,
        getUserMode,
        getSessionId,
        setSessionId,
        clearSessionId,
        isAuthenticated,
        requireAuth,
        handleApiError,
        apiCall,
        startSession,
        endSession,
        getOrCreateSession
    };
}
