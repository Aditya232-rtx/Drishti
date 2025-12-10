# Drishtikosh - Multilingual AI Chat Application

A modern, multilingual AI chat application with voice input capabilities. Built with a focus on accessibility and user experience.

## ✨ Features

### 🌍 Language Translation
- **Dynamic Language Selector**: Top-right language button with dropdown menu
- **8+ Languages Supported**: English, Spanish, French, German, Hindi, Chinese, Japanese, Arabic, and more
- **Real-time Translation**: Powered by Gemini API
- **Smart Language Loading**: Dynamically fetches available languages from backend
- **Persistent Selection**: Remembers your language preference using localStorage
- **Scrollable Dropdown**: Clean, accessible language selection interface

### 🎤 Voice Input
- **Device Microphone Support**: Record audio directly from your device
- **Visual Feedback**: 
  - Blue (idle) - Ready to record
  - Red pulsing (recording) - Currently recording
  - Orange (processing) - Converting speech to text
- **Whisper Integration**: Speech-to-text powered by OpenAI's Whisper model
- **Auto-Insert**: Transcribed text automatically appears in the input field
- **60-Second Limit**: Configurable maximum recording duration
- **Error Handling**: Graceful handling of permission denials and API failures

### 💬 Chat Interface
- **Clean Design**: Modern, gradient background with intuitive layout
- **File Upload**: Support for images, PDFs, and documents
- **Past Chats**: Sidebar with chat history
- **Responsive**: Works seamlessly on desktop and mobile devices

## 🚀 Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Node.js (for backend)
- API keys for:
  - Google Gemini API (for translation)
  - OpenAI API (for Whisper) OR local Whisper installation

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Aditya232-rtx/Drishti.git
cd Drishti
```

2. **Open the application**
```bash
# Simply open index.html in your browser
# Or use a local server:
npx serve .
```

3. **Set up the backend** (See [Backend Setup](#backend-setup))

## 🔧 Backend Setup

The frontend is ready to use, but requires backend API endpoints for full functionality.

### Required Endpoints

#### 1. GET `/api/languages`
Returns available languages for translation.

**Response:**
```json
{
  "languages": {
    "en": { "name": "English", "flag": "🇬🇧" },
    "es": { "name": "Spanish", "flag": "🇪🇸" },
    "fr": { "name": "French", "flag": "🇫🇷" }
  }
}
```

#### 2. POST `/api/translate`
Translates text to target language using Gemini API.

**Request:**
```json
{
  "texts": ["Hello", "How are you?"],
  "targetLanguage": "es"
}
```

**Response:**
```json
{
  "translations": ["Hola", "¿Cómo estás?"],
  "targetLanguage": "es"
}
```

#### 3. POST `/api/speech-to-text`
Converts audio to text using Whisper.

**Request:**
```json
{
  "audio": "base64_encoded_audio_data",
  "format": "webm",
  "language": "en"
}
```

**Response:**
```json
{
  "text": "Hello, how can I help you today?",
  "language": "en"
}
```

### Implementation Examples

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete implementation guides with:
- Node.js/Express examples
- Python/Flask examples
- Error handling
- Testing examples

## 📁 Project Structure

```
Drishtikosh/
├── index.html              # Main application page
├── style.css               # Application styles
├── script.js               # Main application logic
├── API_DOCUMENTATION.md    # Complete API documentation
├── README.md               # This file
├── JS/
│   ├── config.js          # Configuration
│   ├── api.js             # API utilities
│   ├── translate.js       # Translation module
│   └── voice-input.js     # Voice input module
└── assets/
    └── Dristikosh_logo.png # Application logo
```

## 🎨 Design

- **Color Scheme**: Blue gradient (#EAF6FD to #A1D3ED)
- **Primary Color**: #3B93C2
- **Font**: Martel Sans
- **Responsive**: Mobile-first design with breakpoints at 768px

## 🔒 Browser Permissions

The application requires the following permissions:

- **Microphone Access**: For voice input feature
  - Requested only when user clicks the microphone button
  - Can be denied without affecting other features

## 🌐 Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Translation | ✅ | ✅ | ✅ | ✅ |
| Voice Input | ✅ | ✅ | ✅ | ✅ |
| File Upload | ✅ | ✅ | ✅ | ✅ |

## 🛠️ Configuration

### Voice Input Settings
Edit `JS/voice-input.js`:
```javascript
const VOICE_CONFIG = {
    API_ENDPOINT: '/api/speech-to-text',
    SAMPLE_RATE: 16000,
    MAX_DURATION: 60000  // 60 seconds
};
```

### Translation Settings
Edit `JS/translate.js`:
```javascript
const TRANSLATION_CONFIG = {
    API_ENDPOINT: '/api/translate',
    LANGUAGES_ENDPOINT: '/api/languages',
    DEFAULT_LANGUAGE: 'en'
};
```

## 📝 Usage

### Translating the Page
1. Click the globe icon in the top-right corner
2. Select your preferred language from the dropdown
3. All text on the page will be translated automatically
4. Your selection is saved for future visits

### Using Voice Input
1. Click the microphone button beside the send button
2. Allow microphone access when prompted
3. Speak your message (up to 60 seconds)
4. Click the button again to stop recording
5. Transcribed text will appear in the input field automatically

### Uploading Files
1. Click the + button above the input field
2. Select your file (images, PDFs, documents)
3. The file will be attached to your message
4. Type your question and send

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👥 Authors

- **Aditya** - [@Aditya232-rtx](https://github.com/Aditya232-rtx)

## 🙏 Acknowledgments

- Google Gemini API for translation
- OpenAI Whisper for speech-to-text
- All contributors and users of this project

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## 🔮 Roadmap

- [ ] Real-time conversation mode
- [ ] Multiple AI model support
- [ ] Chat export functionality
- [ ] Dark mode
- [ ] Custom language additions
- [ ] Offline mode support

---

**Built with ❤️ for accessibility and multilingual communication**
