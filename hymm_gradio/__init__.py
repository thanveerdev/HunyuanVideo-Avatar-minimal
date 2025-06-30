"""
HunyuanVideo Avatar Gradio Interface Module
Provides web interface and API server functionality for HunyuanVideo Avatar
"""

# Make the module importable
__version__ = "1.0.0"
__author__ = "HunyuanVideo Avatar Team"

# Import key components for easier access
try:
    from .pipeline_utils import *
    from .web_demo import *
except ImportError:
    # Handle cases where dependencies might not be available
    pass 