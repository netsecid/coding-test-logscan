"""Test spesifikasi untuk `logscan.cli` (TASK.md §3.5)."""

from __future__ import annotations

import json

import pytest

from logscan import main, render_report, scan_file
from logscan.cli import NO_ALERT_TEXT, SECTION_TITLES

CLI_KEYS = {
    "file",
    "total_lines",
    "malformed_lines",
    "total_events",
    "failed_logins",
    "successful_logins",
    "unique_source_ips",
    "unique_users",
    "hosts",
    "top_source_ips",
    "top_usernames",
    "alerts",
}


def test_scan_file_reports_file_level_counters(tiny_path):
    result = scan_file(str(tiny_path))

    assert CLI_KEYS <= set(result)
    assert result["file"] == str(tiny_path)
    assert result["total_lines"] == 16  # termasuk 1 baris kosong
    assert result["malformed_lines"] == 1
    assert result["total_events"] == 14
    assert result["failed_logins"] == 8


def test_alerts_use_iso_timestamps(tiny_path):
    alerts = scan_file(str(tiny_path))["alerts"]

    assert len(alerts) == 1
    alert = alerts[0]
    assert set(alert) == {"ip", "start", "end", "failed_count", "users", "severity"}
    assert alert["start"] == "2026-01-12T03:14:15"
    assert alert["end"] == "2026-01-12T03:14:35"
    assert alert["failed_count"] == 5
    assert alert["users"] == ["admin", "root"]
    assert alert["severity"] == "high"
    json.dumps(alert)  # harus JSON-serializable


def test_top_option_truncates_both_rankings(tiny_path):
    result = scan_file(str(tiny_path), top=1)

    assert len(result["top_source_ips"]) == 1
    assert len(result["top_usernames"]) == 1
    assert result["unique_source_ips"] == 4  # tetap dihitung utuh


def test_threshold_option_is_honoured(tiny_path):
    assert scan_file(str(tiny_path), threshold=6)["alerts"] == []


def test_window_option_is_honoured(tiny_path):
    alerts = scan_file(str(tiny_path), window_seconds=90)["alerts"]

    assert len(alerts) == 1
    assert alerts[0]["failed_count"] == 6


def test_year_option_is_honoured(tiny_path):
    result = scan_file(str(tiny_path), year=2020)

    assert result["alerts"][0]["start"].startswith("2020-01-12T03:14:15")


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def test_human_report_contains_all_sections(tiny_path):
    report = render_report(scan_file(str(tiny_path)))

    for title in SECTION_TITLES:
        assert title in report


def test_human_report_says_no_alert_when_clean(tiny_path):
    report = render_report(scan_file(str(tiny_path), threshold=6))

    assert NO_ALERT_TEXT in report


def test_main_prints_json(tiny_path, capsys):
    exit_code = main([str(tiny_path), "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["total_events"] == 14
    assert payload["alerts"][0]["ip"] == "203.0.113.7"


def test_main_prints_human_report(tiny_path, capsys):
    exit_code = main([str(tiny_path)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "TOP SOURCE IP" in out
    assert "203.0.113.7" in out


def test_main_exits_2_for_missing_file(tmp_path, capsys):
    exit_code = main([str(tmp_path / "tidak-ada.log")])

    assert exit_code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "tidak ditemukan" in captured.err or "tidak bisa dibaca" in captured.err


def test_main_respects_threshold_and_window_flags(tiny_path, capsys):
    assert main([str(tiny_path), "--json", "--threshold", "6"]) == 0
    assert json.loads(capsys.readouterr().out)["alerts"] == []

    assert main([str(tiny_path), "--json", "--window", "90"]) == 0
    assert json.loads(capsys.readouterr().out)["alerts"][0]["failed_count"] == 6
