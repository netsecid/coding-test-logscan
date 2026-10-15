"""Struktur data inti `logscan`.

File ini SUDAH LENGKAP — tidak perlu diubah. Test mengandalkan nama field ini.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

#: Nilai `kind` yang dikenali.
KIND_FAILED_PASSWORD = "failed_password"
KIND_ACCEPTED_PASSWORD = "accepted_password"
KIND_INVALID_USER = "invalid_user"
KIND_CONNECTION_CLOSED = "connection_closed"
KIND_OTHER = "other"

ALL_KINDS = frozenset(
    {
        KIND_FAILED_PASSWORD,
        KIND_ACCEPTED_PASSWORD,
        KIND_INVALID_USER,
        KIND_CONNECTION_CLOSED,
        KIND_OTHER,
    }
)


@dataclass(frozen=True)
class Event:
    """Satu baris log SSH yang berhasil diparse."""

    ts: datetime  # naive, tahun sudah diisi dari parameter `year`
    host: str
    user: str | None
    ip: str
    kind: str  # salah satu konstanta KIND_* di atas
    raw: str  # baris asli tanpa newline


@dataclass(frozen=True)
class Alert:
    """Satu rangkaian percobaan login gagal yang mencurigakan dari satu IP."""

    ip: str
    start: datetime
    end: datetime
    failed_count: int
    users: tuple[str, ...]  # username unik, terurut A→Z
    severity: str  # "high" | "medium"
