"""Test spesifikasi untuk `logscan.parser` (TASK.md §1–§3.2)."""

from __future__ import annotations

import inspect
from datetime import datetime

import pytest

from logscan import iter_events, parse_line
from logscan.models import Event


# --------------------------------------------------------------------------- #
# parse_line: jalur bahagia
# --------------------------------------------------------------------------- #
def test_failed_password_root():
    line = ("Jan 12 03:14:15 srv-01 sshd[1234]: "
            "Failed password for root from 203.0.113.7 port 51234 ssh2")
    event = parse_line(line)

    assert isinstance(event, Event)
    assert event.ts == datetime(2026, 1, 12, 3, 14, 15)
    assert event.host == "srv-01"
    assert event.user == "root"
    assert event.ip == "203.0.113.7"
    assert event.kind == "failed_password"
    assert event.raw == line


def test_failed_password_invalid_user_is_failed_password():
    event = parse_line("Jan 12 03:14:20 srv-01 sshd[1235]: "
                       "Failed password for invalid user admin from 203.0.113.7 port 51240 ssh2")

    assert event is not None
    assert event.kind == "failed_password"
    assert event.user == "admin"
    assert event.ip == "203.0.113.7"


def test_invalid_user_line():
    event = parse_line("Jan 12 03:16:00 srv-01 sshd[1240]: "
                       "Invalid user oracle from 203.0.113.7 port 51250 ssh2")

    assert event is not None
    assert event.kind == "invalid_user"
    assert event.user == "oracle"
    assert event.ip == "203.0.113.7"


def test_accepted_password_line():
    event = parse_line("Jan 12 03:17:02 srv-01 sshd[1241]: "
                       "Accepted password for alice from 198.51.100.22 port 40222 ssh2")

    assert event is not None
    assert event.kind == "accepted_password"
    assert event.user == "alice"


def test_accepted_publickey_also_counts_as_accepted_password():
    event = parse_line("Jan 12 03:21:00 srv-01 sshd[1244]: "
                       "Accepted publickey for bob from 2001:db8::1 port 51420 ssh2")

    assert event is not None
    assert event.kind == "accepted_password"
    assert event.ip == "2001:db8::1"


def test_connection_closed_with_user():
    event = parse_line("Jan 12 03:18:11 srv-01 sshd[1242]: "
                       "Connection closed by authenticating user root 203.0.113.7 port 51300 [preauth]")

    assert event is not None
    assert event.kind == "connection_closed"
    assert event.user == "root"
    assert event.ip == "203.0.113.7"


def test_connection_closed_without_user_has_none_user():
    event = parse_line("Jan 12 03:18:11 srv-01 sshd[1242]: "
                       "Connection closed by 198.51.100.9 port 51300 [preauth]")

    assert event is not None
    assert event.kind == "connection_closed"
    assert event.user is None
    assert event.ip == "198.51.100.9"


def test_ipv6_address_is_kept_as_is():
    event = parse_line("Jan 12 03:19:07 srv-01 sshd[1243]: "
                       "Failed password for bob from 2001:db8::1 port 51411 ssh2")

    assert event is not None
    assert event.ip == "2001:db8::1"


def test_single_digit_day_with_two_spaces():
    event = parse_line("Jan  2 09:00:00 srv-01 sshd[1250]: "
                       "Failed password for carol from 192.0.2.55 port 1000 ssh2")

    assert event is not None
    assert event.ts == datetime(2026, 1, 2, 9, 0, 0)


def test_year_is_configurable():
    event = parse_line("Jan 12 03:14:15 srv-01 sshd[1234]: "
                       "Failed password for root from 203.0.113.7 port 1 ssh2", year=2024)

    assert event is not None
    assert event.ts.year == 2024


def test_line_with_trailing_newline_and_spaces():
    base = ("Jan 12 03:14:15 srv-01 sshd[1234]: "
            "Failed password for root from 203.0.113.7 port 1 ssh2")
    assert parse_line(base + "\n") is not None
    assert parse_line(base + "   \n") is not None


# --------------------------------------------------------------------------- #
# parse_line: baris non-SSH dan baris rusak
# --------------------------------------------------------------------------- #
def test_non_ssh_line_becomes_kind_other_without_ip():
    event = parse_line("Jan 12 03:20:00 srv-01 cron[9999]: (root) CMD (/usr/bin/backup.sh)")

    assert event is not None
    assert event.kind == "other"
    assert event.user is None
    assert event.ip == ""


@pytest.mark.parametrize(
    "line",
    [
        "",
        "   ",
        "baris ini sengaja rusak karena tidak punya timestamp syslog",
        "Jan xx 99:99:99 srv-01 sshd[1]: Failed password for root from 1.2.3.4 port 1 ssh2",
        "[garbage]",
    ],
)
def test_malformed_lines_return_none_without_raising(line):
    assert parse_line(line) is None


# --------------------------------------------------------------------------- #
# iter_events
# --------------------------------------------------------------------------- #
def test_iter_events_returns_an_iterator(tiny_path):
    stream = iter_events(tiny_path)

    assert inspect.isgenerator(stream) or not isinstance(stream, (list, tuple))


def test_iter_events_skips_malformed_and_blank_lines(tiny_path):
    events = list(iter_events(tiny_path))

    assert len(events) == 14  # 16 baris fisik - 1 baris rusak - 1 baris kosong
    kinds = [e.kind for e in events]
    assert kinds.count("failed_password") == 8
    assert kinds.count("accepted_password") == 2
    assert kinds.count("invalid_user") == 1
    assert kinds.count("connection_closed") == 1
    assert kinds.count("other") == 2


def test_iter_events_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        list(iter_events(tmp_path / "tidak-ada.log"))


def test_iter_events_on_empty_file(write_log):
    path = write_log("")

    assert list(iter_events(path)) == []
