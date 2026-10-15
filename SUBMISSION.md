# SUBMISSION — Cara Mengumpulkan

## 1. Sebelum push

```bash
make test                 # harus hijau
git status                # pastikan .venv/ dan __pycache__/ tidak ikut
```

Buat `NOTES.md` di root repo (wajib, ~10 baris cukup):

```markdown
# NOTES — <Nama Kamu>

## Asumsi
- ...

## Yang belum selesai / tidak sempat
- ...

## Kalau ada waktu 2x lipat
- ...
```

## 2. Push hasil

```bash
git add -A
git commit -m "solusi: logscan oleh <nama-kamu>"
git push -u origin solusi/<nama-kamu>
```

Repo ini read-only untuk kandidat. Jadi pilih salah satu:

**Opsi A — fork (disarankan)**

1. Fork repo ini ke akun GitHub kamu.
2. Kerjakan di fork, push ke sana, lalu share link fork-nya.

**Opsi B — kirim patch**

```bash
git format-patch main --stdout > logscan-<nama-kamu>.patch
# kirim file .patch via DM Discord #coding-bot
```

**Opsi C — git bundle**

```bash
git bundle create logscan-<nama-kamu>.bundle --all
# kirim file .bundle via DM Discord #coding-bot
```

## 3. Yang dikirim

Format pesan (kirim di Discord **#coding-bot**, DM ke instruktur, atau thread review):

```text
Nama      : <nama lengkap>
Posisi    : <posisi yang dilamar / tujuan latihan>
Repo/Fork : <link>
Waktu     : <menit yang dipakai>
Ringkas   : <1-3 kalimat: bagian tersulit + keputusan desain utama>
```

## 4. Sesudahnya

Kamu akan dijadwalkan sesi review **30 menit** (live, screen share opsional):

1. Kamu jelaskan alur solusi (5 menit).
2. Kami minta perubahan kecil on-the-fly (mis. tambah threshold per-username) — untuk melihat
   cara kamu bernavigasi di kode sendiri (15 menit).
3. Umpan balik + pertanyaan kamu (10 menit).

Yang **tidak** kami nilai: kamu hafal API, kamu cepat mengetik, atau kode kamu langsung benar.
Yang kami nilai: kamu paham kode sendiri, tahu trade-off-nya, dan jujur soal batasannya.
