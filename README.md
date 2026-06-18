# AMA

AI-powered content creation pipeline for social media. AMA turns a single user prompt
into enhanced text, audio narration, images, and post-ready descriptions/hashtags, with
optional publishing to Instagram and Threads.

## What it does

- Enhances a raw prompt into a structured, creative description
- Generates audio narration (TTS)
- Generates images via Replicate (FLUX.1 dev or Ideogram v3)
- Writes captions, descriptions, and hashtags
- Exposes a FastAPI service with `/generate` and publish endpoints

## Quick start (backend)

Follow the full guide in `backend/QUICK_START.md`. Minimal steps:

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python src/main.py --reload
```

Open docs: `http://localhost:8000/docs`

## API usage

Generate content:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Create an Instagram post about AI",
    "modalities": ["audio", "image"]
  }'
```

Publish to Instagram:

```bash
curl -X POST http://localhost:8000/publish/instagram \
  -H "Content-Type: application/json" \
  -d '{
    "ig_user_id": "1784140...",
    "access_token": "EAAG...",
    "image_url": "http://localhost:8000/assets/images/...",
    "caption": "Hello from AMA"
  }'
```

Publish to Threads:

```bash
curl -X POST http://localhost:8000/publish/threads \
  -H "Content-Type: application/json" \
  -d '{
    "threads_user_id": "1784140...",
    "access_token": "THQVJ...",
    "image_url": "http://localhost:8000/assets/images/...",
    "text": "Hello Threads"
  }'
```

## How the agent works

Pipeline:

1. **Parse request** to extract modalities (audio/image)
2. **Prompt enhancer** creates `enhanced_prompt` + `main_statement`
3. **Audio generator** creates narration (optional)
4. **Image generator** creates visuals (optional)
5. **Description writer** produces caption + hashtags

LangGraph orchestrates these steps using `OverallState` and workflow nodes that call workers directly.

## Project structure

```
backend/
├── .env.example
├── QUICK_START.md
├── requirements.txt
└── src/
    ├── main.py
    ├── app.py
    ├── agent/
    │   ├── configuration.py
    │   ├── graph.py
    │   ├── nodes.py
    │   ├── state.py
    │   └── prompts.py
    ├── workers/
    │   ├── prompt_enhancer.py
    │   ├── audio_generator.py
    │   ├── image_generator.py
    │   └── description_writer.py
    └── tools/
        ├── user_request_parser.py
        ├── json_parser.py
        └── error_classification.py
```

## Configuration

Set in `backend/.env` (see `.env.example`):

```env
DEEPSEEK_API_KEY=your_key
WRITER_MODEL=deepseek-chat
OUTPUT_DIR=outputs
LOG_LEVEL=INFO
```

## Requirements

- Python 3.10+
- DeepSeek API key (text generation)
- OpenAI API key (TTS)
- Replicate API token (image generation)
- Internet access for Replicate and OpenAI TTS

## License

See `LICENSE`.