__all__ = ["translate_text", "translate_file", "sync_project", "write_fortls_config"]
__version__ = "0.1.1"

from .translator import translate_text, translate_file
from .sync import sync_project
from .editor import write_fortls_config
