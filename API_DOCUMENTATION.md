# Translation API Documentation for Backend Developer

## Overview

This document provides the API specification for implementing endpoints that integrate with AI models (Gemini for translation, Whisper for speech-to-text) to provide translation and voice input functionality.

## Endpoints

### 1. POST `/api/speech-to-text`

Converts audio input to text using Whisper speech-to-text model.

#### Request

**Method:** POST  
**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "audio": "base64_encoded_audio_data",
  "format": "webm",
  "language": "en"
}
```

**Parameters:**
- `audio` (string, required): Base64-encoded audio data from device microphone
- `format` (string, required): Audio format - "webm", "wav", "mp3", or "ogg" (browser-dependent)
- `language` (string, optional): ISO 639-1 language code for transcription (e.g., "en", "es"). Auto-detect if not provided.

#### Response

**Success (200 OK):**
```json
{
  "text": "Hello, how can I help you today?",
  "language": "en",
  "confidence": 0.95
}
```

**Parameters:**
- `text` (string): Transcribed text from audio
- `language` (string): Detected or specified language
- `confidence` (number, optional): Confidence score (0-1)

**Error (400 Bad Request):**
```json
{
  "error": "Invalid request",
  "message": "Missing required field: audio"
}
```

**Error (500 Internal Server Error):**
```json
{
  "error": "Transcription failed",
  "message": "Whisper API error: [error details]"
}
```

---

### 2. GET `/api/languages`

Returns the list of languages available for translation in the Gemini API.

#### Request

**Method:** GET  
**Headers:** None required

#### Response

**Success (200 OK):**
```json
{
  "languages": {
    "en": {
      "name": "English",
      "flag": "🇬🇧"
    },
    "es": {
      "name": "Spanish",
      "flag": "🇪🇸"
    },
    "fr": {
      "name": "French",
      "flag": "🇫🇷"
    },
    "de": {
      "name": "German",
      "flag": "🇩🇪"
    },
    "hi": {
      "name": "Hindi",
      "flag": "🇮🇳"
    },
    "zh": {
      "name": "Chinese",
      "flag": "🇨🇳"
    },
    "ja": {
      "name": "Japanese",
      "flag": "🇯🇵"
    },
    "ar": {
      "name": "Arabic",
      "flag": "🇸🇦"
    }
  }
}
```

**Notes:**
- The language codes should be ISO 639-1 codes (e.g., "en", "es", "fr")
- Only include languages that Gemini API supports for translation
- The frontend will use this list to populate the language dropdown dynamically
- If this endpoint fails, the frontend will fall back to a default set of languages

---

### 2. GET `/api/languages`

Returns the list of languages available for translation in the Gemini API.

#### Request

**Method:** GET  
**Headers:** None required

#### Response

**Success (200 OK):**
```json
{
  "languages": {
    "en": {
      "name": "English",
      "flag": "🇬🇧"
    },
    "es": {
      "name": "Spanish",
      "flag": "🇪🇸"
    },
    "fr": {
      "name": "French",
      "flag": "🇫🇷"
    },
    "de": {
      "name": "German",
      "flag": "🇩🇪"
    },
    "hi": {
      "name": "Hindi",
      "flag": "🇮🇳"
    },
    "zh": {
      "name": "Chinese",
      "flag": "🇨🇳"
    },
    "ja": {
      "name": "Japanese",
      "flag": "🇯🇵"
    },
    "ar": {
      "name": "Arabic",
      "flag": "🇸🇦"
    }
  }
}
```

**Notes:**
- The language codes should be ISO 639-1 codes (e.g., "en", "es", "fr")
- Only include languages that Gemini API supports for translation
- The frontend will use this list to populate the language dropdown dynamically
- If this endpoint fails, the frontend will fall back to a default set of languages

---

### 3. POST `/api/translate`

Translates an array of text strings to the specified target language using the Gemini API.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "texts": [
    "What's on your mind today?",
    "Upload content or ask a question to get started",
    "Past Chats",
    "No chats yet. Start a new conversation!",
    "Ask anything..."
  ],
  "targetLanguage": "es"
}
```

**Parameters:**
- `texts` (array of strings, required): Array of text strings to translate
- `targetLanguage` (string, required): ISO 639-1 language code (e.g., "es", "fr", "de", "hi", "zh", "ja", "ar")

#### Response

**Success (200 OK):**
```json
{
  "translations": [
    "¿Qué tienes en mente hoy?",
    "Sube contenido o haz una pregunta para comenzar",
    "Chats Pasados",
    "Aún no hay chats. ¡Comienza una nueva conversación!",
    "Pregunta cualquier cosa..."
  ],
  "targetLanguage": "es"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "Invalid request",
  "message": "Missing required field: targetLanguage"
}
```

