# Drishti AI - Complete Setup & Usage Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js (optional, for frontend server)
- MongoDB (running on localhost:27017)
- Ollama (with llama3.1 model)
- 8GB+ RAM (for models)

---

## Backend Setup

### 1. Install Dependencies
```bash
cd Drishti
.\drishti-env\Scripts\activate  # Windows
pip install -r backend/requirements.txt
```

### 2. Download Models (if not already done)
```bash
python backend/scripts/download_models.py
```

Models will be downloaded to `backend/models/`:
- Sarvam-1 (4.7 GB)
- Whisper small (927 MB)
- Indic-Parler-TTS (3.6 GB)
- Llama 3.1 via Ollama (4.9 GB)

### 3. Start Backend Server
```bash
# Using the script
.\backend\scripts\dev_run.bat

# Or manually
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080
```

Backend will be available at: **http://localhost:8080**

API docs at: **http://localhost:8080/docs**

---

## Frontend Setup

### Option 1: Simple (Static Files)
```bash
# Just open in browser
start index.html

# Or use Python's built-in server
python -m http.server 3000
```

Frontend will be at: **http://localhost:3000**

### Option 2: Using npm serve
```bash
npx serve . -p 3000
```

---

## Running the Full Stack

### Windows One-liner
```powershell
# Terminal 1 - Backend
.\drishti-env\Scripts\activate
.\backend\scripts\dev_run.bat

# Terminal 2 - Frontend (optional)
npx serve . -p 3000
```

---

## Testing the Integration

### 1. Backend Health Check
```bash
curl http://localhost:8080/health
```

Should return:
```json
{
  "status": "operational",
  "services": {
    "mongodb": "✅ connected",
    "ollama_llama": "✅ reachable",
    "sarvam": "✅ model present",
    "whisper": "✅ model directory exists",
    "tts": "✅ model present",
    "memori": "✅ MongoDB backend ready"
  }
}
```

### 2. Test Text Chat
```bash
curl -X POST http://localhost:8080/chat/text \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"test\",\"text\":\"Hello in Hindi\",\"lang\":\"auto\"}"
```

### 3. Test Frontend
1. Open `index.html` in browser
2. Type a message in the chat box
3. Click Send or press Enter
4. Should see response from backend

---

## Frontend Features

### Configured Endpoints (JS/config.js)
```javascript
- /health          - Backend health
- /chat/text       - Text chat
- /chat/audio      - Voice chat
- /files/upload    - Document upload
- /files/list      - List documents
- /translate       - Translation
```

### API Client (JS/api.js)
- `sendTextChat()` - Send text message
- `sendAudioChat()` - Send voice message
- `uploadFile()` - Upload PDF/DOCX/TXT
- `listFiles()` - Get user's files
- `translateText()` - Translate text

### Translation (JS/translate.js)
- 12 languages supported
- Uses backend `/translate` endpoint
- Automatic page translation
- Saves language preference

---

## Usage Examples

### Text Chat
1. Open frontend in browser
2. Type message: "Explain quantum computing"
3. Backend routes to Llama 3.1 (heavy model)
4. Response appears in chat

### Voice Chat
1. Click microphone icon
2. Allow microphone access
3. Speak your message
4. Backend: Whisper (STT) → LLM → Indic-Parler (TTS)
5. Get voice response

### File Upload & Context
1. Click "+" to upload file
2. Select PDF/DOCX/TXT
3. Backend chunks and stores in MongoDB
4. Ask questions about the document
5. Backend injects relevant chunks into context

### Translation
1. Click globe icon (top right)
2. Select language (Hindi, Spanish, etc.)
3. Page translates via backend
4. Preference saved in localStorage

---

## Architecture

```
Frontend (index.html)
  ↓ HTTP Request
Backend (FastAPI :8080)
  ↓
Services:
  - Llama 3.1 (Ollama)
  - Sarvam-1 (Transformers)
  - Whisper (STT)
  - Indic-Parler-TTS
  - Memori (Memory)
  ↓
MongoDB (Storage)
```

---

## Troubleshooting

### Backend won't start
- Check MongoDB: `sc query MongoDB`
- Check Ollama: `ollama list`
- Check models: `dir backend\models`
- Check port 8080: `netstat -ano | findstr :8080`

### Frontend can't connect
- Verify backend running: `curl http://localhost:8080/health`
- Check browser console for CORS errors
- Ensure API_BASE_URL in config.js matches backend

### Translation not working
- Backend must be running
- Check `/translate` endpoint in browser dev tools
- LLM may take 5-10 seconds per translation

### Voice input not working
- Grant microphone permission in browser
- Chrome/Edge recommended (better WebRTC support)
- Check backend Whisper model downloaded

---

## Development

### Run Tests
```bash
# All tests
pytest backend/tests -v

# With coverage
pytest --cov=backend --cov-report=html

# Specific category
pytest backend/tests/integration -v
```

### Code Quality
```bash
# Format
black backend/

# Lint
flake8 backend/

# Type check
mypy backend/
```

### Pre-commit
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Production Deployment

### Backend
```bash
# Use Gunicorn with Uvicorn workers
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8080
```

### Frontend
- Host on Netlify, Vercel, or S3
- Update `API_BASE_URL` to production backend
- Enable HTTPS

### Environment Variables
```bash
export MONGO_URI="your-production-mongodb-uri"
export OLLAMA_URL="your-ollama-server-url"
```

---

## Performance

- **Text Chat**: 1-5 seconds (depending on model)
- **Voice Chat**: 3-10 seconds (STT + LLM + TTS)
- **File Upload**: < 2 seconds for 1MB file
- **Translation**: 2-5 seconds per text

---

## Support

- **GitHub**: https://github.com/Aditya232-rtx/Drishti
- **Docs**: See `API_DOCUMENTATION.md`
- **Tests**: Run `pytest backend/tests -v`

---

**Built with ❤️ using FastAPI, Transformers, and modern AI models**
