#!/usr/bin/env python3
"""
Private Doc Q&A - 100% On-Device Document Intelligence

Ask questions about your private documents using voice or text.
All processing happens locally - nothing is ever uploaded.

Usage:
    python main.py                    # Start interactive CLI
    python main.py --docs ~/taxes     # Use specific folder
    python main.py --index            # Auto-index on startup
    python main.py --mock             # Use mock LLM for testing

Examples:
    > What's my total W2 income for 2024?
    > When does my lease expire?
    > What medications am I allergic to?
"""

from ui.cli import main

if __name__ == "__main__":
    main()
