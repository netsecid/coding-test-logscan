"""Test spesifikasi untuk `logscan.bruteforce` (TASK.md §3.4).

Semua timestamp di file uji ini dipilih supaya batas jendela waktu teruji persis.
"""

from __future__ import annotations

from datetime import datetime

from logscan import detect_bruteforce, iter_events
from tests.conftest import syslog_line


def _failed_log(lines_ts_and_ip, user: str = "zed", host: str = "srv-01") -> str:
    """Bangun isi file log dari daftar (timestamp, ip)."""
    rows = []
    for ts, ip in lines_ts_and_ip:
        rows.append(syslog_line(f"Failed password for {user} from {ip} port 1 ssh2",
                                ts=ts, host=host))
    return "\n".join(rows) + "\n"


# --------------------------------------------------------------------------- #
# Skenario pada samples/auth_tiny.log
# --------------------------------------------------------------------------- #
def test_defaults_find_bruteforce_from_one_ip(tiny_events):
    alerts = detect_bruteforce(tiny_events)

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.ip == "203.0.113.7"
    assert alert.start == datetime(2026, 1, 12, 3, 14, 15)
    assert alert.end == datetime(2026, 1, 12, 3, 14, 35)
    assert alert.failed_count == 5
    assert alert.users == ("admin", "root")
    assert alert.severity == "high"  # "root" termasuk user istimewa


def test_higher_threshold_yields_no_alert(tiny_events):
    assert detect_bruteforce(tiny_events, threshold=6) == []


def test_wider_window_swallows_the_slow_attempt(tiny_events):
    alerts = detect_bruteforce(tiny_events, threshold=5, window_seconds=90)

    assert len(alerts) == 1
    assert alerts[0].failed_count == 6
    assert alerts[0].end == datetime(2026, 1, 12, 3, 15, 40)
    assert alerts[0].users == ("admin", "nobody", "root")


def test_input_order_does_not_matter(tiny_path, tmp_path, tiny_events):
    shuffled = tmp_path / "shuffled.log"
    lines = tiny_path.read_text(encoding="utf-8").splitlines()
    shuffled.write_text("\n".join(reversed(lines)) + "\n", encoding="utf-8")

    assert detect_bruteforce(iter_events(shuffled)) == detect_bruteforce(tiny_events)


# --------------------------------------------------------------------------- #
# Aturan algoritma: hanya failed_password, window inklusif, tidak tumpang tindih
# --------------------------------------------------------------------------- #
def test_only_failed_password_lines_are_counted(write_log):
    """5 baris `Invalid user` + `Connection closed` dalam 60 detik bukan brute force."""
    rows = [
        syslog_line("Invalid user deploy from 203.0.113.9 port 1", ts="Jan 12 05:00:00"),
        syslog_line("Invalid user deploy from 203.0.113.9 port 2", ts="Jan 12 05:00:10"),
        syslog_line("Invalid user deploy from 203.0.113.9 port 3", ts="Jan 12 05:00:20"),
        syslog_line("Invalid user deploy from 203.0.113.9 port 4", ts="Jan 12 05:00:30"),
        syslog_line("Connection closed by 203.0.113.9 port 5 [preauth]", ts="Jan 12 05:00:40"),
    ]
    path = write_log("\n".join(rows) + "\n")

    assert detect_bruteforce(iter_events(path), threshold=5, window_seconds=60) == []


def test_window_boundary_is_inclusive(write_log):
    """Jarak tepat 60 detik masih masuk jendela 60 detik."""
    rows = [
        ("Jan 12 06:00:00", "198.51.100.1"),
        ("Jan 12 06:00:10", "198.51.100.1"),
        ("Jan 12 06:00:20", "198.51.100.1"),
        ("Jan 12 06:00:30", "198.51.100.1"),
        ("Jan 12 06:01:00", "198.51.100.1"),  # +60s dari baris pertama
    ]
    path = write_log(_failed_log(rows))

    alerts = detect_bruteforce(iter_events(path), threshold=5, window_seconds=60)

    assert len(alerts) == 1
    assert alerts[0].failed_count == 5
    assert alerts[0].end == datetime(2026, 1, 12, 6, 1, 0)


def test_alerts_never_overlap(write_log):
    """10 kegagalan berjarak 5 detik, threshold 3 / window 20 -> 2 alert terpisah."""
    rows = [(f"Jan 12 07:00:{sec:02d}", "203.0.113.50") for sec in range(0, 50, 5)]
    path = write_log(_failed_log(rows))

    alerts = detect_bruteforce(iter_events(path), threshold=3, window_seconds=20)

    assert len(alerts) == 2
    assert alerts[0].start == datetime(2026, 1, 12, 7, 0, 0)
    assert alerts[0].end == datetime(2026, 1, 12, 7, 0, 20)
    assert alerts[0].failed_count == 5
    assert alerts[1].start == datetime(2026, 1, 12, 7, 0, 25)
    assert alerts[1].end == datetime(2026, 1, 12, 7, 0, 45)
    assert alerts[0].end < alerts[1].start


def test_different_ips_are_tracked_separately(write_log):
    rows = [(f"Jan 12 08:00:{sec:02d}", "10.0.0.1") for sec in range(0, 25, 5)]
    rows += [(f"Jan 12 08:00:{sec:02d}", "10.0.0.2") for sec in range(0, 25, 5)]
    path = write_log(_failed_log(rows, user="zed"))

    alerts = detect_bruteforce(iter_events(path), threshold=5, window_seconds=60)

    assert [a.ip for a in alerts] == ["10.0.0.1", "10.0.0.2"]
    assert all(a.failed_count == 5 for a in alerts)


# --------------------------------------------------------------------------- #
# Severity
# --------------------------------------------------------------------------- #
def test_severity_medium_for_normal_user(write_log):
    rows = [(f"Jan 12 09:00:{sec:02d}", "192.0.2.10") for sec in range(0, 15, 3)]
    path = write_log(_failed_log(rows, user="zed"))

    alerts = detect_bruteforce(iter_events(path), threshold=5, window_seconds=60)

    assert alerts[0].severity == "medium"


def test_severity_high_when_count_reaches_twice_threshold(write_log):
    rows = [(f"Jan 12 10:00:{sec:02d}", "192.0.2.11") for sec in range(0, 30, 3)]  # 10 kegagalan
    path = write_log(_failed_log(rows, user="zed"))

    alerts = detect_bruteforce(iter_events(path), threshold=5, window_seconds=60)

    assert alerts[0].failed_count == 10
    assert alerts[0].severity == "high"


def test_users_list_is_sorted_and_deduplicated(write_log):
    rows = []
    for idx, user in enumerate(["carol", "bob", "carol", "alice", "bob"]):
        rows.append(syslog_line(
            f"Failed password for {user} from 198.51.100.77 port {idx} ssh2",
            ts=f"Jan 12 11:00:{idx * 5:02d}",
        ))
    path = write_log("\n".join(rows) + "\n")

    alerts = detect_bruteforce(iter_events(path), threshold=5, window_seconds=60)

    assert alerts[0].users == ("alice", "bob", "carol")
    assert alerts[0].severity == "medium"


def test_no_alerts_for_empty_input():
    assert detect_bruteforce([]) == []
