__all__ = [
    "TranslationResult",
    "translate_text",
    "translate_with_map",
    "translate_file",
    "sync_project",
    "write_fortls_config",
]
__version__ = "0.2.1"

from .translator import (
    TranslationResult,
    translate_file,
    translate_text,
    translate_with_map,
)
from .sync import sync_project
from .editor import write_fortls_config
