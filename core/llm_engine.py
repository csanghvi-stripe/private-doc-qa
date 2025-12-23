"""LLM inference via llama.cpp"""
import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    LFM2_TEXT_MODEL, RUNNERS_DIR,
    MAX_NEW_TOKENS, TEMPERATURE, CONTEXT_TEMPLATE
)

logger = logging.getLogger(__name__)


class LLMEngine:
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        runner_path: Optional[Path] = None,
        max_new_tokens: int = MAX_NEW_TOKENS,
        temperature: float = TEMPERATURE
    ):
        self.model_path = model_path or LFM2_TEXT_MODEL
        self.runner_path = runner_path or RUNNERS_DIR
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        
        # Find llama binary
        self.llama_bin = self._find_llama_binary()
        
        logger.info(f"LLM Engine initialized with {self.model_path.name}")
    
    def _find_llama_binary(self) -> Path:
        """Locate llama-completion or llama-cli binary."""
        import shutil

        # Prefer llama-completion (non-interactive)
        system_completion = shutil.which("llama-completion")
        if system_completion:
            logger.info(f"Found system llama-completion: {system_completion}")
            return Path(system_completion)

        # Check homebrew locations
        homebrew_paths = [
            Path("/opt/homebrew/bin/llama-completion"),
            Path("/usr/local/bin/llama-completion"),
        ]
        for p in homebrew_paths:
            if p.exists():
                logger.info(f"Found homebrew llama-completion: {p}")
                return p

        # Fall back to llama-cli
        system_llama = shutil.which("llama-cli")
        if system_llama:
            logger.info(f"Found system llama-cli: {system_llama}")
            return Path(system_llama)

        # Check local runners directory
        standard_names = ["llama-completion", "llama-cli", "llama-cpp", "main", "llama"]
        for name in standard_names:
            bin_path = self.runner_path / name
            if bin_path.exists() and os.access(bin_path, os.X_OK):
                logger.info(f"Found llama binary in runners: {bin_path}")
                return bin_path

        raise FileNotFoundError(
            "llama-completion or llama-cli not found for text generation.\n"
            "Install with: brew install llama.cpp"
        )
    
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        max_tokens = max_tokens or self.max_new_tokens
        temperature = temperature or self.temperature

        # Write prompt to temp file to avoid shell escaping issues
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        try:
            cmd = [
                str(self.llama_bin),
                "-m", str(self.model_path),
                "-f", prompt_file,
                "-n", str(max_tokens),
                "--temp", str(temperature),
                "-c", "4096",
                "-no-cnv",
                "--no-display-prompt",
                "--simple-io",
                "-ngl", "0",
            ]

            logger.info("Running LLM...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=120,
                stdin=subprocess.DEVNULL,
                env={**os.environ, "TOKENIZERS_PARALLELISM": "false"}
            )

            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')

            if result.returncode != 0:
                logger.error(f"LLM error: {stderr}")
                raise RuntimeError(f"LLM failed: {stderr[:500]}")

            output = stdout.strip()

            # Strip EOS tokens
            for eos in ["[end of text]", "<|endoftext|>", "<|im_end|>"]:
                if output.endswith(eos):
                    output = output[:-len(eos)].strip()

            logger.info(f"LLM output length: {len(output)} chars")
            return output
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("LLM generation timed out (120s)")
        finally:
            # Clean up temp file
            try:
                os.unlink(prompt_file)
            except:
                pass
    
    def answer_with_context(self, question: str, context: str) -> str:
        prompt = CONTEXT_TEMPLATE.format(context=context, question=question)
        return self.generate(prompt)

    def is_available(self) -> bool:
        return (
            self.llama_bin is not None and
            self.llama_bin.exists() and
            self.model_path.exists()
        )
    
    def get_info(self) -> dict:
        return {
            'model': self.model_path.name if self.model_path else None,
            'runner': str(self.llama_bin) if self.llama_bin else None,
            'available': self.is_available(),
            'max_tokens': self.max_new_tokens,
            'temperature': self.temperature
        }


class MockLLMEngine:
    """For testing without downloading models."""

    def __init__(self, *args, **kwargs):
        logger.info("Using mock LLM")
    
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        return f"[Mock response] This is a test response. In production, this would be generated by LFM2-1.2B based on your documents."
    
    def answer_with_context(self, question: str, context: str) -> str:
        return f"[Mock answer to: {question}]\n\nThis is a mock response. Install llama.cpp and download LFM2-1.2B for real answers.\n\nContext preview: {context[:200]}..."
    
    def is_available(self) -> bool:
        return True
    
    def get_info(self) -> dict:
        return {
            'model': 'mock',
            'runner': 'mock',
            'available': True,
            'max_tokens': 512,
            'temperature': 0.3
        }


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        engine = LLMEngine()
        print(f"Engine info: {engine.get_info()}")
        
        if engine.is_available():
            response = engine.generate("What is 2+2? Answer briefly:")
            print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
        print("Using mock engine...")
        engine = MockLLMEngine()
        print(engine.generate("test"))