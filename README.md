# Coding Test — Log Analyser (`logscan`)

Simulasi **technical interview coding test** (take-home style, 90 menit, closed-book).
Semua kandidat mengerjakan tugas yang sama: membangun CLI analisis log autentikasi.

> ⚠️ Repo ini adalah **soal ujian**, bukan solusi. Jangan commit solusi ke repo ini.

---

## 1. Mulai dari sini

```bash
git clone https://github.com/netsecid/coding-test-logscan.git
cd coding-test-logscan
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Baca **`TASK.md`** (spesifikasi lengkap) sebelum menulis kode. Jangan lompat ke kode.

## 2. Alur pengerjaan

| # | Langkah | Perintah |
|---|---------|----------|
| 1 | Clone repo | `git clone <url>` |
| 2 | Buat branch kerja | `git switch -c solusi/<nama-kamu>` |
| 3 | Baca spesifikasi | `less TASK.md` |
| 4 | Implementasi | edit `logscan/*.py` (ada `TODO` di tiap fungsi) |
| 5 | Jalankan test | `make test` |
| 6 | Cek manual | `make demo` |
| 7 | Isi catatan | edit `NOTES.md` |
| 8 | Commit + push | `git push -u origin solusi/<nama-kamu>` |
| 9 | Kirim link | lihat `SUBMISSION.md` |

## 3. Aturan

- ⏱️ **Timebox 90 menit.** Tidak selesai 100% itu normal — kami menilai cara berpikir, bukan kelengkapan.
- 🚫 **Tanpa AI generatif** (ChatGPT/Copilot/Claude/Cursor dsb). Ini simulasi interview asli.
  Boleh: dokumentasi Python, `man`, Stack Overflow *dibaca* (bukan tempel ke AI).
- 🧠 Tulis kode sendiri. Kalau nyontek solusi orang lain, sesi interview lanjutan akan cepat ketahuan.
- 💬 Tulis **`NOTES.md`**: asumsi yang kamu ambil, yang belum selesai, dan langkah berikutnya kalau ada waktu 2x lipat.
- ✅ Boleh pakai standard library + `pytest`. Jangan tambah dependency lain.

## 4. Yang dinilai

| Bobot | Aspek | Yang dilihat |
|-------|-------|--------------|
| 35% | Kebenaran fungsional | `make test` hijau, output CLI sesuai spesifikasi |
| 20% | Ketahanan (edge case) | baris rusak, file kosong, IPv6, lintas tengah malam, input tidak terurut |
| 15% | Kualitas kode | penamaan, pemisahan tanggung jawab, tanpa duplikasi, type hint |
| 15% | Test yang kamu tulis sendiri | ada test tambahan di luar `tests/` bawaan, kasusnya bermakna |
| 10% | Performa & memori | `iter_events` streaming, file 500k baris tidak habis di RAM |
| 5% | Komunikasi | `NOTES.md` jelas, keputusan teknis dijelaskan singkat |

## 5. Kirim hasil

Ikuti `SUBMISSION.md`. Deadline & penjadwalan sesi review diumumkan di Discord **#coding-bot**.

---

Dokumen kandidat: [`TASK.md`](TASK.md) · [`SUBMISSION.md`](SUBMISSION.md)
