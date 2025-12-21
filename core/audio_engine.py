"""
Audio Engine - Voice input using LFM2-Audio
Transcribes speech to text locally using LFM2-Audio model.
"""
import subprocess
import tempfile
import logging
import wave
import struct
from pathlib import Path
from typing import Optional, Callable
import threading
import queue

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    LFM2_AUDIO_MODEL, LFM2_AUDIO_ENCODER, LFM2_AUDIO_DECODER,
     AUDIO_SAMPLE_RATE, AUDIO_CHUNK_DURATION
)

logger = logging.getLogger(__name__)


class AudioEngine:
    def __init__(
        self,
        model_path: Optional[Path] = None,
        encoder_path: Optional[Path] = None,
        decoder_path: Optional[Path] = None,
        runner_path: Optional[Path] = None
    ):
        self.model_path = model_path or LFM2_AUDIO_MODEL
        self.encoder_path = encoder_path or LFM2_AUDIO_ENCODER
        self.decoder_path = decoder_path or LFM2_AUDIO_DECODER
        self.runner_path = runner_path or AUDIO_RUNNERS_DIR  # Use audio-specific path
        # Find llama binary
        self.llama_bin = self._find_llama_binary()
        
        # Audio recording state
        self._recording = False
        self._audio_queue = queue.Queue()
        
        logger.info("Audio Engine initialized")
    
    
    def _find_llama_binary(self) -> Optional[Path]:
        """Find the llama.cpp binary for AUDIO transcription"""
        
        # For audio, we need the special LFM2-Audio runner
        audio_binary_names = [
            "llama-lfm2-audio",  # Primary audio binary
            "llama-mtmd-cli",    # Alternative multimodal binary
        ]
        
        # 1. Check in runners directory
        for name in audio_binary_names:
            bin_path = self.runner_path / name
            if bin_path.exists() and os.access(bin_path, os.X_OK):
                logger.info(f"Found audio binary: {bin_path}")
                return bin_path
        
        # 2. Check in subdirectories of runners (like lfm2-audio-macos-arm64/)
        if self.runner_path.exists():
            for subdir in self.runner_path.iterdir():
                if subdir.is_dir():
                    for name in audio_binary_names:
                        bin_path = subdir / name
                        if bin_path.exists() and os.access(bin_path, os.X_OK):
                            logger.info(f"Found audio binary in subdir: {bin_path}")
                            return bin_path
        
        # 3. Check if installed globally
        import shutil
        for name in audio_binary_names:
            system_path = shutil.which(name)
            if system_path:
                logger.info(f"Found system audio binary: {system_path}")
                return Path(system_path)
        
        logger.warning("Audio binary not found - voice input will be disabled")
        return None


    def transcribe_file(self, audio_path: Path) -> str:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to WAV file (16kHz, 16-bit)
        
        Returns:
            Transcribed text
        """
        if not self.is_available():
            raise RuntimeError("Audio model not available. Please download LFM2-Audio.")
        
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Build command for LFM2-Audio transcription
        cmd = [
            str(self.llama_bin),
            "-m", str(self.model_path),
            "--mmproj", str(self.encoder_path),
            "-f", str(audio_path),
            "--temp", "0.0",
            "-n", "256",
            "--no-display-prompt",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Transcription error: {result.stderr}")
                return ""
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            logger.error("Transcription timed out")
            return ""
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def record_and_transcribe(
        self,
        duration: float = AUDIO_CHUNK_DURATION,
        device: Optional[str] = None
    ) -> str:
        """
        Record audio from microphone and transcribe.
        
        Args:
            duration: Recording duration in seconds
            device: Audio input device (None for default)
        
        Returns:
            Transcribed text
        """
        try:
            import sounddevice as sd
            import numpy as np
        except ImportError:
            raise ImportError("Please install sounddevice: pip install sounddevice")
        
        logger.info(f"Recording {duration}s of audio...")
        
        # Record audio
        audio = sd.rec(
            int(duration * AUDIO_SAMPLE_RATE),
            samplerate=AUDIO_SAMPLE_RATE,
            channels=1,
            dtype='int16',
            device=device
        )
        sd.wait()
        
        # Check audio level
        max_level = np.max(np.abs(audio))
        if max_level < 100:  # Threshold for silence
            logger.info("Audio too quiet, skipping transcription")
            return ""
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = Path(f.name)
            self._save_wav(temp_path, audio)
        
        try:
            # Transcribe
            text = self.transcribe_file(temp_path)
            return text
        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
    
    def start_continuous_recording(
        self,
        callback: Callable[[str], None],
        chunk_duration: float = AUDIO_CHUNK_DURATION,
        device: Optional[str] = None
    ):
        """
        Start continuous recording with callbacks for each transcription.
        
        Args:
            callback: Function called with each transcription
            chunk_duration: Duration of each chunk in seconds
            device: Audio input device
        """
        self._recording = True
        
        def record_loop():
            while self._recording:
                text = self.record_and_transcribe(chunk_duration, device)
                if text:
                    callback(text)
        
        self._record_thread = threading.Thread(target=record_loop, daemon=True)
        self._record_thread.start()
        logger.info("Continuous recording started")
    
    def stop_recording(self):
        """Stop continuous recording"""
        self._recording = False
        if hasattr(self, '_record_thread'):
            self._record_thread.join(timeout=2)
        logger.info("Recording stopped")
    
    def _save_wav(self, path: Path, audio):
        """Save numpy audio array to WAV file"""
        import numpy as np
        
        with wave.open(str(path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(AUDIO_SAMPLE_RATE)
            wf.writeframes(audio.tobytes())
    
        def is_available(self) -> bool:
            """Check if audio model is ready"""
            return (
                self.llama_bin is not None and
                self.llama_bin.exists() and
                self.model_path.exists() and
                self.encoder_path.exists()
            )
    
    def list_devices(self) -> list:
        """List available audio input devices"""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            input_devices = []
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': dev['name'],
                        'channels': dev['max_input_channels'],
                        'sample_rate': dev['default_samplerate']
                    })
            return input_devices
        except ImportError:
            return []
    
    def get_info(self) -> dict:
        """Get audio engine info"""
        return {
            'model': self.model_path.name if self.model_path else None,
            'available': self.is_available(),
            'sample_rate': AUDIO_SAMPLE_RATE,
            'chunk_duration': AUDIO_CHUNK_DURATION
        }


class MockAudioEngine:
    """Mock audio engine for testing without microphone"""
    
    def transcribe_file(self, audio_path: Path) -> str:
        return "[Mock transcription of audio file]"
    
    def record_and_transcribe(self, duration: float = 4, device=None) -> str:
        return "What is my total income for 2024?"
    
    def is_available(self) -> bool:
        return True
    
    def list_devices(self) -> list:
        return [{'index': 0, 'name': 'Mock Microphone', 'channels': 1}]
    
    def get_info(self) -> dict:
        return {'model': 'Mock Audio', 'available': True}


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    engine = AudioEngine()
    print(f"Audio Engine Info: {engine.get_info()}")
    
    if engine.is_available():
        devices = engine.list_devices()
        print(f"Available devices: {devices}")
    else:
        print("Audio model not available. Using mock...")
        engine = MockAudioEngine()
        print(f"Mock devices: {engine.list_devices()}")
