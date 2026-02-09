__all__ = ["translate_text", "translate_file", "sync_project"]
__version__ = "3.1.0"

from .translator import translate_text, translate_file
from .sync import sync_project