**Error (500 Internal Server Error):**
```json
{
  "error": "Translation failed",
  "message": "Gemini API error: [error details]"
}
```

## Implementation Guide

### 1. Speech-to-Text Endpoint (Whisper)

This endpoint converts audio from the device microphone to text using Whisper.

**Implementation Options:**

**Option A: Using OpenAI Whisper API**

```javascript
const express = require('express');
const fetch = require('node-fetch');
const FormData = require('form-data');

app.post('/api/speech-to-text', async (req, res) => {
  try {
    const { audio, format, language } = req.body;

    if (!audio) {
      return res.status(400).json({
        error: 'Invalid request',
        message: 'audio field is required'
      });
    }

    // Decode base64 audio
    const audioBuffer = Buffer.from(audio, 'base64');

    // Create form data for Whisper API
    const formData = new FormData();
    formData.append('file', audioBuffer, {
      filename: `audio.${format || 'webm'}`,
      contentType: `audio/${format || 'webm'}`
    });
    formData.append('model', 'whisper-1');
    if (language) {
      formData.append('language', language);
    }

    // Call OpenAI Whisper API
    const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        ...formData.getHeaders()
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Whisper API error: ${response.statusText}`);
    }

    const data = await response.json();

    res.json({
      text: data.text,
      language: language || 'en'
    });

  } catch (error) {
    console.error('Speech-to-text error:', error);
    res.status(500).json({
      error: 'Transcription failed',
      message: error.message
    });
  }
});
```

**Option B: Using Local Whisper Model**

```python
# Python Flask example with local Whisper
from flask import Flask, request, jsonify
import whisper
import base64
import io
import tempfile

app = Flask(__name__)

# Load Whisper model (do this once at startup)
model = whisper.load_model("base")  # or "small", "medium", "large"

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        data = request.json
        audio_base64 = data.get('audio')
        audio_format = data.get('format', 'webm')
        language = data.get('language', 'en')

        if not audio_base64:
            return jsonify({
                'error': 'Invalid request',
                'message': 'audio field is required'
            }), 400

        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        # Transcribe with Whisper
        result = model.transcribe(temp_audio_path, language=language)

        return jsonify({
            'text': result['text'],
            'language': result.get('language', language)
        })

    except Exception as e:
        return jsonify({
            'error': 'Transcription failed',
            'message': str(e)
        }), 500
