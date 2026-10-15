"""Parsing baris syslog OpenSSH → `Event`.

Kerangka ini menyediakan docstring + contoh, isinya TODO untuk kamu.
Lihat TASK.md §2 untuk aturan lengkap.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .models import Event

__all__ = ["parse_line", "iter_events", "SYSLOG_TS_FORMAT"]

#: Timestamp syslog klasik: nama bulan pendek, hari, jam:menit:detik. Tanpa tahun!
SYSLOG_TS_FORMAT = "%b %d %H:%M:%S"


def parse_line(line: str, year: int = 2026) -> Event | None:
    """Parse satu baris log.

    Args:
        line: baris mentah (tanpa newline, boleh ada spasi ekstra di ujung).
        year: tahun yang dipakai karena syslog tidak menyimpan tahun.

    Returns:
        `Event` kalau baris valid secara syslog (walaupun bukan event SSH —
        baris dari `cron`, `sudo`, dsb. tetap jadi Event dengan
        ``kind="other"``), atau ``None`` kalau baris tidak bisa diparse.

    Catatan:
        Fungsi ini TIDAK BOLEH melempar exception untuk input apa pun.
        Contoh yang harus mengembalikan ``None``:
        ``"[garbage tanpa timestamp]"``, ``""``, ``"Jan xx 99:99:99 h sshd: x"``.

    Contoh:
        >>> e = parse_line("Jan 12 03:14:15 srv-01 sshd[1234]: Failed password for root from 203.0.113.7 port 51234 ssh2")
        >>> e.kind, e.user, e.ip, e.host
        ('failed_password', 'root', '203.0.113.7', 'srv-01')
        >>> e.ts.isoformat()
        '2026-01-12T03:14:15'
    """
    raise NotImplementedError("TODO: implementasikan parse_line()")


def iter_events(path: str | Path, year: int = 2026) -> Iterator[Event]:
    """Streaming generator: hasilkan `Event` dari file log.

    WAJIB streaming — jangan baca seluruh file ke memori, dan jangan
    mengembalikan ``list``. Baris yang tidak bisa diparse dilewati.

    Raises:
        FileNotFoundError: kalau file tidak ada (biarkan exception bawaan).

    Contoh:
        >>> for ev in iter_events("samples/auth_tiny.log"):
        ...     print(ev.kind)
    """
    raise NotImplementedError("TODO: implementasikan iter_events()")
