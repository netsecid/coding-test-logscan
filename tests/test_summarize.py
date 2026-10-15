"""Test spesifikasi untuk `logscan.summarize` (TASK.md §3.3)."""

from __future__ import annotations

from logscan import summarize


def test_totals_on_tiny_log(tiny_events):
    result = summarize(tiny_events)

    assert result["total_events"] == 14
    assert result["failed_logins"] == 8
    assert result["successful_logins"] == 2
    assert result["unique_source_ips"] == 4  # 203.0.113.7, 192.0.2.55, 2001:db8::1, 198.51.100.22
    assert result["unique_users"] == 7  # root, admin, nobody, oracle, alice, bob, carol
    assert result["hosts"] == ["srv-01", "srv-02"]


def test_top_source_ips_ranking(tiny_events):
    top = summarize(tiny_events)["top_source_ips"]

    assert [entry["ip"] for entry in top] == [
        "203.0.113.7",
        "192.0.2.55",
        "2001:db8::1",
        "198.51.100.22",
    ]
    assert top[0] == {"ip": "203.0.113.7", "failures": 6, "successes": 0}
    assert top[2] == {"ip": "2001:db8::1", "failures": 1, "successes": 1}
    assert top[3] == {"ip": "198.51.100.22", "failures": 0, "successes": 1}


def test_top_source_ips_excludes_events_without_ip(tiny_events):
    top = summarize(tiny_events)["top_source_ips"]

    assert all(entry["ip"] for entry in top)


def test_top_usernames_only_counts_failed_passwords(tiny_events):
    top = summarize(tiny_events)["top_usernames"]

    assert [(entry["user"], entry["failures"]) for entry in top] == [
        ("root", 4),
        ("admin", 1),
        ("bob", 1),
        ("carol", 1),
        ("nobody", 1),
    ]


def test_empty_input_gives_zeroed_summary():
    result = summarize([])

    assert result["total_events"] == 0
    assert result["failed_logins"] == 0
    assert result["successful_logins"] == 0
    assert result["unique_source_ips"] == 0
    assert result["hosts"] == []
    assert result["top_source_ips"] == []
    assert result["top_usernames"] == []


def test_top_lists_are_capped_at_ten(write_log, tmp_path):
    from logscan import iter_events

    lines = [
        f"Jan 12 03:00:{i:02d} srv-01 sshd[1]: Failed password for user{i} from 10.0.0.{i} port 1 ssh2"
        for i in range(1, 13)  # 12 IP berbeda, masing-masing 1 kegagalan
    ]
    path = write_log("\n".join(lines) + "\n")

    result = summarize(iter_events(path))

    assert len(result["top_source_ips"]) == 10
    assert len(result["top_usernames"]) == 10
    assert result["unique_source_ips"] == 12
