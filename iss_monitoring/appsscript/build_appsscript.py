"""Bangun Index.html untuk Apps Script dari tampilan bersama index_src.html.
Pakai: python3 build_appsscript.py  -> menulis dist/Index.html (paste ke file Index di editor Apps Script)."""
import os, hashlib
H = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(H, "..", "index_src.html"), encoding="utf-8").read()
shim = open(os.path.join(H, "shim.js"), encoding="utf-8").read()
for k in ("data/weekly.json", "data/today.json", "data/daily.json", "data/calleffort.json"):
    assert f'fetch("{k}")' in src, f"titik fetch {k} tidak ditemukan - tampilan berubah, cek shim.js"
head, sep, body = src.partition("</style>")
assert sep, "</style> tidak ditemukan"
out = ("<!DOCTYPE html>\n<html lang=\"id\">\n<head>\n<base target=\"_top\">\n<meta charset=\"utf-8\">\n"
       + head + sep + "\n<script>\n" + shim + "\n</script>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")
os.makedirs(os.path.join(H, "dist"), exist_ok=True)
p = os.path.join(H, "dist", "Index.html")
open(p, "w", encoding="utf-8").write(out)
print("OK", p, len(out), "byte; sha tampilan", hashlib.sha1(src.encode()).hexdigest()[:12])
