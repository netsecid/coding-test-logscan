"""Fixture bersama untuk test spesifikasi."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"

#: File log kecil yang dipakai hampir semua test (16 baris).
TINY_LOG = SAMPLES / "auth_tiny.log"

#: File log "produksi" yang lebih besar & realistis, dipakai untuk demo.
SAMPLE_LOG = SAMPLES / "auth_sample.log"


@pytest.fixture
def tiny_path() -> Path:
    """Path ke samples/auth_tiny.log."""
    return TINY_LOG


@pytest.fixture
def tiny_events(tiny_path):
    """Semua `Event` dari samples/auth_tiny.log (list, urut file)."""
    from logscan import iter_events

    return list(iter_events(tiny_path))


@pytest.fixture
def write_log(tmp_path):
    """Helper: tulis file log sementara, kembalikan path-nya."""

    def _write(content: str, name: str = "auth.log") -> Path:
        path = tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    return _write


def syslog_line(body: str, ts: str = "Jan 12 03:00:00", host: str = "srv-01") -> str:
    """Bikin satu baris syslog lengkap dari `body`."""
    return f"{ts} {host} sshd[1000]: {body}"
