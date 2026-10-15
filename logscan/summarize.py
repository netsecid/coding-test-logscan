"""Agregasi statistik dari sekumpulan `Event`.

Lihat TASK.md §3.3 untuk bentuk dict yang diharapkan.
"""

from __future__ import annotations

from typing import Iterable

from .models import Event

__all__ = ["summarize"]

#: Panjang maksimum daftar peringkat yang dikembalikan `summarize`.
TOP_LIMIT = 10


def summarize(events: Iterable[Event]) -> dict:
    """Hitung ringkasan statistik dari `events`.

    Args:
        events: iterable (boleh generator — habiskan sekali saja).

    Returns:
        dict dengan key: ``total_events``, ``failed_logins``,
        ``successful_logins``, ``unique_source_ips``, ``unique_users``,
        ``hosts``, ``top_source_ips``, ``top_usernames``.

    Peringkat:
        - ``top_source_ips``: maks 10, urut ``failures`` DESC lalu ``ip`` ASC,
          semua IP yang muncul ikut (termasuk yang hanya berhasil login).
        - ``top_usernames``: maks 10, urut ``failures`` DESC lalu ``user`` ASC,
          hanya user dengan minimal 1 ``failed_password``.
    """
    raise NotImplementedError("TODO: implementasikan summarize()")
