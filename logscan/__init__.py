"""logscan — CLI analisis log autentikasi SSH.

Kerangka coding test. Implementasikan TODO di `parser.py`, `summarize.py`,
`bruteforce.py`, dan `cli.py`.
"""

from __future__ import annotations

from .bruteforce import detect_bruteforce
from .cli import main, render_report, scan_file
from .models import Alert, Event
from .parser import iter_events, parse_line
from .summarize import summarize

__version__ = "0.1.0"

__all__ = [
    "Alert",
    "Event",
    "__version__",
    "detect_bruteforce",
    "iter_events",
    "main",
    "parse_line",
    "render_report",
    "scan_file",
    "summarize",
]
