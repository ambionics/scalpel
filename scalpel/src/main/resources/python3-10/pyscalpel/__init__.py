"""
This is a module providing tools to handle Burp HTTP traffic through the use of the Scalpel extension.

It provides many utilities to manipulate HTTP requests, responses and converting data.
"""

from pyscalpel.http import Request, Response, Flow
from pyscalpel.edit import editor
from pyscalpel.burp_utils import ctx as _context
from pyscalpel.java.scalpel_types import Context
from pyscalpel.logger import Logger, logger
from pyscalpel.events import MatchEvent
from . import http
from . import java
from . import encoding
from . import utils
from . import burp_utils
from . import venv
from . import edit

ctx: Context = _context
"""The Scalpel Python execution context

Contains the Burp Java API object, the venv directory, the user script path,
the path to the file loading the user script and a logging object
"""


__all__ = [
    "http",
    "java",
    "encoding",
    "utils",
    "burp_utils",
    "venv",
    "edit",
    "Request",
    "Response",
    "Flow",
    "ctx",
    "Context",
    "MatchEvent",
    "editor",
    "logger",
    "Logger",
]
