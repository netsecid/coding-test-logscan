"""Root conftest — memastikan root repo masuk `sys.path` saat pytest dijalankan.

Sengaja kosong isinya; cukup keberadaan file ini di root project.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
