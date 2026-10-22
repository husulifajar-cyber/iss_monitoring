# ISS Monitoring — tampilan bersama & target publish (dibuat 19 Okt 2026)

Artefak ISS Monitoring (halaman Today, Daily, Weekly, Call Effort) ada di dua akun Claude dengan tampilan yang sama:

| Akun | Artefak |
|---|---|
| pribadi | https://claude.ai/artifact/EY4t8ZPsd9y7ZV3osvPWmp |
| kantor | https://claude.ai/artifact/3LJm3LZNgWzuXYxPvDN27x |

## Isi folder
- `target.json` — daftar artefak, aturan memilih target, link yang sedang dibagikan ke tim (`dibagikan_ke_tim`), sha tampilan (`layout`) dan tampilan terakhir yang dipublish per akun (`layout_publish`).
- `index_src.html` — **sumber tampilan bersama** (isi halaman mulai `<title>` s/d sebelum `</body></html>`). Semua publish memakai file ini.
- `layout.py` — cek tampilan live vs `index_src.html` sebelum publish (`extract`, `check`, `mark`, `adopt`).
- `export_kantor_2026-10-19.html`, `tracker.json` — export zip artefak kantor 19 Okt 2026 (arsip; tracker disembunyikan di halaman).

## Aturan
1. Publish selalu ke artefak milik akun yang sedang dipakai (pribadi → EY4t…, kantor → 3LJm…). Data BigQuery sama untuk keduanya.
2. Sebelum publish, `layout.py check <akun> <live.html>`:
   - `SAMA` / `DS_LEBIH_BARU` → publish `index_src.html`.
   - `LIVE_BERUBAH` → tampilan diubah langsung di artefak. Berhenti, tanya user mau pakai versi live (lalu `adopt`) atau timpa dengan `index_src.html`.
3. Kalau tampilan diubah (fitur/halaman baru), simpan hasilnya ke `index_src.html` (pakai `adopt`) supaya akun lain ikut versi yang sama.
4. Catatan "data terakhir dipublish" per akun ada di `DS/_skills/iss-artifact-refresh/last_publish.json` (`refresh_data.py --akun …`).
