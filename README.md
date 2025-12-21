# Private Doc Q&A

**100% on-device document intelligence** powered by [Liquid AI's LFM2](https://www.liquid.ai/).

> Ask questions about your private documents using voice or text. All processing happens locally - nothing is ever uploaded.

```
┌─────────────────────────────────────────────────────────────┐
│                    Private Doc Q&A                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📁 Your Documents (on-device only)                         │
│  ├── 📄 2024_W2_Google.pdf                                  │
│  ├── 📄 Apartment_Lease.pdf                                 │
│  └── 📄 Employment_Contract.pdf                             │
│                                                              │
│  💬 "What's my total W2 income for 2024?"                   │
│                                                              │
│  🤖 Based on your W-2 documents:                            │
│     • Total wages: $277,500                                  │
│     • Federal tax withheld: $64,200                         │
│                                                              │
│  📎 Sources: 2024_W2_Google.pdf, 2024_W2_Stripe.pdf         │
│                                                              │
│  🔒 100% on-device • Never uploaded • Works offline         │
└─────────────────────────────────────────────────────────────┘
```

## Why This Exists

Some documents are too sensitive for cloud AI:
- **Tax documents** - W-2s, 1099s, SSNs → identity theft risk
- **Medical records** - Lab results, prescriptions → HIPAA-level sensitive  
- **Legal contracts** - Employment terms, NDAs → confidential terms
- **Financial docs** - Bank statements, investments → material info

This tool lets you query your private documents with AI, while keeping everything on your device.

## Features

| Feature | Description |
|---------|-------------|
| **100% Local** | Nothing ever leaves your device. No API keys needed. |
| **Voice Input** | Ask questions by speaking (LFM2-Audio) |
| **Multi-Doc RAG** | Search across all your documents at once |
| **Source Citations** | Every answer shows which document it came from |
| **Offline Ready** | Works without internet after initial setup |

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/private-doc-qa.git
cd private-doc-qa
python setup.py
```

### 2. Download Models

Download from HuggingFace and place in `models/`:

| Model | Size | Purpose |
|-------|------|---------|
| [LFM2-1.2B-Q4_K_M.gguf](https://huggingface.co/LiquidAI/LFM2-1.2B-GGUF) | ~730 MB | Text generation |
| [LFM2-Audio-1.5B-Q8_0.gguf](https://huggingface.co/LiquidAI/LFM2-Audio-1.5B-GGUF) | ~1.2 GB | Voice input |
| Audio encoder/decoder | ~670 MB | Voice processing |

Also download the llama.cpp runner from the same HuggingFace repo.

### 3. Add Your Documents

```bash
cp ~/Documents/taxes/*.pdf data/docs/
cp ~/Documents/contracts/*.pdf data/docs/
```

Supported formats: PDF, DOCX, DOC, TXT, MD

### 4. Run

```bash
python main.py --index
```

## Usage

### Interactive Mode

```bash
python main.py
```

```
🔒 Private Doc Q&A
==================================================

💬 You: What's my total income for 2024?

🤖 Based on your W-2 documents:
   • Google: $185,000
   • Stripe: $92,500 (partial year)
   • Total: $277,500

📎 Sources (87% confidence):
   📄 2024_W2_Google.pdf (Page 1)
   📄 2024_W2_Stripe.pdf (Page 1)
```

### Commands

| Command | Description |
|---------|-------------|
| `/index` | Index documents from folder |
| `/docs` | Show indexed documents |
| `/voice` | Use voice input |
| `/clear` | Clear the index |
| `/quit` | Exit |

### Command Line Options

```bash
# Specify custom docs folder
python main.py --docs ~/Documents/taxes

# Auto-index on startup
python main.py --index

# Use mock LLM for testing (no model needed)
python main.py --mock

# Verbose logging
python main.py -v
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Private Doc Q&A                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  INPUT LAYER                                                             │
│  ┌──────────────┐     ┌──────────────┐                                  │
│  │   Voice 🎤   │     │   Text 💬    │                                  │
│  │  (LFM2-Audio)│     │   (Direct)   │                                  │
│  └──────┬───────┘     └──────┬───────┘                                  │
│         └────────┬───────────┘                                           │
│                  ▼                                                       │
│  DOCUMENT LAYER                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │  PDF/DOCX/TXT → Chunker → Embedder → Vector Store        │           │
│  │                          (MiniLM)    (SQLite+numpy)       │           │
│  └──────────────────────────────────────────────────────────┘           │
│                  │                                                       │
│  INFERENCE LAYER │                                                       │
│                  ▼                                                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  RAG Query   │────►│   LFM2-1.2B  │────►│   Response   │            │
│  │  (top-k)     │     │  (llama.cpp) │     │  + Citations │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
private-doc-qa/
├── main.py                 # Entry point
├── setup.py                # Setup script
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
│
├── core/
│   ├── document_store.py   # Document indexing
│   ├── rag_engine.py       # Retrieval engine
│   ├── llm_engine.py       # LFM2 text generation
│   └── audio_engine.py     # Voice input
│
├── parsers/
│   ├── pdf_parser.py       # PDF extraction
│   ├── docx_parser.py      # Word extraction
│   └── text_parser.py      # TXT/MD extraction
│
├── ui/
│   └── cli.py              # Terminal interface
│
├── models/                 # GGUF model files
├── runners/                # llama.cpp binaries
└── data/
    ├── docs/               # Your documents
    └── index/              # Vector index
```

## Requirements

- **macOS** with Apple Silicon (M1/M2/M3/M4)
- **8GB+ RAM** (16GB recommended)
- **Python 3.10+**
- ~3GB disk space for models

## Use Cases

### Tax Preparation
```
> What's my total income across all W-2s?
> How much did I contribute to my HSA?
> What charitable donations can I claim?
```

### Medical Records
```
> What was my A1C trend over the last 2 years?
> What medications am I currently prescribed?
> What vaccinations am I due for?
```

### Legal & Contracts
```
> When does my lease expire?
> What's the early termination penalty?
> What's my non-compete clause?
```

### Business Documents
```
> What's my vested equity percentage?
> When is the next board meeting?
> What were the Q3 revenue numbers?
```

## Privacy & Security

- **100% on-device**: All processing happens locally using LFM2 models
- **No API calls**: No data is ever sent to any cloud service
- **No telemetry**: Zero analytics or tracking
- **Offline capable**: Works without internet after initial setup
- **You own your data**: Documents and index stay in `data/`

## Troubleshooting

### "Model not found"
Ensure GGUF files are in `models/` directory. Run `python setup.py` to verify.

### "llama.cpp runner not found"
Download the macOS ARM64 runner from HuggingFace and place in `runners/macos-arm64/`.

### "Audio model not available"
Voice input requires additional audio model files. Text input works without them.

### Testing without models
Use `--mock` flag to test the app without downloading models:
```bash
python main.py --mock
```

## License

MIT License - See LICENSE for details.

## Acknowledgments

- [Liquid AI](https://www.liquid.ai/) for LFM2 models
- [llama.cpp](https://github.com/ggml-org/llama.cpp) for efficient local inference
- [sentence-transformers](https://www.sbert.net/) for embeddings
