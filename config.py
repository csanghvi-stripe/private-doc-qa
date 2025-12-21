"""
Private Doc Q&A - Configuration
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
RUNNERS_DIR = BASE_DIR / "runners" / "macos-arm64"
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = DATA_DIR / "index"
DEFAULT_DOCS_DIR = DATA_DIR / "docs"

# Model files (adjust based on what you download)
LFM2_TEXT_MODEL = MODELS_DIR / "LFM2-1.2B-Q4_K_M.gguf"
LFM2_AUDIO_MODEL = MODELS_DIR / "LFM2-Audio-1.5B-Q8_0.gguf"
LFM2_AUDIO_ENCODER = MODELS_DIR / "mmproj-audioencoder-LFM2-Audio-1.5B-Q8_0.gguf"
LFM2_AUDIO_DECODER = MODELS_DIR / "audiodecoder-LFM2-Audio-1.5B-Q8_0.gguf"

# Embedding model (using sentence-transformers)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Small, fast, good enough
EMBEDDING_DIM = 384

# Chunking settings
CHUNK_SIZE = 500        # tokens
CHUNK_OVERLAP = 50      # tokens overlap between chunks

# RAG settings
TOP_K_RESULTS = 5       # Number of chunks to retrieve
MIN_CONFIDENCE = 0.1    # Minimum similarity score to include

# LLM settings
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.3
CONTEXT_TEMPLATE = """You are a helpful assistant answering questions based on the user's private documents.
Use ONLY the provided context to answer. If the answer is not in the context, say "I couldn't find that information in your documents."
Always cite which document(s) you used.

Context:
{context}

Question: {question}

Answer:"""

# Audio settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_DURATION = 4  # seconds

# Supported file types
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md', '.rtf'}
