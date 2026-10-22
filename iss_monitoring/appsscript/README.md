# ISS Monitoring — web app Apps Script (opsi A, dibuat 22 Okt 2026)

Tampilan sama dengan artefak (dari `../index_src.html`); data dibaca dari tabel BigQuery `rg-crm.inside_sales.iss_monitoring_payload` (diisi `upload_bq.py`).

**Kenapa bukan Drive (22 Okt 2026):** Drive API dari login ADC butuh quota project, dan akun cxperience.analyst tidak punya `serviceusage.services.use` di project mana pun. BigQuery tidak butuh itu. Folder Drive "ISS Dashboard" dan `upload_drive.py` tidak dipakai lagi.

| Bagian | Isi |
|---|---|
| Pemilik | akun BigQuery `cxperience.analyst@ruangguru.com` |
| Folder data | https://drive.google.com/drive/folders/1WLZpoj4W8HF36LLCw-SHJo6T7pNald1r |
| File data | `weekly.json.gz`, `today.json.gz`, `daily.json.gz`, `calleffort.json.gz` (ID di `drive_ids.json`) |

## File
- `Code.gs` — `doGet()` + `getData(key)` (query BigQuery, cache 5 menit, kirim gzip base64; dibuka di browser).
- `appsscript.json` — manifest (advanced service BigQuery; web app execute as deployer, akses domain).
- `shim.js` — pengganti `fetch("data/*.json")` dan `window.claude` (download CSV jalan; ekspor ke Google Sheets belum).
- `build_appsscript.py` → `dist/Index.html` (jalankan ulang setiap `index_src.html` berubah, lalu paste ulang ke editor).
- `upload_bq.py` — upload 4 data ke tabel payload (WRITE_TRUNCATE).

## Setup sekali
1. Login ulang ADC dengan scope Drive (di Mac, akun cxperience.analyst):
   `gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/userinfo.email,openid,https://www.googleapis.com/auth/sqlservice.login`
   lalu `cp ~/.config/gcloud/application_default_credentials.json ~/Desktop/DS/_creds/`
2. `python3 upload_bq.py` (upload pertama, membuat tabel payload).
3. script.google.com (akun cxperience.analyst) → New project "ISS Monitoring" → isi `Code.gs`; tambah file HTML `Index` → paste `dist/Index.html`; Project Settings → centang "Show appsscript.json" → paste `appsscript.json`.
4. Jalankan `cekData` sekali (izinkan akses BigQuery) → log menampilkan 4 baris data.
5. Deploy → New deployment → Web app → Execute as: Me, Who has access: Anyone with Google account → salin URL /exec.

## Refresh data
Setelah `iss-artifact-refresh` / `call-effort-update` membangun JSON: `python3 _master/iss_monitoring/appsscript/upload_bq.py`. Web app memakai data baru paling lambat 5 menit kemudian (cache), tanpa deploy ulang. Deploy ulang hanya kalau tampilan/kode berubah (Manage deployments → Edit → New version, URL tetap).

## Uji 22 Okt 2026
Index.html diuji di Chromium dengan google.script.run tiruan + data asli (gzip+base64): Weekly, Today, Daily, Call Effort tampil tanpa error. Ukuran gzip: weekly 4,56 MB → ±0,62 MB; daily ±0,18 MB; calleffort ±0,17 MB.
