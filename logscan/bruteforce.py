"""Deteksi pola brute force berbasis jendela waktu.

Lihat TASK.md §3.4 — algoritma ditulis eksak di sana. Ikuti apa adanya.
"""

from __future__ import annotations

from typing import Iterable

from .models import Alert, Event

__all__ = ["detect_bruteforce"]

DEFAULT_THRESHOLD = 5
DEFAULT_WINDOW_SECONDS = 60

#: Username yang otomatis menaikkan severity ke "high".
PRIVILEGED_USERS = frozenset({"root", "admin"})


def detect_bruteforce(
    events: Iterable[Event],
    threshold: int = DEFAULT_THRESHOLD,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
) -> list[Alert]:
    """Cari rangkaian login gagal yang mencurigakan.

    Hanya ``kind == "failed_password"`` yang dihitung.

    Args:
        events: iterable `Event` (urutan baris tidak dijamin urut waktu).
        threshold: jumlah kegagalan minimum dalam satu jendela.
        window_seconds: lebar jendela waktu (detik).

    Returns:
        list `Alert` urut ``start`` ASC lalu ``ip`` ASC. Alert per IP tidak
        tumpang tindih.

    Contoh (threshold=4, window=60):
        >>> alerts = detect_bruteforce(iter_events("samples/auth_tiny.log"), threshold=4)
        >>> alerts[0].ip, alerts[0].failed_count, alerts[0].users
        ('203.0.113.7', 4, ('root',))
    """
    raise NotImplementedError("TODO: implementasikan detect_bruteforce()")