```

**Notes:**
- Local Whisper requires GPU for good performance
- OpenAI API is easier but requires API key and has costs
- Consider audio format conversion if needed (ffmpeg)
- The frontend sends base64-encoded audio from browser's MediaRecorder

---

### 2. Languages Endpoint

This endpoint should return the languages that Gemini API supports for translation.

**Example Implementation (Node.js/Express):**

```javascript
app.get('/api/languages', (req, res) => {
  // Return the languages supported by Gemini API
  // You can customize this list based on what Gemini supports
  const languages = {
    'en': { name: 'English', flag: '🇬🇧' },
    'es': { name: 'Spanish', flag: '🇪🇸' },
    'fr': { name: 'French', flag: '🇫🇷' },
    'de': { name: 'German', flag: '🇩🇪' },
    'hi': { name: 'Hindi', flag: '🇮🇳' },
    'zh': { name: 'Chinese', flag: '🇨🇳' },
    'ja': { name: 'Japanese', flag: '🇯🇵' },
    'ar': { name: 'Arabic', flag: '🇸🇦' },
    'pt': { name: 'Portuguese', flag: '🇵🇹' },
    'ru': { name: 'Russian', flag: '🇷🇺' },
    'ko': { name: 'Korean', flag: '🇰🇷' },
    'it': { name: 'Italian', flag: '🇮🇹' }
    // Add more languages as supported by Gemini
  };

  res.json({ languages });
});
```

**Notes:**
- You can add or remove languages based on Gemini API capabilities
- The frontend will automatically update the dropdown based on this response
- Consider caching this response since it rarely changes

---

### 2. Languages Endpoint

This endpoint should return the languages that Gemini API supports for translation.

**Example Implementation (Node.js/Express):**

```javascript
app.get('/api/languages', (req, res) => {
  // Return the languages supported by Gemini API
  // You can customize this list based on what Gemini supports
  const languages = {
    'en': { name: 'English', flag: '🇬🇧' },
    'es': { name: 'Spanish', flag: '🇪🇸' },
    'fr': { name: 'French', flag: '🇫🇷' },
    'de': { name: 'German', flag: '🇩🇪' },
    'hi': { name: 'Hindi', flag: '🇮🇳' },
    'zh': { name: 'Chinese', flag: '🇨🇳' },
    'ja': { name: 'Japanese', flag: '🇯🇵' },
    'ar': { name: 'Arabic', flag: '🇸🇦' },
    'pt': { name: 'Portuguese', flag: '🇵🇹' },
    'ru': { name: 'Russian', flag: '🇷🇺' },
    'ko': { name: 'Korean', flag: '🇰🇷' },
    'it': { name: 'Italian', flag: '🇮🇹' }
    // Add more languages as supported by Gemini
  };

  res.json({ languages });
});
```

**Notes:**
- You can add or remove languages based on Gemini API capabilities
- The frontend will automatically update the dropdown based on this response
- Consider caching this response since it rarely changes

---

### 3. Translation Endpoint

### Using Gemini API

1. **API Setup:**
   - Use the Gemini API client library for your backend language
   - Configure your API key securely (environment variable recommended)

2. **Translation Prompt:**
   ```
   Translate the following texts to {targetLanguage} ({languageName}). 
   Return ONLY the translations in the exact same order as the input, 
   one translation per line. Do not add any explanations or numbering.

   Texts to translate:
   1. {text1}
   2. {text2}
   3. {text3}
   ...
   ```

3. **Processing Steps:**
   - Validate the request body (check for required fields)
   - Validate the target language code
   - Construct the translation prompt with all texts
   - Call Gemini API with the prompt
   - Parse the response to extract translations
   - Ensure the number of translations matches the input
   - Return the translations in the same order

4. **Error Handling:**
   - Handle missing or invalid parameters (400)
   - Handle Gemini API errors (500)
   - Handle rate limiting (429)
   - Log errors for debugging

### Example Implementation (Node.js/Express)

```javascript
const express = require('express');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const app = express();
app.use(express.json());

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

app.post('/api/translate', async (req, res) => {
  try {
    const { texts, targetLanguage } = req.body;

    // Validation
    if (!texts || !Array.isArray(texts) || texts.length === 0) {
      return res.status(400).json({
        error: 'Invalid request',
        message: 'texts must be a non-empty array'
      });
    }

    if (!targetLanguage) {
      return res.status(400).json({
        error: 'Invalid request',
        message: 'targetLanguage is required'
      });
    }

    // Language name mapping
    const languageNames = {
      'es': 'Spanish',
      'fr': 'French',
      'de': 'German',
      'hi': 'Hindi',
      'zh': 'Chinese',
      'ja': 'Japanese',
      'ar': 'Arabic'
    };

    const languageName = languageNames[targetLanguage];
    if (!languageName) {
      return res.status(400).json({
        error: 'Invalid request',
        message: 'Unsupported target language'
      });
    }

    // Construct prompt
    const numberedTexts = texts.map((text, i) => `${i + 1}. ${text}`).join('\n');
    const prompt = `Translate the following texts to ${languageName}. Return ONLY the translations in the exact same order as the input, one translation per line. Do not add any explanations or numbering.\n\nTexts to translate:\n${numberedTexts}`;

    // Call Gemini API
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const translatedText = response.text();

    // Parse translations
    const translations = translatedText.trim().split('\n').map(t => t.trim());

    // Validate translation count
    if (translations.length !== texts.length) {
      throw new Error('Translation count mismatch');
    }

    // Return response
    res.json({
      translations,
      targetLanguage
    });

  } catch (error) {
    console.error('Translation error:', error);
    res.status(500).json({
      error: 'Translation failed',
      message: error.message
    });
  }
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Supported Languages

| Code | Language |
|------|----------|
| en   | English  |
| es   | Spanish  |
| fr   | French   |
| de   | German   |
| hi   | Hindi    |
| zh   | Chinese  |
| ja   | Japanese |
| ar   | Arabic   |

## Testing

### Test Request (cURL)

```bash
curl -X POST http://localhost:3000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello", "How are you?", "Welcome"],
    "targetLanguage": "es"
  }'
```

### Expected Response

```json
{
  "translations": ["Hola", "¿Cómo estás?", "Bienvenido"],
  "targetLanguage": "es"
}
```

## Notes

- The frontend will automatically collect all translatable text from the page
- Translations are cached in the browser using localStorage
- The API should handle batch translation efficiently
- Consider implementing rate limiting to prevent abuse
- The order of translations MUST match the order of input texts
