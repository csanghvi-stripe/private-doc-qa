#!/usr/bin/env python3
"""
Backend Server for Private Doc Q&A
Communicates with Tauri via JSON over stdin/stdout.

Usage:
    python backend_server.py --json-mode
"""

import sys
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.document_store import DocumentStore
from core.rag_engine import RAGEngine
from core.llm_engine import LLMEngine, MockLLMEngine
from core.audio_engine import AudioEngine, MockAudioEngine
from config import DEFAULT_DOCS_DIR

# Configure logging to stderr (stdout is for IPC)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class BackendServer:
    """JSON-RPC style server for Tauri communication"""
    
    def __init__(self):
        logger.info("Initializing backend server...")
        
        self.store = DocumentStore()
        self.rag = RAGEngine(self.store)
        
        # Try to load real engines, fall back to mock
        try:
            self.llm = LLMEngine()
            logger.info("LLM engine loaded")
        except Exception as e:
            logger.warning(f"Using mock LLM: {e}")
            self.llm = MockLLMEngine()
        
        try:
            self.audio = AudioEngine()
            if not self.audio.is_available():
                raise RuntimeError("Audio model not available")
            logger.info("Audio engine loaded")
        except Exception as e:
            logger.warning(f"Using mock audio: {e}")
            self.audio = MockAudioEngine()
        
        logger.info("Backend server ready")
    
    def handle_request(self, request: dict) -> dict:
        """Handle a single request and return response"""
        command = request.get("command", "")
        
        try:
            if command == "init":
                return self._handle_init()
            elif command == "add_documents":
                return self._handle_add_documents(request.get("paths", []))
            elif command == "ask":
                return self._handle_ask(request.get("question", ""))
            elif command == "remove_document":
                return self._handle_remove_document(request.get("name", ""))
            elif command == "voice_input":
                return self._handle_voice_input()
            elif command == "get_documents":
                return self._handle_get_documents()
            else:
                return {"success": False, "error": f"Unknown command: {command}"}
        except Exception as e:
            logger.exception(f"Error handling command {command}")
            return {"success": False, "error": str(e)}
    
    def _handle_init(self) -> dict:
        """Initialize and return current state"""
        stats = self.store.get_stats()
        documents = [
            {
                "name": doc,
                "path": "",
                "chunks": 0,  # TODO: track per-doc chunks
                "status": "indexed"
            }
            for doc in stats.get("documents", [])
        ]
        
        return {
            "success": True,
            "data": {
                "documents": documents,
                "llm_ready": self.llm.is_available(),
                "audio_ready": self.audio.is_available()
            }
        }
    

    def _handle_add_documents(self, paths: list) -> dict:
        results = []
        
        for path in paths:
            path = Path(path)
            try:
                if path.is_dir():
                    folder_results = self.store.add_folder(path)
                    for name, chunks in folder_results.items():
                        results.append({
                            "name": name,
                            "path": str(path / name),
                            "chunks": chunks if chunks >= 0 else 0,
                            "status": "indexed" if chunks >= 0 else "error",
                            "error": None if chunks >= 0 else "Failed to index"
                        })
                else:
                    chunks = self.store.add_document(path)
                    results.append({
                        "name": path.name,
                        "path": str(path),
                        "chunks": chunks,
                        "status": "indexed",
                        "error": None
                    })
            except Exception as e:
                logger.error(f"Error adding {path}: {e}")
                results.append({
                    "name": path.name if path else str(path),
                    "path": str(path),
                    "chunks": 0,
                    "status": "error",
                    "error": str(e)
                })
        
        response = {"success": True, "data": {"documents": results}}
        logger.info(f"Returning add_documents response: {response}")  # ADD THIS
        return response

    def _handle_ask(self, question: str) -> dict:
        """Answer a question"""
        if not question.strip():
            return {"success": False, "error": "Empty question"}
        
        # Retrieve context
        result = self.rag.retrieve(question)
        
        if result.num_chunks == 0:
            return {
                "success": True,
                "data": {
                    "answer": "I couldn't find any relevant information in your documents.",
                    "sources": [],
                    "confidence": 0.0
                }
            }
        
        # Generate answer
        answer = self.llm.answer_with_context(question, result.context)
        
        # Format sources
        sources = [
            {
                "document": s["document"],
                "page": s.get("page"),
                "score": s["score"],
                "snippet": s["snippet"]
            }
            for s in result.sources
        ]
        
        return {
            "success": True,
            "data": {
                "answer": answer,
                "sources": sources,
                "confidence": result.confidence
            }
        }
    
    def _handle_remove_document(self, name: str) -> dict:
        """Remove a document from the index"""
        if not name:
            return {"success": False, "error": "No document name provided"}
        
        self.store.remove_document(name)
        return {"success": True, "data": {}}
    
    def _handle_voice_input(self) -> dict:
        """Record and transcribe voice input"""
        try:
            transcription = self.audio.record_and_transcribe()
            return {
                "success": True,
                "data": {"transcription": transcription}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_get_documents(self) -> dict:
        """Get list of indexed documents"""
        stats = self.store.get_stats()
        documents = [
            {
                "name": doc,
                "path": "",
                "chunks": 0,
                "status": "indexed"
            }
            for doc in stats.get("documents", [])
        ]
        return {"success": True, "data": {"documents": documents}}
    
    def run(self):
        """Main loop - read JSON from stdin, write JSON to stdout"""
        logger.info("Backend server running, waiting for commands...")
        
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = self.handle_request(request)
            except json.JSONDecodeError as e:
                response = {"success": False, "error": f"Invalid JSON: {e}"}
            except Exception as e:
                response = {"success": False, "error": str(e)}
            
            # Write response
            print(json.dumps(response), flush=True)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Private Doc Q&A Backend Server")
    parser.add_argument("--json-mode", action="store_true", help="Run in JSON IPC mode")
    args = parser.parse_args()
    
    if args.json_mode:
        server = BackendServer()
        server.run()
    else:
        print("Use --json-mode to run as IPC server")
        print("Or use main.py for CLI mode")


if __name__ == "__main__":
    main()
