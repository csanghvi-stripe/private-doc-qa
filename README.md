# Private Doc Q&A

<div align="center">

![Private Doc Q&A](https://img.shields.io/badge/100%25-On_Device-green?style=for-the-badge)
![Privacy First](https://img.shields.io/badge/Privacy-First-blue?style=for-the-badge)
![Powered by LFM2](https://img.shields.io/badge/Powered_by-Liquid_AI-purple?style=for-the-badge)

**Ask questions about your private documents using voice or text.**  
**All processing happens locally — nothing is ever uploaded.**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture) • [FAQ](#faq)

</div>

---

## The Problem

You have sensitive documents — tax returns, medical records, legal contracts, financial statements — and you want to query them with AI. But:

- **ChatGPT/Claude**: You're (rightfully) scared to upload W-2s with your SSN
- **Notion AI**: Still cloud-based, still a privacy concern
- **Local PDF readers**: No intelligence, just Ctrl+F
- **Enterprise RAG solutions**: $50K+ and require IT teams

**Private Doc Q&A solves this.** Run state-of-the-art AI models entirely on your Mac. Your documents never leave your device. Ever.

---

## Features

### 🔒 100% On-Device Processing
Every computation happens locally using [Liquid AI's LFM2](https://www.liquid.ai/) models. No API keys. No cloud calls. No telemetry. Works offline after initial setup.

### 🎤 Voice & Text Input
Ask questions by typing or speaking. LFM2-Audio transcribes your voice locally with ~300ms latency.

### 📄 Multi-Document Search
Index entire folders of documents. Ask questions that span multiple files:
> "What's my total income across all W-2s?"

### 📎 Source Citations
Every answer includes which document(s) it came from, with page numbers and confidence scores. Verify anything instantly.

### ⚡ Fast Retrieval
Semantic search using local embeddings (MiniLM). Find relevant information in milliseconds, even across hundreds of documents.

### 🖥️ Native Mac App
Beautiful Tauri-based desktop app with drag-and-drop, keyboard shortcuts, and native macOS integration.

---

## Use Cases

<details>
<summary><b>💰 Tax Preparation</b></summary>

```
Documents: W-2s, 1099s, HSA statements, mortgage interest, charitable donations

Questions you can ask:
• "What was my total income across all employers?"
• "How much did I contribute to my HSA this year?"
• "What's my total student loan interest paid?"
• "List all my charitable donations over $250"
• "What's my capital gains from stock sales?"
```

**Why local matters:** SSNs, income details, and employer information are prime targets for identity theft.
</details>

<details>
<summary><b>🏥 Medical Records</b></summary>

```
Documents: Lab results, prescription history, doctor's notes, insurance EOBs

Questions you can ask:
• "What was my A1C trend over the last 2 years?"
• "What medications am I currently prescribed?"
• "What vaccinations am I due for?"
• "Summarize my last cardiology visit"
• "What's my family medical history?"
```

**Why local matters:** HIPAA exists for a reason. Medical records are among the most sensitive personal data.
</details>

<details>
<summary><b>⚖️ Legal & Contracts</b></summary>

```
Documents: Leases, employment contracts, NDAs, divorce decrees, HOA docs

Questions you can ask:
• "When does my lease expire?"
• "What's the early termination penalty?"
• "What's my non-compete clause?"
• "What are my stock vesting terms?"
• "What's covered under my homeowner's insurance?"
```

**Why local matters:** Active legal matters, confidential employment terms, and binding agreements shouldn't be uploaded anywhere.
</details>

<details>
<summary><b>💼 Business & Finance</b></summary>

```
Documents: Term sheets, cap tables, board minutes, investment statements

Questions you can ask:
• "What's my diluted ownership after Series B?"
• "What were the Q3 revenue numbers?"
• "When is my next board meeting?"
• "What's my total 401k balance?"
• "Compare my investment returns across accounts"
```

**Why local matters:** Material non-public information, NDA-protected documents, and insider knowledge require strict confidentiality.
</details>

---

## Screenshots

```
┌─────────────────────────────────────────────────────────────────────┐
│  Private Doc Q&A                                        ─  □  ×    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📁 Documents (4 indexed)                              [+ Add]     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 📄 2024_W2_Google.pdf                    12 chunks   ✓     │   │
│  │ 📄 2024_W2_Stripe.pdf                     8 chunks   ✓     │   │
│  │ 📄 Apartment_Lease.pdf                   24 chunks   ✓     │   │
│  │ 📄 Employment_Contract.pdf               18 chunks   ✓     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ───────────────────────────────────────────────────────────────   │
│                                                                     │
│  💬 What's my total W2 income for 2024?                            │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🤖 Based on your W-2 documents:                              │   │
│  │                                                               │   │
│  │    • Google: $185,000                                        │   │
│  │    • Stripe: $92,500 (partial year)                          │   │
│  │    • Total: $277,500                                         │   │
│  │                                                               │   │
│  │ 📎 Sources:                                                  │   │
│  │    2024_W2_Google.pdf (p1) · 2024_W2_Stripe.pdf (p1)        │   │
│  │    Confidence: 92%                                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐  🎤  │
│  │ Ask a question...                                        │      │
│  └─────────────────────────────────────────────────────────┘      │
│                                                                     │
│  🔒 100% on-device  •  Never uploaded  •  Works offline            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| macOS | 12+ | Apple Silicon (M1/M2/M3/M4) |
| RAM | 8GB+ | 16GB recommended |
| Python | 3.10+ | For backend |
| Node.js | 18+ | For desktop app |
| Rust | Latest | For Tauri |
| Disk Space | ~5GB | Models + app |

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/private-doc-qa.git
cd private-doc-qa
```

### Step 2: Install Rust (if needed)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### Step 3: Run Setup

```bash
python setup.py
```

This will:
- Create necessary directories
- Install Python dependencies
- Verify your environment
- Tell you what models to download

### Step 4: Download Models

Download from HuggingFace and place in `models/`:

| Model | Size | Download |
|-------|------|----------|
| LFM2-1.2B-Q4_K_M.gguf | 730 MB | [HuggingFace](https://huggingface.co/LiquidAI/LFM2-1.2B-GGUF) |
| LFM2-Audio-1.5B-Q8_0.gguf | 1.2 GB | [HuggingFace](https://huggingface.co/LiquidAI/LFM2-Audio-1.5B-GGUF) |
| mmproj-audioencoder-*.gguf | 317 MB | Same repo |
| audiodecoder-*.gguf | 358 MB | Same repo |
| llama-cli (runner) | ~5 MB | Same repo, `/runners` folder |

### Step 5: Build Desktop App

```bash
cd desktop
npm install
npm run tauri build
```

The built app will be in `desktop/src-tauri/target/release/bundle/`.

### Step 6: Run

```bash
# Desktop app (development)
cd desktop && npm run tauri dev

# Or CLI mode
python main.py --index
```

---

## Usage

### Desktop App

1. **Launch** the app from Applications or `npm run tauri dev`
2. **Add documents** by dragging files into the window or clicking "+ Add"
3. **Wait for indexing** (progress shown in real-time)
4. **Ask questions** by typing or clicking the 🎤 microphone
5. **View sources** by clicking on citations to open the original document

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘ + N` | New question |
| `⌘ + O` | Add documents |
| `⌘ + K` | Focus search |
| `⌘ + M` | Toggle voice input |
| `⌘ + ,` | Settings |
| `Esc` | Cancel/Clear |

### CLI Mode

```bash
# Interactive mode
python main.py

# With custom docs folder
python main.py --docs ~/Documents/taxes

# Auto-index on startup
python main.py --index

# Test without models
python main.py --mock

# Verbose logging
python main.py -v
```

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Private Doc Q&A                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      TAURI DESKTOP APP                               │    │
│  │                                                                      │    │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐ │    │
│  │  │  React UI   │◄──►│ Rust/Tauri  │◄──►│   Python Backend        │ │    │
│  │  │ (Frontend)  │IPC │  (Bridge)   │JSON│   (AI Processing)       │ │    │
│  │  └─────────────┘    └─────────────┘    └─────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│  ════════════════════════════════════╪═══════════════════════════════════   │
│                                      │                                       │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │                         PYTHON BACKEND                                 │  │
│  │                                                                        │  │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐  │  │
│  │  │ Audio Engine │   │ Document     │   │ RAG Engine               │  │  │
│  │  │              │   │ Store        │   │                          │  │  │
│  │  │ • Record     │   │              │   │ • Embed query            │  │  │
│  │  │ • Transcribe │   │ • Parse      │   │ • Vector search          │  │  │
│  │  │   (LFM2-     │   │ • Chunk      │   │ • Build context          │  │  │
│  │  │    Audio)    │   │ • Embed      │   │ • Track sources          │  │  │
│  │  │              │   │ • Index      │   │                          │  │  │
│  │  └──────┬───────┘   └──────┬───────┘   └────────────┬─────────────┘  │  │
│  │         │                  │                        │                 │  │
│  │         │                  │                        │                 │  │
│  │         │           ┌──────▼───────┐                │                 │  │
│  │         │           │ Vector Store │                │                 │  │
│  │         │           │ (SQLite +    │◄───────────────┘                 │  │
│  │         │           │  NumPy)      │                                  │  │
│  │         │           └──────────────┘                                  │  │
│  │         │                                                             │  │
│  │         │           ┌──────────────┐                                  │  │
│  │         └──────────►│ LLM Engine   │                                  │  │
│  │                     │              │                                  │  │
│  │   Question ────────►│ • LFM2-1.2B  │──────► Answer + Citations       │  │
│  │   + Context         │ • llama.cpp  │                                  │  │
│  │                     │              │                                  │  │
│  │                     └──────────────┘                                  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
private-doc-qa/
├── README.md                    # This file
├── setup.py                     # Setup script
├── requirements.txt             # Python dependencies
├── main.py                      # CLI entry point
├── config.py                    # Configuration
│
├── core/                        # Python backend
│   ├── document_store.py        # Indexing & storage
│   ├── rag_engine.py            # Retrieval
│   ├── llm_engine.py            # LFM2 inference
│   └── audio_engine.py          # Voice input
│
├── parsers/                     # Document parsers
│   ├── pdf_parser.py
│   ├── docx_parser.py
│   └── text_parser.py
│
├── ui/                          # CLI interface
│   └── cli.py
│
├── desktop/                     # Tauri Mac app
│   ├── src/                     # React frontend
│   │   ├── App.tsx
│   │   ├── components/
│   │   └── hooks/
│   ├── src-tauri/               # Rust backend
│   │   ├── src/main.rs
│   │   └── Cargo.toml
│   └── package.json
│
├── models/                      # AI models (git-ignored)
└── data/                        # User data (git-ignored)
    ├── docs/
    └── index/
```

---

## Performance

| Operation | Latency | Hardware |
|-----------|---------|----------|
| Index 1 page | ~2s | M1 Pro |
| Voice transcription | ~300ms | M1 Pro |
| Vector search | <50ms | Any |
| Answer generation | 500-1500ms | M1 Pro |
| **Total query** | **<2s** | M1 Pro |

Memory usage: ~4GB when running

---

## Privacy Guarantee

| Data | Location | Uploaded? |
|------|----------|-----------|
| Documents | `data/docs/` | ❌ Never |
| Index | `data/index/` | ❌ Never |
| Queries | Memory only | ❌ Never |
| Audio | Temp file, deleted | ❌ Never |
| Answers | Memory only | ❌ Never |

**Zero network calls.** Works in airplane mode.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Model not found | Download GGUFs to `models/` |
| Runner not found | Download llama-cli to `runners/macos-arm64/` |
| Out of memory | Close apps, use Q4 quantization |
| Slow indexing | Normal for large PDFs with tables |
| No voice input | Check microphone permissions |

Test without models: `python main.py --mock`

---

## Roadmap & Future Improvements

### Model & Accuracy
| Improvement | Description | Impact |
|-------------|-------------|--------|
| Larger LFM2 models | Upgrade to 3B+ parameter variants when available | Higher quality answers |
| Reranking | Add cross-encoder reranking after initial retrieval | Better source selection |
| Query expansion | Rephrase queries for better semantic matching | Improved recall |
| Hybrid search | Combine semantic + keyword (BM25) search | Catch exact matches |
| Better chunking | Semantic chunking instead of fixed-size | More coherent context |

### Performance & Latency
| Improvement | Description | Impact |
|-------------|-------------|--------|
| GPU offloading | Use `-ngl` flag for Metal acceleration | 2-3x faster inference |
| Embedding cache | Cache document embeddings to disk | Faster reindexing |
| Streaming responses | Stream LLM output token-by-token | Better perceived latency |
| Batch embeddings | Process multiple chunks in parallel | Faster indexing |

### Storage & Scalability
| Improvement | Description | Impact |
|-------------|-------------|--------|
| SQLite + vec extension | Replace NumPy with sqlite-vec | Better for large collections |
| LanceDB | Embedded vector DB with disk-backed storage | Scale to 100K+ docs |
| Incremental indexing | Only reindex changed documents | Faster updates |
| Index compression | Quantize embeddings (int8) | 4x smaller index |

### App Experience
| Improvement | Description | Impact |
|-------------|-------------|--------|
| Document preview | View source snippets in context | Easier verification |
| Conversation history | Persist chat sessions | Resume later |
| Export answers | Copy/export to Markdown, PDF | Share findings |
| Keyboard shortcuts | Full keyboard navigation | Power user efficiency |
| Multi-language | Support non-English documents | Broader use cases |

### Reliability
| Improvement | Description | Impact |
|-------------|-------------|--------|
| Error recovery | Graceful handling of corrupt files | Better UX |
| Progress indicators | Show indexing/generation progress | User confidence |
| Health checks | Verify model/backend status on startup | Fewer surprises |
| Logging | Structured logs for debugging | Easier troubleshooting |

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Acknowledgments

- [Liquid AI](https://www.liquid.ai/) - LFM2 models
- [llama.cpp](https://github.com/ggml-org/llama.cpp) - Local inference
- [Tauri](https://tauri.app/) - Desktop framework
- [sentence-transformers](https://www.sbert.net/) - Embeddings

---

<div align="center">

**Built with ❤️ for privacy**

</div>
