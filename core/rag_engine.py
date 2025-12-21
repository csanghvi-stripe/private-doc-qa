"""
RAG Engine - Retrieval-Augmented Generation
Handles query processing, context building, and source tracking.
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TOP_K_RESULTS, MIN_CONFIDENCE
from core.document_store import DocumentStore

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from RAG retrieval"""
    context: str                    # Combined context for LLM
    sources: List[Dict[str, Any]]   # Source citations
    confidence: float               # Average confidence score
    num_chunks: int                 # Number of chunks retrieved


class RAGEngine:
    """
    Handles retrieval-augmented generation:
    1. Query → Vector search → Relevant chunks
    2. Chunks → Context window for LLM
    3. Track sources for citations
    """
    
    def __init__(self, document_store: DocumentStore):
        self.store = document_store
    
    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K_RESULTS,
        min_score: float = MIN_CONFIDENCE
    ) -> RetrievalResult:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User's question
            top_k: Maximum number of chunks to retrieve
            min_score: Minimum similarity score threshold
        
        Returns:
            RetrievalResult with context, sources, and confidence
        """
        # Search for relevant chunks
        results = self.store.search(query, top_k=top_k)
        
        # Filter by minimum score
        results = [r for r in results if r['score'] >= min_score]
        
        if not results:
            return RetrievalResult(
                context="",
                sources=[],
                confidence=0.0,
                num_chunks=0
            )
        
        # Build context string
        context_parts = []
        sources = []
        
        for i, result in enumerate(results):
            # Format chunk for context
            source_info = f"[Source: {result['source']}"
            if result['page']:
                source_info += f", Page {result['page']}"
            source_info += "]"
            
            context_parts.append(f"{source_info}\n{result['text']}")
            
            # Track source for citation
            sources.append({
                'document': result['source'],
                'page': result['page'],
                'score': result['score'],
                'snippet': result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
            })
        
        context = "\n\n---\n\n".join(context_parts)
        avg_confidence = sum(r['score'] for r in results) / len(results)
        
        return RetrievalResult(
            context=context,
            sources=sources,
            confidence=avg_confidence,
            num_chunks=len(results)
        )
    
    def format_sources_for_display(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources for user display"""
        if not sources:
            return "No sources found."
        
        lines = []
        seen = set()  # Deduplicate by document
        
        for source in sources:
            doc = source['document']
            if doc in seen:
                continue
            seen.add(doc)
            
            line = f"📄 {doc}"
            if source['page']:
                line += f" (Page {source['page']})"
            line += f" - {source['score']:.0%} match"
            lines.append(line)
        
        return "\n".join(lines)
    
    def get_context_stats(self, result: RetrievalResult) -> Dict[str, Any]:
        """Get statistics about retrieved context"""
        if not result.sources:
            return {
                'num_chunks': 0,
                'num_documents': 0,
                'avg_confidence': 0.0,
                'documents': []
            }
        
        unique_docs = list(set(s['document'] for s in result.sources))
        
        return {
            'num_chunks': result.num_chunks,
            'num_documents': len(unique_docs),
            'avg_confidence': result.confidence,
            'documents': unique_docs
        }


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    store = DocumentStore()
    rag = RAGEngine(store)
    
    # Test retrieval
    result = rag.retrieve("What is the total income?")
    print(f"Retrieved {result.num_chunks} chunks")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Sources:\n{rag.format_sources_for_display(result.sources)}")
