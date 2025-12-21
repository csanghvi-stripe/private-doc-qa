"""
CLI Interface for Private Doc Q&A
Interactive terminal-based interface for document Q&A.
"""
import sys
import logging
from pathlib import Path
from typing import Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DEFAULT_DOCS_DIR
from core.document_store import DocumentStore
from core.rag_engine import RAGEngine
from core.llm_engine import LLMEngine, MockLLMEngine
from core.audio_engine import AudioEngine, MockAudioEngine

logger = logging.getLogger(__name__)


class CLI:
    """Interactive CLI for Private Doc Q&A"""
    
    def __init__(self, docs_path: Optional[Path] = None, use_mock: bool = False):
        self.docs_path = Path(docs_path) if docs_path else DEFAULT_DOCS_DIR
        self.docs_path.mkdir(parents=True, exist_ok=True)
        
        print("\n🔒 Private Doc Q&A")
        print("=" * 50)
        print("100% on-device • Never uploaded • Works offline")
        print("=" * 50)
        
        # Initialize components
        print("\n⏳ Loading components...")
        
        self.store = DocumentStore()
        self.rag = RAGEngine(self.store)
        
        # Try real LLM, fall back to mock
        if use_mock:
            self.llm = MockLLMEngine()
            self.audio = MockAudioEngine()
            print("ℹ️  Using mock engines (for testing)")
        else:
            try:
                self.llm = LLMEngine()
                print(f"✅ LLM loaded: {self.llm.get_info()['model']}")
            except FileNotFoundError:
                print("⚠️  LLM model not found, using mock")
                self.llm = MockLLMEngine()
            
            try:
                self.audio = AudioEngine()
                if self.audio.is_available():
                    print(f"✅ Audio loaded: {self.audio.get_info()['model']}")
                else:
                    print("⚠️  Audio model not found, using mock")
                    self.audio = MockAudioEngine()
            except Exception:
                self.audio = MockAudioEngine()
        
        print()
    
    def index_documents(self):
        """Index all documents in the docs folder"""
        print(f"\n📂 Scanning: {self.docs_path}")
        
        if not self.docs_path.exists():
            print(f"❌ Folder not found: {self.docs_path}")
            return
        
        files = list(self.docs_path.iterdir())
        if not files:
            print("📭 No documents found. Add PDFs, DOCX, or TXT files to get started.")
            return
        
        results = self.store.add_folder(self.docs_path)
        
        print("\n📊 Indexing Results:")
        for filename, num_chunks in results.items():
            if num_chunks > 0:
                print(f"  ✅ {filename}: {num_chunks} chunks")
            elif num_chunks == 0:
                print(f"  ⏭️  {filename}: already indexed")
            else:
                print(f"  ❌ {filename}: failed")
        
        stats = self.store.get_stats()
        print(f"\n📈 Total: {stats['num_documents']} documents, {stats['num_chunks']} chunks")
    
    def show_documents(self):
        """Show indexed documents"""
        stats = self.store.get_stats()
        
        if stats['num_documents'] == 0:
            print("\n📭 No documents indexed yet.")
            print(f"   Add documents to: {self.docs_path}")
            return
        
        print("\n📁 Indexed Documents:")
        for doc in stats['documents']:
            print(f"  📄 {doc}")
        print(f"\n   Total: {stats['num_chunks']} searchable chunks")
    
    def ask(self, question: str) -> str:
        """Ask a question about the documents"""
        if not question.strip():
            return ""
        
        # Retrieve relevant context
        result = self.rag.retrieve(question)
        
        if result.num_chunks == 0:
            return "❌ I couldn't find any relevant information in your documents."
        
        # Generate answer
        answer = self.llm.answer_with_context(question, result.context)
        
        # Format response
        response = []
        response.append(f"\n🤖 {answer}")
        response.append(f"\n📎 Sources ({result.confidence:.0%} confidence):")
        response.append(self.rag.format_sources_for_display(result.sources))
        
        return "\n".join(response)
    
    def voice_input(self) -> Optional[str]:
        """Record and transcribe voice input"""
        if not self.audio.is_available():
            print("🎤 Voice input not available (model not loaded)")
            return None
        
        print("\n🎤 Listening... (speak your question)")
        
        try:
            text = self.audio.record_and_transcribe()
            if text:
                print(f"📝 Heard: \"{text}\"")
                return text
            else:
                print("🔇 No speech detected")
                return None
        except Exception as e:
            print(f"❌ Audio error: {e}")
            return None
    
    def run(self):
        """Run interactive CLI loop"""
        print("\n💡 Commands:")
        print("  /index  - Index documents from folder")
        print("  /docs   - Show indexed documents")
        print("  /voice  - Use voice input")
        print("  /clear  - Clear the index")
        print("  /help   - Show this help")
        print("  /quit   - Exit")
        print("\nOr just type your question!\n")
        
        while True:
            try:
                # Get input
                user_input = input("💬 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    cmd = user_input.lower()
                    
                    if cmd in ["/quit", "/exit", "/q"]:
                        print("\n👋 Goodbye!")
                        break
                    
                    elif cmd == "/index":
                        self.index_documents()
                    
                    elif cmd == "/docs":
                        self.show_documents()
                    
                    elif cmd == "/voice":
                        question = self.voice_input()
                        if question:
                            response = self.ask(question)
                            print(response)
                    
                    elif cmd == "/clear":
                        confirm = input("⚠️  Clear entire index? (y/n): ")
                        if confirm.lower() == 'y':
                            self.store.clear()
                            print("🗑️  Index cleared")
                    
                    elif cmd in ["/help", "/?"]:
                        print("\n💡 Commands:")
                        print("  /index  - Index documents from folder")
                        print("  /docs   - Show indexed documents")
                        print("  /voice  - Use voice input")
                        print("  /clear  - Clear the index")
                        print("  /quit   - Exit")
                    
                    else:
                        print(f"❓ Unknown command: {cmd}")
                
                else:
                    # It's a question
                    response = self.ask(user_input)
                    print(response)
                
                print()  # Blank line for readability
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                break


def main():
    """Main entry point for CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Private Doc Q&A - 100% on-device document intelligence"
    )
    parser.add_argument(
        "--docs", "-d",
        type=str,
        help="Path to documents folder"
    )
    parser.add_argument(
        "--index", "-i",
        action="store_true",
        help="Index documents immediately"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock LLM for testing"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create CLI
    cli = CLI(docs_path=args.docs, use_mock=args.mock)
    
    # Auto-index if requested
    if args.index:
        cli.index_documents()
    
    # Run interactive loop
    cli.run()


if __name__ == "__main__":
    main()
