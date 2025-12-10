/**
 * Voice Input Module
 * Handles audio recording and speech-to-text
 */

const VOICE_CONFIG = {
    API_ENDPOINT: CONFIG.API_BASE_URL + '/chat/audio',
    MAX_DURATION: 60000, // 60 seconds
};

let mediaRecorder = null;
let audioChunks = [];
let recordingTimeout = null;
let isRecording = false;

/**
 * Initialize voice input
 */
function initVoiceInput() {
    const micBtn = document.getElementById('micBtn');

    if (!micBtn) return;

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        micBtn.disabled = true;
        micBtn.title = 'Voice input not supported';
        return;
    }

    micBtn.addEventListener('click', handleMicButtonClick);
}

/**
 * Handle mic button click
 */
async function handleMicButtonClick() {
    if (isRecording) {
        stopRecording();
    } else {
        try {
            await startRecording();
        } catch (error) {
            console.error('Failed to start recording:', error);
            showError('Microphone access denied');
        }
    }
}

/**
 * Start recording
 */
async function startRecording() {
    const micBtn = document.getElementById('micBtn');

    const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
            sampleRate: 16000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true
        }
    });

    const options = { mimeType: 'audio/webm' };
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'audio/ogg';
    }

    mediaRecorder = new MediaRecorder(stream, options);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            audioChunks.push(event.data);
        }
    };

    mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        await processRecordedAudio();
    };

    mediaRecorder.start();
    isRecording = true;

    micBtn.classList.add('recording');
    micBtn.title = 'Click to stop recording';

    recordingTimeout = setTimeout(() => {
        if (isRecording) stopRecording();
    }, VOICE_CONFIG.MAX_DURATION);
}

/**
 * Stop recording
 */
function stopRecording() {
    const micBtn = document.getElementById('micBtn');

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }

    isRecording = false;

    if (recordingTimeout) {
        clearTimeout(recordingTimeout);
        recordingTimeout = null;
    }

    micBtn.classList.remove('recording');
    micBtn.classList.add('processing');
    micBtn.title = 'Processing...';
}

/**
 * Process recorded audio
 */
async function processRecordedAudio() {
    const micBtn = document.getElementById('micBtn');

    try {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const result = await sendAudioChat(audioBlob);

        // Trigger the chat to handle the audio response
        if (window.handleAudioResponse) {
            window.handleAudioResponse(result);
        }

        micBtn.classList.remove('processing');
        micBtn.title = 'Click to record voice';
    } catch (error) {
        console.error('Error processing audio:', error);
        micBtn.classList.remove('processing');
        micBtn.title = 'Click to record voice';
        showError('Failed to process audio');
    }
}

/**
 * Show error message
 */
function showError(message) {
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

    setTimeout(() => errorDiv.remove(), 5000);
}

// Initialize when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVoiceInput);
} else {
    initVoiceInput();
}
