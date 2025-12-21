#!/usr/bin/env python3
"""
Setup script for Private Doc Q&A
Downloads models and configures the environment.
"""
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
RUNNERS_DIR = BASE_DIR / "runners" / "macos-arm64"
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"


def print_header(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print('='*60)


def print_step(msg):
    print(f"\n→ {msg}")


def check_python_version():
    print_step("Checking Python version...")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        sys.exit(1)
    print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor}")


def create_directories():
    print_step("Creating directories...")
    dirs = [MODELS_DIR, RUNNERS_DIR, DATA_DIR, DOCS_DIR, DATA_DIR / "index"]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  📁 {d.relative_to(BASE_DIR)}")


def install_dependencies():
    print_step("Installing Python dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", 
        str(BASE_DIR / "requirements.txt"), "-q"
    ], check=True)
    print("  ✅ Dependencies installed")


def check_models():
    print_step("Checking for models...")
    
    required_models = {
        "LFM2-1.2B (Text)": MODELS_DIR / "LFM2-1.2B-Q4_K_M.gguf",
        "LFM2-Audio": MODELS_DIR / "LFM2-Audio-1.5B-Q8_0.gguf",
        "Audio Encoder": MODELS_DIR / "mmproj-audioencoder-LFM2-Audio-1.5B-Q8_0.gguf",
    }
    
    missing = []
    for name, path in required_models.items():
        if path.exists():
            size = path.stat().st_size / 1e9
            print(f"  ✅ {name}: {size:.1f} GB")
        else:
            print(f"  ❌ {name}: NOT FOUND")
            missing.append(name)
    
    if missing:
        print("\n⚠️  Missing models. Download from HuggingFace:")
        print("   https://huggingface.co/LiquidAI/LFM2-1.2B-GGUF")
        print("   https://huggingface.co/LiquidAI/LFM2-Audio-1.5B-GGUF")
        print("\n   Place GGUF files in: models/")
        return False
    return True


def check_runner():
    print_step("Checking for llama.cpp runner...")
    
    runner_names = ["llama-cli", "llama-cpp", "main", "llama"]
    found = None
    
    # Check in runners directory
    for name in runner_names:
        path = RUNNERS_DIR / name
        if path.exists():
            found = path
            break
    
    # Check if installed globally
    if not found:
        import shutil
        for name in runner_names:
            if shutil.which(name):
                found = Path(shutil.which(name))
                break
    
    if found:
        print(f"  ✅ Runner found: {found}")
        return True
    else:
        print("  ❌ llama.cpp runner NOT FOUND")
        print("\n   Download from:")
        print("   https://huggingface.co/LiquidAI/LFM2-Audio-1.5B-GGUF/tree/main/runners")
        print(f"\n   Place binary in: {RUNNERS_DIR}/")
        return False


def test_embeddings():
    print_step("Testing embedding model...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embedding = model.encode(["test"])
        print(f"  ✅ Embedding model loaded ({embedding.shape[1]} dimensions)")
        return True
    except Exception as e:
        print(f"  ❌ Embedding test failed: {e}")
        return False


def show_usage():
    print_header("Setup Complete!")
    print("""
Quick Start:
-----------
1. Add documents to: data/docs/
   (PDFs, DOCX, TXT, MD files)

2. Run the app:
   python main.py --index

3. Ask questions:
   > What's my total income for 2024?
   > When does my lease expire?
   > /voice  (for voice input)

Commands:
---------
  /index  - Index documents
  /docs   - Show indexed documents  
  /voice  - Voice input
  /clear  - Clear index
  /quit   - Exit

Testing without models:
-----------------------
  python main.py --mock

For more info:
  python main.py --help
""")


def main():
    print_header("Private Doc Q&A - Setup")
    
    check_python_version()
    create_directories()
    install_dependencies()
    
    models_ok = check_models()
    runner_ok = check_runner()
    embeddings_ok = test_embeddings()
    
    print("\n" + "="*60)
    print("  Summary")
    print("="*60)
    print(f"  Python deps: ✅")
    print(f"  Embeddings:  {'✅' if embeddings_ok else '❌'}")
    print(f"  LFM2 models: {'✅' if models_ok else '⚠️  (can use --mock)'}")
    print(f"  llama.cpp:   {'✅' if runner_ok else '⚠️  (can use --mock)'}")
    
    if not models_ok or not runner_ok:
        print("\n⚠️  Some components missing. You can still test with:")
        print("     python main.py --mock")
    
    show_usage()


if __name__ == "__main__":
    main()
