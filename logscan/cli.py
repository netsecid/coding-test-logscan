"""CLI `python -m logscan` — kerangka.

Bagian argparse + penanganan error sudah disediakan (plumbing, bukan penilaian).
Yang perlu kamu isi: `scan_file()` dan `render_report()`.
"""

from __future__ import annotations

import argparse
import json
import sys

from .bruteforce import (
    DEFAULT_THRESHOLD,
    DEFAULT_WINDOW_SECONDS,
    detect_bruteforce,
)
from .parser import iter_events
from .summarize import summarize

__all__ = ["scan_file", "render_report", "main", "build_parser"]

DEFAULT_TOP = 10
DEFAULT_YEAR = 2026

#: Judul seksi yang HARUS muncul di output non-JSON (persis seperti ini).
SECTION_TITLES = ("RINGKASAN", "TOP SOURCE IP", "TOP USERNAME", "ALERT BRUTE FORCE")

#: Teks pengganti kalau tidak ada alert brute force.
NO_ALERT_TEXT = "Tidak ada indikasi brute force."


def build_parser() -> argparse.ArgumentParser:
    """Bangun parser argparse untuk CLI."""
    parser = argparse.ArgumentParser(
        prog="logscan",
        description="Analisis log autentikasi SSH: ringkasan, top IP/user, dan deteksi brute force.",
    )
    parser.add_argument("logfile", help="path file auth.log")
    parser.add_argument("--json", action="store_true", help="cetak hasil sebagai JSON")
    parser.add_argument("--top", type=int, default=DEFAULT_TOP, metavar="N",
                        help=f"jumlah entri peringkat yang ditampilkan (default {DEFAULT_TOP})")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD, metavar="N",
                        help=f"jumlah kegagalan minimum per jendela (default {DEFAULT_THRESHOLD})")
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW_SECONDS, metavar="S",
                        help=f"lebar jendela waktu dalam detik (default {DEFAULT_WINDOW_SECONDS})")
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR, metavar="YYYY",
                        help=f"tahun untuk timestamp syslog (default {DEFAULT_YEAR})")
    return parser


def scan_file(
    path: str,
    *,
    threshold: int = DEFAULT_THRESHOLD,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
    top: int = DEFAULT_TOP,
    year: int = DEFAULT_YEAR,
) -> dict:
    """Scan satu file log dan kembalikan dict hasil (lihat TASK.md §3.5).

    Tips: file boleh dibaca lebih dari sekali (dua pass streaming lebih hemat
    memori daripada menampung semua `Event` di list).
    """
    raise NotImplementedError("TODO: implementasikan scan_file()")


def render_report(result: dict) -> str:
    """Ubah dict hasil `scan_file()` menjadi laporan teks untuk manusia.

    Wajib memuat keempat judul di `SECTION_TITLES` dan, bila tidak ada alert,
    memuat `NO_ALERT_TEXT`.
    """
    raise NotImplementedError("TODO: implementasikan render_report()")


def main(argv: list[str] | None = None) -> int:
    """Entry point CLI. Sudah lengkap — tidak perlu diubah."""
    args = build_parser().parse_args(argv)
    try:
        result = scan_file(
            args.logfile,
            threshold=args.threshold,
            window_seconds=args.window,
            top=args.top,
            year=args.year,
        )
    except OSError:
        print(
            f"Error: file tidak ditemukan atau tidak bisa dibaca: {args.logfile}",
            file=sys.stderr,
        )
        return 2

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render_report(result))
    return 0
