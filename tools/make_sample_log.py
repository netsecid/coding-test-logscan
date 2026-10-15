"""Generator file log contoh untuk menguji skala (dipakai `make demo` / `samples/`).

Jalankan: ``python3 tools/make_sample_log.py``
Output:   ``samples/auth_sample.log`` (~800 baris, 3 pola brute force + 1 pola
          lambat yang bukan brute force, sebagai kontrol negatif).
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "samples" / "auth_sample.log"
HOSTS = ["srv-01", "srv-02", "web-03"]
USERS = ["root", "admin", "deploy", "oracle", "alice", "bob", "carol", "ubuntu"]


def _fmt(ts: datetime) -> str:
    return ts.strftime("%b %d %H:%M:%S")


def _line(ts: datetime, host: str, body: str) -> str:
    return f"{_fmt(ts)} {host} sshd[{random.randint(1000, 9999)}]: {body}"


def build() -> list[str]:
    random.seed(1337)
    start = datetime(2026, 1, 12, 0, 0, 0)
    lines: list[str] = []
    ip_pool = [f"203.0.113.{n}" for n in range(2, 40)] + [
        f"198.51.100.{n}" for n in range(2, 40)
    ] + ["2001:db8::1", "2001:db8::2"]

    # Latar belakang normal: login berhasil + sedikit gagal salah ketik password.
    ts = start
    while ts < start + timedelta(hours=23):
        ts += timedelta(seconds=random.randint(40, 180))
        host = random.choice(HOSTS)
        user = random.choice(USERS)
        ip = random.choice(ip_pool)
        roll = random.random()
        if roll < 0.55:
            lines.append(_line(ts, host, f"Accepted password for {user} from {ip} port {random.randint(1024, 65000)} ssh2"))
        elif roll < 0.72:
            lines.append(_line(ts, host, f"Failed password for {user} from {ip} port {random.randint(1024, 65000)} ssh2"))
        elif roll < 0.80:
            lines.append(_line(ts, host, f"Invalid user {user}x from {ip} port {random.randint(1024, 65000)}"))
        elif roll < 0.86:
            lines.append(_line(ts, host, f"Connection closed by authenticating user {user} {ip} port {random.randint(1024, 65000)} [preauth]"))
        elif roll < 0.92:
            lines.append(f"{_fmt(ts)} {host} cron[9999]: (root) CMD (/usr/local/bin/backup.sh)")
        elif roll < 0.96:
            lines.append(f"{_fmt(ts)} {host} sudo:    {user} : TTY=pts/0 ; PWD=/home/{user} ; USER=root ; COMMAND=/bin/systemctl restart nginx")
        else:
            lines.append("-- rotasi log: berkas log di-truncate oleh logrotate --")  # baris rusak

    # Pola 1: brute force cepat (8 kegagalan dalam ~40 detik) → alert high.
    burst = start + timedelta(hours=3, minutes=14)
    for n in range(8):
        ts = burst + timedelta(seconds=n * 5)
        user = "root" if n % 2 == 0 else "admin"
        lines.append(_line(ts, "srv-01", f"Failed password for {user} from 203.0.113.7 port {51234 + n} ssh2"))

    # Pola 2: password spraying — 20 percobaan dalam 1 menit, 14 user berbeda → alert high.
    spray = start + timedelta(hours=13, minutes=30)
    spray_users = USERS + ["git", "jenkins", "postgres", "mysql"]
    for n in range(20):
        ts = spray + timedelta(seconds=n * 3)
        user = spray_users[n % len(spray_users)]
        lines.append(_line(ts, "web-03", f"Failed password for {user} from 198.51.100.66 port {40000 + n} ssh2"))

    # Pola 3: brute force moderat 6 kegagalan / 25 detik → alert medium (bukan user istimewa).
    moderat = start + timedelta(hours=20, minutes=5)
    for n in range(6):
        ts = moderat + timedelta(seconds=n * 5)
        lines.append(_line(ts, "srv-02", f"Failed password for deploy from 192.0.2.200 port {33000 + n} ssh2"))

    # Pola 4 (negatif): 5 kegagalan tersebar 5 menit sekali → TIDAK boleh jadi alert.
    lambat = start + timedelta(hours=6, minutes=10)
    for n in range(5):
        ts = lambat + timedelta(minutes=n * 5)
        lines.append(_line(ts, "srv-02", f"Failed password for oracle from 192.0.2.99 port {34000 + n} ssh2"))

    # Urutkan campur-campur: file asli tidak selalu urut kronologis.
    random.shuffle(lines)
    return lines


def main() -> None:
    lines = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT} ditulis: {len(lines)} baris")


if __name__ == "__main__":
    main()
