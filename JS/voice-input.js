/**
 * Voice Input Module
 * Handles audio recording from device microphone and speech-to-text using Whisper
 */

// Voice input configuration
const VOICE_CONFIG = {
    // API endpoint for speech-to-text (Whisper)
    API_ENDPOINT: '/api/speech-to-text',

    // Audio recording settings
    AUDIO_FORMAT: 'audio/wav',
    SAMPLE_RATE: 16000, // Whisper works well with 16kHz

    // Maximum recording duration (in milliseconds)
    MAX_DURATION: 60000, // 60 seconds
};

// Recording state
let mediaRecorder = null;
let audioChunks = [];
let recordingTimeout = null;
let isRecording = false;

/**
 * Initialize the voice input module
 */
function initVoiceInput() {
    const micBtn = document.getElementById('micBtn');

    if (!micBtn) {
        console.error('Microphone button not found');
        return;
    }

    // Check if browser supports audio recording
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('Audio recording not supported in this browser');
        micBtn.disabled = true;
        micBtn.title = 'Voice input not supported in this browser';
        return;
    }

    // Setup microphone button click handler
    micBtn.addEventListener('click', handleMicButtonClick);
}

/**
 * Handle microphone button click
 */
async function handleMicButtonClick() {
    const micBtn = document.getElementById('micBtn');

    if (isRecording) {
        // Stop recording
        stopRecording();
    } else {
        // Start recording
        try {
            await startRecording();
        } catch (error) {
            console.error('Failed to start recording:', error);
            showVoiceError('Microphone access denied or unavailable');
        }
    }
}

/**
 * Start audio recording
 */
async function startRecording() {
    const micBtn = document.getElementById('micBtn');

    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                sampleRate: VOICE_CONFIG.SAMPLE_RATE,
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true
            }
        });

        // Create MediaRecorder
        const options = { mimeType: 'audio/webm' };

        // Try different MIME types if webm is not supported
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options.mimeType = 'audio/ogg';
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'audio/mp4';
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options.mimeType = '';
                }
            }
        }

        mediaRecorder = new MediaRecorder(stream, options);
        audioChunks = [];

        // Handle data available
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        // Handle recording stop
        mediaRecorder.onstop = async () => {
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());

            // Process the recorded audio
            await processRecordedAudio();
        };

        // Start recording
        mediaRecorder.start();
        isRecording = true;

        // Update UI
        micBtn.classList.add('recording');
        micBtn.title = 'Click to stop recording';

        // Set maximum recording duration
        recordingTimeout = setTimeout(() => {
            if (isRecording) {
                stopRecording();
            }
        }, VOICE_CONFIG.MAX_DURATION);

    } catch (error) {
        console.error('Error starting recording:', error);
        throw error;
    }
}

/**
 * Stop audio recording
 */
function stopRecording() {
    const micBtn = document.getElementById('micBtn');

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }

    isRecording = false;

    // Clear timeout
    if (recordingTimeout) {
        clearTimeout(recordingTimeout);
        recordingTimeout = null;
    }

    // Update UI
    micBtn.classList.remove('recording');
    micBtn.classList.add('processing');
    micBtn.title = 'Processing audio...';
}

/**
 * Process recorded audio and send to Whisper API
 */
async function processRecordedAudio() {
    const micBtn = document.getElementById('micBtn');

    try {
        // Create audio blob
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

        // Convert to base64
        const base64Audio = await blobToBase64(audioBlob);

        // Send to Whisper API
        const transcription = await sendToWhisperAPI(base64Audio);

        // Insert transcription into prompt input
        insertTranscription(transcription);

        // Reset UI
        micBtn.classList.remove('processing');
        micBtn.title = 'Click to record voice';

    } catch (error) {
        console.error('Error processing audio:', error);
        micBtn.classList.remove('processing');
        micBtn.title = 'Click to record voice';
        showVoiceError('Failed to process audio. Please try again.');
    }
}

/**
 * Convert blob to base64
 * @param {Blob} blob - Audio blob
 * @returns {Promise<string>} - Base64 encoded audio
 */
function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            // Remove data URL prefix (e.g., "data:audio/webm;base64,")
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

/**
 * Send audio to Whisper API for transcription
 * @param {string} base64Audio - Base64 encoded audio
 * @returns {Promise<string>} - Transcribed text
 */
async function sendToWhisperAPI(base64Audio) {
    /**
     * BACKEND DEVELOPER: Implement this endpoint
     * 
     * Endpoint: POST /api/speech-to-text
     * 
     * Request Body:
     * {
     *   "audio": "base64_encoded_audio_data",
     *   "format": "webm",  // or "wav", "mp3", "ogg" depending on browser
     *   "language": "en"   // optional, auto-detect if not provided
     * }
     * 
     * Response:
     * {
     *   "text": "transcribed text from audio",
     *   "language": "en",
     *   "confidence": 0.95  // optional
     * }
     * 
     * Use Whisper model for speech-to-text conversion.
     * You can use OpenAI's Whisper API or run Whisper locally.
     * 
     * Example with OpenAI Whisper API:
     * - Decode base64 to audio file
     * - Send to Whisper API
     * - Return transcribed text
     */

    const response = await fetch(VOICE_CONFIG.API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            audio: base64Audio,
            format: 'webm',
            language: 'en' // You can make this dynamic based on selected language
        })
    });

    if (!response.ok) {
        throw new Error(`Speech-to-text API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    if (!data.text) {
        throw new Error('No transcription returned from API');
    }

    return data.text;
}

/**
 * Insert transcription into prompt input
 * @param {string} text - Transcribed text
 */
function insertTranscription(text) {
    const promptInput = document.getElementById('promptInput');

    if (!promptInput) {
        console.error('Prompt input not found');
        return;
    }

    // Get current cursor position
    const cursorPos = promptInput.selectionStart;
    const currentText = promptInput.value;

    // Insert transcription at cursor position
    const newText = currentText.substring(0, cursorPos) + text + currentText.substring(cursorPos);
    promptInput.value = newText;

    // Set cursor position after inserted text
    const newCursorPos = cursorPos + text.length;
    promptInput.setSelectionRange(newCursorPos, newCursorPos);

    // Focus on input
    promptInput.focus();

    // Trigger input event for any listeners
    promptInput.dispatchEvent(new Event('input', { bubbles: true }));
}

/**
 * Show voice input error message
 * @param {string} message - Error message
 */
function showVoiceError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: #e74c3c;
        color: white;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        font-family: 'Martel Sans', sans-serif;
        max-width: 300px;
    `;
    errorDiv.textContent = message;

    document.body.appendChild(errorDiv);

    // Remove error message after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Initialize voice input when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVoiceInput);
} else {
    initVoiceInput();
}
