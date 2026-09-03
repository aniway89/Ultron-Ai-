# Ultron AI

A desktop AI assistant with a decoupled **decision layer** and **generation layer**: [Cohere](https://cohere.com/) classifies what a query needs before anything else runs, and [Groq](https://groq.com/) (Llama models) handles the actual chat generation and real-time search summarization. A PyQt5 GUI wraps it, with voice input/output and OS-level automation.

## How it works

```
User (voice or text)
        │
        ▼
 Speech-to-Text (faster-whisper, local, CPU)
        │
        ▼
 Decision Model (Cohere) ── classifies the query into one of:
        │   exit · general · realtime · open · close · play ·
        │   generate image · system · content · google search ·
        │   youtube search · reminder
        │
        ├─► general / realtime  → Chatbot / RealtimeSearchEngine (Groq)
        ├─► open / close / play / system / google search / youtube search
        │                       → Automation (AppOpener, pywhatkit, keyboard, selenium)
        └─► generate image      → Image Generation
        │
        ▼
 Text-to-Speech (edge-tts + pygame)
        │
        ▼
 PyQt5 GUI (status, chat log, mic indicator)
```

Chat history persists in `Data/ChatLog.json`, which is what gives the assistant continuity across sessions rather than a single-turn context window.

## Features

- **Two-model routing** — a lightweight Cohere call decides *what kind* of request it is before spending a Groq call on generation, instead of sending every query through one large prompt.
- **Voice in, voice out** — local speech-to-text via `faster-whisper` (no cloud STT dependency), text-to-speech via `edge-tts`.
- **OS automation** — open/close applications, play media, run Google/YouTube searches, and other system-level actions triggered by natural language.
- **Real-time search** — pulls live web results and summarizes them through Groq rather than relying on static training data.
- **Persistent chat log** — conversation history stored locally in JSON.
- **Desktop GUI** — PyQt5 interface showing assistant status, mic state, and chat.

## Tech stack

| Layer | Tool |
|---|---|
| Decision / intent routing | Cohere (`cohere` SDK) |
| Chat generation & real-time answers | Groq (`groq` SDK) |
| Speech-to-text | `faster-whisper` |
| Text-to-speech | `edge-tts` + `pygame` |
| Automation | `AppOpener`, `pywhatkit`, `keyboard`, `selenium` |
| Web search / parsing | `googlesearch-python`, `beautifulsoup4` |
| GUI | `PyQt5` |

## Setup

```bash
git clone https://github.com/aniway89/Ultron-Ai-.git
cd Ultron-Ai-
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r Requirements.txt
```

> **Note:** `Requirements.txt` currently doesn't list `faster-whisper`, `sounddevice`, or `numpy`, which are required by `SpeechToText.py`. Install them manually for now:
> ```bash
> pip install faster-whisper sounddevice numpy
> ```

Create a `.env` file in the project root:

```env
COHERE_API_KEY=your_cohere_key
GroqAPIKey=your_groq_key
Username=YourName
AssistantName=Ultron
AssistantVoice=en-CA-LiamNeural
```

Run it:

```bash
python Main.py
```

## Known issues

- `Backend/ImageGeneration.py` is referenced by `Main.py` (`from Backend.ImageGeneration import GenerateImages`) but is not present in this repo. Add the module or remove the import before running.
- Windows-only paths are hardcoded in a few places (e.g. `Data\ChatLog.json`), so this won't run as-is on macOS/Linux.
- `AssistantVoice` and other `.env` values aren't documented anywhere else — listed above for now.

## Roadmap

- [ ] Add the missing image generation module
- [ ] Cross-platform path handling
- [ ] Pin dependency versions in `Requirements.txt`

## License

Add a license (MIT is a reasonable default for a portfolio project) — none is currently specified.
