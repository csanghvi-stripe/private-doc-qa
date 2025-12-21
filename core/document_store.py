"""
Document Store - Load, chunk, embed, and index documents
All processing happens locally on-device.
"""
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, EMBEDDING_DIM,
    INDEX_DIR, SUPPORTED_EXTENSIONS
)
from parsers import parse_pdf, parse_docx, parse_text

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """A chunk of a document with its embedding"""
    id: str                     # Unique chunk ID
    source: str                 # Original filename
    text: str                   # Chunk text content
    page: Optional[int]         # Page number (if applicable)
    chunk_index: int            # Position in document
    embedding: Optional[List[float]] = None  # Vector embedding


class DocumentStore:
    """
    Manages document ingestion, chunking, and vector storage.
    Everything is stored locally in SQLite + numpy arrays.
    """
    
    def __init__(self, index_path: Optional[Path] = None):
        self.index_path = index_path or INDEX_DIR
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.chunks: List[DocumentChunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self.embedder = None
        
        # Load existing index if present
        self._load_index()
    
    def _get_embedder(self):
        """Lazy-load the embedding model"""
        if self.embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
                self.embedder = SentenceTransformer(EMBEDDING_MODEL)
            except ImportError:
                raise ImportError(
                    "Please install sentence-transformers: "
                    "pip install sentence-transformers"
                )
        return self.embedder
    
    def add_document(self, file_path: Path) -> int:
        """
        Add a document to the store.
        Returns the number of chunks created.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Check if document already indexed
        doc_hash = self._file_hash(file_path)
        if self._is_indexed(file_path.name, doc_hash):
            logger.info(f"Document already indexed: {file_path.name}")
            return 0
        
        # Parse document based on type
        logger.info(f"Parsing document: {file_path.name}")
        parsed = self._parse_document(file_path)
        
        if 'error' in parsed:
            logger.error(f"Failed to parse {file_path.name}: {parsed['error']}")
            return 0
        
        # Chunk the document
        new_chunks = self._chunk_document(parsed)
        logger.info(f"Created {len(new_chunks)} chunks from {file_path.name}")
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embedder = self._get_embedder()
        texts = [c.text for c in new_chunks]
        vectors = embedder.encode(texts, show_progress_bar=True)
        
        # Add to store
        for chunk, vector in zip(new_chunks, vectors):
            chunk.embedding = vector.tolist()
            self.chunks.append(chunk)
        
        # Update embedding matrix
        self._rebuild_embedding_matrix()
        
        # Save index
        self._save_index()
        
        return len(new_chunks)
    
    def add_folder(self, folder_path: Path) -> Dict[str, int]:
        """
        Add all supported documents from a folder.
        Returns dict of {filename: num_chunks}
        """
        folder_path = Path(folder_path)
        if not folder_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {folder_path}")
        
        results = {}
        for file_path in folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                try:
                    num_chunks = self.add_document(file_path)
                    results[file_path.name] = num_chunks
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {e}")
                    results[file_path.name] = -1
        
        return results
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks using vector similarity.
        Returns list of {chunk, score, source}
        """
        if not self.chunks or self.embeddings is None:
            return []
        
        # Embed the query
        embedder = self._get_embedder()
        query_vector = embedder.encode([query])[0]
        
        # Compute cosine similarity
        similarities = self._cosine_similarity(query_vector, self.embeddings)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            score = float(similarities[idx])
            results.append({
                'chunk': chunk,
                'score': score,
                'source': chunk.source,
                'text': chunk.text,
                'page': chunk.page
            })
        
        return results
    
    def get_sources(self) -> List[str]:
        """Get list of indexed document names"""
        return list(set(c.source for c in self.chunks))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        sources = self.get_sources()
        return {
            'num_documents': len(sources),
            'num_chunks': len(self.chunks),
            'documents': sources
        }
    
    def clear(self):
        """Clear the entire index"""
        self.chunks = []
        self.embeddings = None
        
        # Remove saved files
        index_file = self.index_path / "chunks.json"
        embeddings_file = self.index_path / "embeddings.npy"
        
        if index_file.exists():
            index_file.unlink()
        if embeddings_file.exists():
            embeddings_file.unlink()
        
        logger.info("Index cleared")
    
    def remove_document(self, source_name: str):
        """Remove a document from the index"""
        self.chunks = [c for c in self.chunks if c.source != source_name]
        self._rebuild_embedding_matrix()
        self._save_index()
        logger.info(f"Removed document: {source_name}")
    
    # --- Private methods ---
    
    def _parse_document(self, file_path: Path) -> Dict[str, Any]:
        """Parse document based on file type"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return parse_pdf(file_path)
        elif suffix in ['.docx', '.doc']:
            return parse_docx(file_path)
        elif suffix in ['.txt', '.md', '.rtf']:
            return parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    def _chunk_document(self, parsed: Dict[str, Any]) -> List[DocumentChunk]:
        """Split document into overlapping chunks"""
        text = parsed['text']
        source = parsed['source']
        
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        start = 0
        chunk_index = 0
        
        while start < len(words):
            end = min(start + CHUNK_SIZE, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            # Try to detect page number from text
            page = self._detect_page(chunk_text)
            
            chunk_id = f"{source}_{chunk_index}_{hashlib.md5(chunk_text.encode()).hexdigest()[:8]}"
            
            chunks.append(DocumentChunk(
                id=chunk_id,
                source=source,
                text=chunk_text,
                page=page,
                chunk_index=chunk_index
            ))
            
            # Move forward with overlap
            start = end - CHUNK_OVERLAP
            chunk_index += 1
            
            # Prevent infinite loop
            if start >= len(words) - CHUNK_OVERLAP:
                break
        
        return chunks
    
    def _detect_page(self, text: str) -> Optional[int]:
        """Try to detect page number from chunk text"""
        import re
        match = re.search(r'\[Page (\d+)\]', text)
        if match:
            return int(match.group(1))
        return None
    
    def _file_hash(self, file_path: Path) -> str:
        """Compute file hash for change detection"""
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()
    
    def _is_indexed(self, source: str, file_hash: str) -> bool:
        """Check if document is already indexed with same hash"""
        # Load hash cache
        hash_file = self.index_path / "hashes.json"
        if hash_file.exists():
            hashes = json.loads(hash_file.read_text())
            return hashes.get(source) == file_hash
        return False
    
    def _save_hash(self, source: str, file_hash: str):
        """Save document hash"""
        hash_file = self.index_path / "hashes.json"
        hashes = {}
        if hash_file.exists():
            hashes = json.loads(hash_file.read_text())
        hashes[source] = file_hash
        hash_file.write_text(json.dumps(hashes))
    
    def _cosine_similarity(self, query: np.ndarray, docs: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and all documents"""
        query_norm = query / (np.linalg.norm(query) + 1e-8)
        docs_norm = docs / (np.linalg.norm(docs, axis=1, keepdims=True) + 1e-8)
        return np.dot(docs_norm, query_norm)
    
    def _rebuild_embedding_matrix(self):
        """Rebuild numpy embedding matrix from chunks"""
        if not self.chunks:
            self.embeddings = None
            return
        
        vectors = [c.embedding for c in self.chunks if c.embedding]
        if vectors:
            self.embeddings = np.array(vectors)
        else:
            self.embeddings = None
    
    def _save_index(self):
        """Save index to disk"""
        # Save chunks (without embeddings in JSON for smaller size)
        chunks_data = []
        for chunk in self.chunks:
            data = asdict(chunk)
            data['embedding'] = None  # Don't save embeddings in JSON
            chunks_data.append(data)
        
        chunks_file = self.index_path / "chunks.json"
        chunks_file.write_text(json.dumps(chunks_data, indent=2))
        
        # Save embeddings as numpy array
        if self.embeddings is not None:
            embeddings_file = self.index_path / "embeddings.npy"
            np.save(embeddings_file, self.embeddings)
        
        logger.info(f"Saved index: {len(self.chunks)} chunks")
    
    def _load_index(self):
        """Load index from disk"""
        chunks_file = self.index_path / "chunks.json"
        embeddings_file = self.index_path / "embeddings.npy"
        
        if chunks_file.exists():
            chunks_data = json.loads(chunks_file.read_text())
            self.chunks = [DocumentChunk(**c) for c in chunks_data]
            logger.info(f"Loaded {len(self.chunks)} chunks from index")
        
        if embeddings_file.exists():
            self.embeddings = np.load(embeddings_file)
            
            # Re-associate embeddings with chunks
            if len(self.chunks) == len(self.embeddings):
                for chunk, emb in zip(self.chunks, self.embeddings):
                    chunk.embedding = emb.tolist()
            
            logger.info(f"Loaded embeddings: {self.embeddings.shape}")


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    store = DocumentStore()
    print(f"Index stats: {store.get_stats()}")
