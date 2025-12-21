"""
Text/Markdown Parser - Handles plain text and markdown files
"""
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_text(file_path: Path) -> Dict[str, Any]:
    """
    Parse a text or markdown file.
    
    Returns:
        {
            'text': str,           # Full text content
            'lines': List[str],    # Lines of text
            'metadata': dict,      # Basic file metadata
            'source': str          # Original filename
        }
    """
    try:
        # Try UTF-8 first, fall back to other encodings
        text = None
        for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
            try:
                text = file_path.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if text is None:
            raise ValueError(f"Could not decode file with any supported encoding")
        
        lines = text.splitlines()
        
        # Extract any YAML frontmatter from markdown
        metadata = {}
        if file_path.suffix.lower() == '.md' and text.startswith('---'):
            metadata, text = _extract_frontmatter(text)
        
        return {
            'text': text,
            'lines': lines,
            'metadata': metadata,
            'source': file_path.name
        }
        
    except Exception as e:
        logger.error(f"Error parsing text file {file_path}: {e}")
        return {
            'text': '',
            'lines': [],
            'metadata': {},
            'source': file_path.name,
            'error': str(e)
        }


def _extract_frontmatter(text: str) -> tuple:
    """Extract YAML frontmatter from markdown files"""
    if not text.startswith('---'):
        return {}, text
    
    try:
        # Find the closing ---
        end_idx = text.find('---', 3)
        if end_idx == -1:
            return {}, text
        
        frontmatter = text[3:end_idx].strip()
        content = text[end_idx + 3:].strip()
        
        # Try to parse as YAML
        try:
            import yaml
            metadata = yaml.safe_load(frontmatter)
            if not isinstance(metadata, dict):
                metadata = {}
        except ImportError:
            # If no yaml module, just skip frontmatter parsing
            metadata = {'raw_frontmatter': frontmatter}
        
        return metadata, content
        
    except Exception:
        return {}, text
