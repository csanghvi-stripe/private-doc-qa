"""
LLM Engine - Local LFM2 inference for answer generation
Uses llama.cpp for efficient on-device inference.
"""
import subprocess
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    LFM2_TEXT_MODEL, RUNNERS_DIR,
    MAX_NEW_TOKENS, TEMPERATURE, CONTEXT_TEMPLATE
)

logger = logging.getLogger(__name__)


class LLMEngine:
    """
    Handles local LLM inference using LFM2 via llama.cpp.
    All processing happens on-device, nothing is sent to the cloud.
    """
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        runner_path: Optional[Path] = None
    ):
        self.model_path = model_path or LFM2_TEXT_MODEL
        self.runner_path = runner_path or RUNNERS_DIR
        
        # Find llama-cli or llama.cpp binary
        self.llama_bin = self._find_llama_binary()
        
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}\n"
                "Please download the LFM2 GGUF model from HuggingFace."
            )
        
        logger.info(f"LLM Engine initialized with {self.model_path.name}")
    
    def _find_llama_binary(self) -> Path:
        """Find the llama.cpp binary"""
        # Check common names
        possible_names = [
            "llama-cli",
            "llama-cpp",
            "main",
            "llama",
        ]
        
        # Check in runners directory
        for name in possible_names:
            bin_path = self.runner_path / name
            if bin_path.exists() and os.access(bin_path, os.X_OK):
                return bin_path
        
        # Check if installed globally
        for name in possible_names:
            result = subprocess.run(
                ["which", name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        
        raise FileNotFoundError(
            f"llama.cpp binary not found in {self.runner_path}\n"
            "Please download from HuggingFace or install llama.cpp."
        )
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = MAX_NEW_TOKENS,
        temperature: float = TEMPERATURE,
        stop_sequences: Optional[list] = None
    ) -> str:
        """
        Generate text using local LLM.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic)
            stop_sequences: List of sequences to stop generation
        
        Returns:
            Generated text response
        """
        # Build llama.cpp command
        cmd = [
            str(self.llama_bin),
            "-m", str(self.model_path),
            "-p", prompt,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "-c", "4096",  # Context size
            "--no-display-prompt",  # Don't echo the prompt
        ]
        
        # Add stop sequences if provided
        if stop_sequences:
            for seq in stop_sequences:
                cmd.extend(["--stop", seq])
        
        try:
            logger.debug(f"Running: {' '.join(cmd[:5])}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"LLM error: {result.stderr}")
                return f"Error generating response: {result.stderr[:200]}"
            
            response = result.stdout.strip()
            return response
            
        except subprocess.TimeoutExpired:
            logger.error("LLM generation timed out")
            return "Response generation timed out. Please try a simpler question."
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"Error: {str(e)}"
    
    def answer_with_context(
        self,
        question: str,
        context: str,
        template: Optional[str] = None
    ) -> str:
        """
        Generate an answer using RAG context.
        
        Args:
            question: User's question
            context: Retrieved context from documents
            template: Optional custom prompt template
        
        Returns:
            Generated answer
        """
        template = template or CONTEXT_TEMPLATE
        
        prompt = template.format(
            context=context,
            question=question
        )
        
        return self.generate(
            prompt,
            stop_sequences=["Question:", "Context:", "\n\n---"]
        )
    
    def is_available(self) -> bool:
        """Check if LLM is ready to use"""
        return self.llama_bin.exists() and self.model_path.exists()
    
    def get_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model': self.model_path.name,
            'model_size': f"{self.model_path.stat().st_size / 1e9:.1f} GB" if self.model_path.exists() else "N/A",
            'runner': self.llama_bin.name,
            'available': self.is_available()
        }


class MockLLMEngine:
    """
    Mock LLM for testing without actual model.
    Useful for UI development and testing.
    """
    
    def generate(self, prompt: str, **kwargs) -> str:
        return f"[Mock response to: {prompt[:50]}...]"
    
    def answer_with_context(self, question: str, context: str, **kwargs) -> str:
        # Extract some info from context for a semi-realistic mock
        if "income" in question.lower() or "w2" in question.lower():
            return (
                "Based on your W-2 documents:\n"
                "• Total wages: $185,000\n"
                "• Federal tax withheld: $42,500\n"
                "\nNote: This is mock data for testing."
            )
        return f"[Mock answer based on {len(context)} chars of context]"
    
    def is_available(self) -> bool:
        return True
    
    def get_info(self) -> Dict[str, Any]:
        return {'model': 'Mock LLM', 'available': True}


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        llm = LLMEngine()
        print(f"LLM Info: {llm.get_info()}")
        
        # Test simple generation
        response = llm.generate("What is 2 + 2?", max_tokens=50)
        print(f"Response: {response}")
    except FileNotFoundError as e:
        print(f"Setup needed: {e}")
        print("\nUsing mock LLM for testing...")
        llm = MockLLMEngine()
        print(f"Mock info: {llm.get_info()}")
