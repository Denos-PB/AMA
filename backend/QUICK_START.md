# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### 1. **Copy Environment Template**
```bash
cd backend
cp .env.example .env
```

### 2. **Edit .env with Your Keys**
```bash
# Open .env and fill in:
GOOGLE_API_KEY=your_actual_key_here
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Run the Application**

**Option A: Development (with hot-reload)**
```bash
python src/main.py --reload
```

**Option B: Production**
```bash
python src/main.py --workers 4
```

### 5. **Test It Works**
```bash
# Health check
curl http://localhost:8000/health

# Try generating content
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Create an engaging Instagram post about machine learning",
    "modalities": ["audio", "image"]
  }'
```

### 6. **View API Docs**
Open your browser to: `http://localhost:8000/docs`

---

## 📋 Configuration Options

See `.env.example` for all available environment variables.

**Key settings**:
```env
WRITER_MODEL=gemini-2.0-flash              # LLM model to use
API_PORT=8000                              # Port to run on
OUTPUT_DIR=outputs                         # Where to save files
SERVE_GENERATED_ASSETS=false               # DEV: serve OUTPUT_DIR publicly at /assets
LOG_LEVEL=INFO                             # Logging verbosity
CORS_ENABLED=true                          # Allow cross-origin requests
```

---

## 🐛 Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'src'
```
**Solution**: Make sure you run from the `backend/` directory:
```bash
cd backend
python src/main.py
```

### API Key Not Working
```
google.api_core.exceptions.InvalidArgument: Invalid API Key
```
**Solution**: Check `.env` file has correct `GOOGLE_API_KEY`

### Port Already in Use
```
Address already in use: ('0.0.0.0', 8000)
```
**Solution**: Use different port:
```bash
python src/main.py --port 8001
```

### Logs Not Appearing
**Solution**: Check `LOG_LEVEL` in `.env` is not set to `CRITICAL`

---

## 📚 API Endpoints

### `POST /generate`
Generate content (main endpoint)

**Request**:
```json
{
  "user_prompt": "Create an Instagram post about AI",
  "request_id": "optional-tracking-id",
  "modalities": ["audio", "image"]
}
```

**Response**:
```json
{
  "success": true,
  "request_id": "req_12345",
  "status": "completed",
  "enhanced_text": "...",
  "audio_path": "outputs/audio/...",
  "audio_url": "http://localhost:8000/assets/audio/...",
  "image_path": "outputs/images/...",
  "image_url": "http://localhost:8000/assets/images/...",
  "description": "...",
  "hashtags": ["#ai", "#tech"]
}
```

If `SERVE_GENERATED_ASSETS=true`, you can open returned `audio_url` / `image_url` directly in browser.

### `GET /health`
Health check

**Response**:
```json
{
  "status": "healthy",
  "service": "AMA Agent",
  "version": "1.0.0"
}
```

### `GET /config`
Get current configuration

**Response**:
```json
{
  "writer_model": "gemini-2.0-flash",
  "audio_engine": "edge-tts",
  "image_model": "pollinations",
  "output_dir": "outputs"
}
```

---

## 📁 Directory Structure

```
backend/
├── .env                          # Your configuration (create from .env.example)
├── .env.example                  # Template
├── requirements.txt              # Python packages
├── Dockerfile                    # Container setup
├── REFACTORING_SUMMARY.md        # Detailed changes
├── QUICK_START.md                # This file
│
├── outputs/                      # Generated files (created at runtime)
│   ├── audio/                    # Generated audio files
│   └── images/                   # Generated images
│
└── src/
    ├── main.py                   # ⭐ Entry point - start here
    ├── app.py                    # FastAPI application
    ├── logging_config.py         # Logging setup
    │
    ├── agent/                    # Agent pipeline
    │   ├── configuration.py       # Config management
    │   ├── state.py              # Data structures
    │   ├── graph.py              # Main workflow
    │   ├── nodes.py              # Node definitions
    │   ├── subgraphs.py          # Worker subgraphs
    │   ├── prompts.py            # LLM prompts
    │   └── utils.py              # Shared utilities
    │
    ├── workers/                  # 4-Worker Pipeline
    │   ├── base.py               # Base worker class
    │   ├── prompt_enhancer.py    # Worker 1: Text enhancement
    │   ├── audio_generator.py    # Worker 2: Audio creation
    │   ├── image_generator.py    # Worker 3: Image creation
    │   └── description_writer.py # Worker 4: Descriptions & hashtags
    │
    └── tools/                    # Utilities
        ├── error_classification.py
        ├── json_parser.py
        └── user_request_parser.py
```

---

## 💡 Usage Examples

### Python Client
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "user_prompt": "Create a funny post about Python programming",
        "modalities": ["audio", "image"]
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Audio: {result['audio_path']}")
print(f"Image: {result['image_path']}")
print(f"Audio URL: {result.get('audio_url')}")
print(f"Image URL: {result.get('image_url')}")
print(f"Hashtags: {result['hashtags']}")
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_prompt: 'Create an Instagram post about web development',
    modalities: ['audio', 'image']
  })
});

const data = await response.json();
console.log(data.status); // 'completed'
console.log(data.hashtags); // ['#webdev', ...]
```

### cURL
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Create a TikTok script about AI",
    "modalities": ["audio"]
  }' | jq
```

---

## 🔄 Processing Pipeline

```
User Request
    ↓
Parse Request (extract modalities)
    ↓
├→ Worker 1: Enhance Text
│   Output: enhanced_text, main_statement
│   ↓
├→ Worker 2: Generate Audio Script
│   Output: audio_path, script
│   ↓
├→ Worker 3: Generate Image
│   Output: image_path, visual_brief
│   ↓
└→ Worker 4: Write Descriptions & Hashtags
    Inputs: all above outputs
    Output: description, hashtags
    ↓
Final Response with all assets
```

---

## 📊 Monitoring

### View Logs
```bash
# Real-time logs (when running in foreground)
# Logs appear in terminal

# View log file
tail -f logs/ama_agent.log
```

### Check Generated Assets
```bash
# List generated audio files
ls outputs/audio/

# List generated images
ls outputs/images/
```

---

## 🛠️ Development

### Add New Environment Variable
1. Add to `.env.example`
2. Add to `src/agent/configuration.py` as a Field
3. Load in your code: `config.your_variable`

### Add Logging
```python
from src.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Something happened")
logger.error("Error message", exc_info=True)
```
