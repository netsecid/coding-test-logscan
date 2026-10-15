# TASK — `logscan`: CLI Analisis Log Autentikasi SSH

**Durasi:** 90 menit · **Bahasa:** Python 3.11+ · **Dependency:** standard library + pytest
**Kerjakan di branch:** `solusi/<nama-kamu>`

---

## 0. Konteks

Tim SOC menerima kiriman file `auth.log` dari server produksi. Analis butuh alat kecil untuk
menjawab tiga pertanyaan dengan cepat:

1. Ada berapa percobaan login gagal, dan dari IP mana saja?
2. Username apa yang paling sering jadi sasaran?
3. Apakah ada pola **brute force** (banyak kegagalan dalam jendela waktu singkat)?

Target pemakaian: bisa dijalankan di laptop analis maupun di server kecil, terhadap file log
**ratusan ribu baris**, tanpa menghabiskan memori.

## 1. Format input

File syslog bergaya OpenSSH (tanpa tahun pada timestamp — ini yang bikin repot):

```
Jan 12 03:14:15 srv-01 sshd[1234]: Failed password for root from 203.0.113.7 port 51234 ssh2
Jan 12 03:14:20 srv-01 sshd[1235]: Failed password for invalid user admin from 203.0.113.7 port 51240 ssh2
Jan 12 03:15:02 srv-01 sshd[1236]: Accepted password for alice from 198.51.100.22 port 40222 ssh2
Jan 12 03:16:00 srv-01 sshd[1237]: Invalid user oracle from 203.0.113.7 port 51250 ssh2
Jan 12 03:20:11 srv-01 sshd[1240]: Connection closed by authenticating user root 203.0.113.7 port 51300 [preauth]
Jan 12 04:01:07 srv-01 sshd[1241]: Failed password for bob from 2001:db8::1 port 51411 ssh2
```

Variasi yang harus ditangani (muncul di `samples/`):

- `Failed password for <user> ...` dan `Failed password for invalid user <user> ...`
- `Accepted password for <user> ...` (juga boleh ada `Accepted publickey`)
- `Invalid user <user> from <ip> port ...`
- `Connection closed by <ip> ...` / `Connection closed by authenticating user <user> <ip> ...` / `... invalid user <user> ...`
- Baris dari proses lain (`cron`, `sudo`, `systemd-logind`) → tetap valid secara syslog, tapi bukan event SSH
- Baris rusak / terpotong (tanpa timestamp) → **bukan error**, cukup dilewati
- Timestamp hari satu digit: `Jan  2 09:00:00` (dua spasi)
- IP IPv4 dan IPv6
- Baris tidak urut kronologis

## 2. Aturan parsing

| Hal | Ketentuan |
|-----|-----------|
| Timestamp | `%b %d %H:%M:%S`, tanpa tahun. Tahun diambil dari parameter `year` (default `2026`) |
| `host` | token hostname setelah timestamp (contoh `srv-01`) |
| `kind` | `failed_password`, `accepted_password`, `invalid_user`, `connection_closed`, atau `other` |
| `user` | username bila ada di baris; `None` kalau tidak ada (mis. `Connection closed by <ip> ...` tanpa user) |
| `ip` | string IP apa adanya, tanpa normalisasi. Untuk baris `other` yang tidak memuat IP, isi string kosong `""` |
| Baris gagal parse | `parse_line()` mengembalikan `None`. **Jangan pernah melempar exception** |
| Baris kosong | baris yang jadi kosong setelah `.strip()` diabaikan sepenuhnya (bukan `malformed`, tapi tetap masuk hitungan `total_lines`) |

`Accepted publickey for <user> from <ip> ...` → `kind="accepted_password"` (ya, namanya tetap itu).

## 3. API yang harus diimplementasikan

Semua di paket `logscan/`. Signature dan nama **jangan diubah** — test memanggilnya langsung.

### 3.1 `logscan.models`

```python
@dataclass(frozen=True)
class Event:
    ts: datetime          # sudah ada tahun, naive, urut apa adanya dari file
    host: str
    user: str | None
    ip: str
    kind: str             # lihat tabel di §2
    raw: str              # baris asli tanpa newline

@dataclass(frozen=True)
class Alert:
    ip: str
    start: datetime       # percobaan pertama pada rangkaian
    end: datetime         # percobaan terakhir pada rangkaian
    failed_count: int     # jumlah percobaan gagal pada rentang [start, end]
    users: tuple[str, ...]  # username unik, terurut A→Z; username tak diketahui tidak dimasukkan
    severity: str         # "high" | "medium"
```

### 3.2 `logscan.parser`

```python
def parse_line(line: str, year: int = 2026) -> Event | None
def iter_events(path: str | Path, year: int = 2026) -> Iterator[Event]   # generator!
```

- `iter_events` **wajib generator/iterator streaming**: tidak boleh membaca seluruh file ke memori
  (hidden test memproses file 500k baris) dan tidak boleh mengembalikan `list`.
- `iter_events` melempar `FileNotFoundError` kalau file tidak ada (biarkan exception bawaan).

### 3.3 `logscan.summarize`

```python
def summarize(events: Iterable[Event]) -> dict
```

