# Private Doc Q&A - Claude Code Context

## Project Overview
A 100% on-device document Q&A application using Liquid AI's LFM2 models. Users can query their private documents (tax forms, medical records, legal contracts) using voice or text, with all processing happening locally.

## Tech Stack
- **Desktop App**: Tauri v2 + React + TypeScript + Tailwind CSS
- **Backend**: Python 3.10+ with JSON-RPC over stdin/stdout
- **Text LLM**: LFM2-1.2B via `llama-cli` (brew install llama.cpp)
- **Voice**: LFM2-Audio via `llama-lfm2-audio` (optional)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Store**: NumPy + JSON (no external DB)

## Directory Structure
```
private-doc-qa/
├── desktop/                 # Tauri app
│   ├── src/                 # React frontend
│   │   ├── App.tsx          # Main component, state management
│   │   └── components/      # UI components
│   ├── src-tauri/           # Rust backend
│   │   ├── src/main.rs      # Tauri commands, Python IPC
│   │   └── tauri.conf.json  # App config
│   └── package.json
├── core/                    # Python backend modules
│   ├── document_store.py    # Chunking, embeddings, vector search
│   ├── rag_engine.py        # Retrieval-augmented generation
│   ├── llm_engine.py        # LFM2 text generation via llama-cli
│   └── audio_engine.py      # Voice transcription via llama-lfm2-audio
├── parsers/                 # Document parsers
│   ├── pdf_parser.py        # Uses pdfplumber for tables
│   ├── docx_parser.py       # Uses python-docx
│   └── text_parser.py       # TXT/MD files
├── backend_server.py        # JSON-RPC server for Tauri IPC
├── config.py                # All configuration constants
├── main.py                  # CLI entry point
└── models/                  # GGUF model files (user downloads)
```

## Key Architecture Decisions

### Two Separate Runners
1. **Text Generation** (`llama-cli`): Installed via `brew install llama.cpp`, uses LFM2-1.2B-Q4_K_M.gguf
2. **Audio Transcription** (`llama-lfm2-audio`): In `runners/macos-arm64/lfm2-audio-macos-arm64/`, uses LFM2-Audio-1.5B

### Tauri ↔ Python Communication
- Tauri spawns `python3 backend_server.py --json-mode`
- Communication via JSON over stdin/stdout
- Commands: `init`, `add_documents`, `ask`, `remove_document`, `voice_input`

### Prompt Handling
- Multi-line prompts written to temp file, passed via `-f` flag to llama-cli
- Avoids shell escaping issues with special characters

## Common Commands
```bash
# Development
cd desktop && npm run tauri dev

# Test Python backend directly
echo '{"command": "init"}' | python3 backend_server.py --json-mode

# Test llama-cli
llama-cli -m models/LFM2-1.2B-Q4_K_M.gguf -p "Hello" -n 20

# Build for production
cd desktop && npm run tauri build
```

## Current Issues / TODOs

1. **Backend starts twice** - `init_backend` called twice on app start
2. **Document status not updating** - UI shows "pending" even after indexing
3. **Audio not tested** - Voice input path needs verification
4. **No error toasts** - Errors only show in status bar
5. **No document preview** - Can't view source snippets in context

## Configuration (config.py)

Key settings:
- `CHUNK_SIZE = 500` - Tokens per chunk
- `CHUNK_OVERLAP = 50` - Overlap between chunks
- `TOP_K_RESULTS = 5` - Chunks to retrieve
- `MAX_NEW_TOKENS = 512` - Max response length
- `TEMPERATURE = 0.3` - LLM temperature

Paths:
- `RUNNERS_DIR` - For standard llama-cli
- `AUDIO_RUNNERS_DIR` - For llama-lfm2-audio
- `MODELS_DIR` - GGUF model files

## React Component Structure
```
App.tsx (state management)
├── Header.tsx (title bar)
├── DocumentList.tsx (sidebar, indexed docs)
├── DropZone.tsx (file picker via Tauri dialog)
├── ChatArea.tsx (messages, sources)
├── InputArea.tsx (text input, voice button)
└── StatusBar.tsx (connection status, doc count)
```

## Debugging Tips

1. **Check Tauri logs**: Terminal where `npm run tauri dev` runs
2. **Check browser console**: Right-click app → Inspect → Console
3. **Test backend standalone**: `python3 backend_server.py --json-mode`
4. **Test LLM directly**: `llama-cli -m models/... -p "test" -n 20`

## Code Style

- Python: Use logging, not print statements
- TypeScript: Functional components with hooks
- Rust: Minimal, just IPC bridge to Python
- All responses include source citations

## Privacy Guarantees

- Zero network calls after model download
- All processing on-device
- No telemetry or analytics
- Works in airplane mode