Return dict dengan tipe berikut (urutan key tidak penting):

```python
{
  "total_events": int,
  "failed_logins": int,          # kind == "failed_password"
  "successful_logins": int,      # kind == "accepted_password"
  "unique_source_ips": int,      # IP unik, hanya dari event yang ip-nya tidak kosong
  "unique_users": int,           # user != None
  "hosts": list[str],            # unik, terurut A→Z
  "top_source_ips": list[dict],  # {"ip": str, "failures": int, "successes": int}
  "top_usernames": list[dict],   # {"user": str, "failures": int}
}
```

Aturan peringkat:
- `top_source_ips`: maksimal **10** entri, urut `failures` DESC, lalu `ip` ASC. Hanya IP dengan
  `failures >= 1` yang masuk? **Tidak** — masukkan semua IP yang muncul, `failures` boleh 0
  (mis. IP yang hanya sukses login).
- `top_usernames`: maksimal **10** entri, urut `failures` DESC, lalu `user` ASC. Hanya user yang
  punya minimal 1 kegagalan (`failed_password`).
- Semua nilai integer, siap di-`json.dumps()`.

### 3.4 `logscan.bruteforce`

```python
def detect_bruteforce(events: Iterable[Event], threshold: int = 5,
                      window_seconds: int = 60) -> list[Alert]
```

Definisi **eksak** (jangan improvisasi, ini yang diuji):

1. Yang dihitung sebagai percobaan gagal **hanya** `kind == "failed_password"`.
   (Baris `invalid_user` **tidak** ikut dihitung.)
2. Kelompokkan per `ip`, urutkan timestamp menaik.
3. Untuk setiap IP, jalankan greedy scan dari percobaan paling awal:
   - `i` = indeks percobaan; `j` = indeks terbesar sehingga `t[j] - t[i] <= window_seconds`.
   - Kalau jumlah percobaan pada rentang `i..j` (`j - i + 1`) `>= threshold` → **satu** alert:
     `start = t[i]`, `end = t[j]`, `failed_count = j - i + 1`,
     `users` = username unik pada rentang itu (terurut A→Z), lalu lompat `i = j + 1`.
   - Kalau tidak memenuhi → `i += 1`.
   - Karena itu, alert per IP **tidak saling tumpang tindih**.
4. `severity = "high"` kalau `failed_count >= 2 * threshold` **atau** `users` memuat `"root"`
   atau `"admin"`; selain itu `"medium"`.
5. Hasil diurutkan `start` ASC lalu `ip` ASC.

### 3.5 `logscan.cli` / `logscan.__main__`

```bash
python -m logscan <logfile> [--json] [--top N] [--threshold N] [--window S] [--year YYYY]
```

- Default: `--top 10`, `--threshold 5`, `--window 60`, `--year 2026`.
- `scan_file(path, threshold=5, window_seconds=60, top=10, year=2026) -> dict` menghasilkan
  dict yang **sama dengan `summarize()`** ditambah 4 key berikut:

  ```python
  {
    "file": str,               # path apa adanya dari argumen
    "total_lines": int,        # jumlah baris fisik (termasuk baris kosong)
    "malformed_lines": int,    # baris tidak kosong yang gagal di-parse
    "alerts": list[dict],      # dari detect_bruteforce, tapi start/end => string ISO 8601
  }
  ```

- `top` hanya memotong panjang `top_source_ips` dan `top_usernames`.
- `alerts[i]` = `{"ip", "start", "end", "failed_count", "users" (list), "severity"}`,
  `start`/`end` format `YYYY-MM-DDTHH:MM:SS` (pakai `datetime.isoformat()`).
- `--json`: cetak `json.dumps(result, indent=2, ensure_ascii=False)`.
- Tanpa `--json`: cetak laporan manusiawi dengan 4 seksi **berjudul persis**:
  `RINGKASAN`, `TOP SOURCE IP`, `TOP USERNAME`, `ALERT BRUTE FORCE`.
  Kalau tidak ada alert, seksi terakhir berisi teks: `Tidak ada indikasi brute force.`
- File tidak ada / tidak bisa dibaca: tulis pesan ke **stderr** berisi kata
  `file tidak ditemukan` atau `tidak bisa dibaca`, keluar dengan exit code **2**.
- Sukses: exit code **0**.

## 4. Test

```bash
make test        # = python -m pytest -q
```

`tests/` berisi **test spesifikasi** yang saat ini merah semua (fungsi masih `TODO`).
Test itu adalah kontrak — jangan diubah agar hijau dengan cara curang (menghapus assert,
menambah `skip`, dsb). Menambah test **baru** di file terpisah justru nilai plus.

## 5. Checklist terakhir sebelum push

- [ ] `make test` hijau
- [ ] `make demo` jalan tanpa error
- [ ] Skenario di §1 (`samples/`) sudah dicoba manual
- [ ] `NOTES.md` diisi (asumsi, yang belum selesai, rencana lanjutan)
- [ ] Tidak ada `print()` debug nyasar, tidak ada file `__pycache__`/`.venv` ter-commit
- [ ] Push ke branch `solusi/<nama-kamu>`
