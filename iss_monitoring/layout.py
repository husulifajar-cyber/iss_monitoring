#!/usr/bin/env python3
"""Penjaga tampilan (index.html) artefak ISS Monitoring di dua akun (pribadi & kantor).

Sumber tampilan bersama: index_src.html di folder ini (isi halaman mulai baris <title> s/d sebelum </body></html>).
Target artefak & catatan publish: target.json di folder ini.

  python3 layout.py extract <file_hasil_artifact_read> <keluar.html>   # potong skeleton -> isi halaman live
  python3 layout.py check <akun> <live.html>       # bandingkan tampilan live vs index_src.html
       SAMA            -> live = index_src; publish pakai index_src.html
       DS_LEBIH_BARU   -> live = versi yang terakhir dipublish ke akun itu, index_src sudah diperbarui; publish index_src.html
       LIVE_BERUBAH    -> tampilan live diubah langsung di artefak (di luar DS); STOP, tanya user versi mana yang dipakai
  python3 layout.py mark <akun> <file_yang_dipublish.html>   # catat sha tampilan setelah publish sukses
  python3 layout.py adopt <live.html>              # jadikan live sebagai index_src.html baru (setelah user setuju)
Bisa dijalankan di shell device atau di container (path dikirim sebagai argumen).
"""
import sys, os, json, hashlib, datetime as dt, re
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "index_src.html"); TGT = os.path.join(HERE, "target.json")
now = lambda: dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")
def norm(t): return re.sub(r"\s+$", "", t.replace("\r\n", "\n"))
def sha_txt(t): return hashlib.sha1(norm(t).encode()).hexdigest()
def sha_file(p): return sha_txt(open(p, encoding="utf-8").read())
def extract(t):
    a = t.find("<title>"); a = t.rfind("\n", 0, a) + 1 if a >= 0 else 0
    b = t.rfind("</body></html>"); b = len(t) if b < 0 else b
    return t[a:b]
T = json.load(open(TGT))
cmd = sys.argv[1] if len(sys.argv) > 1 else ""
if cmd == "extract":
    open(sys.argv[3], "w", encoding="utf-8").write(extract(open(sys.argv[2], encoding="utf-8").read())); print("ok", sys.argv[3])
elif cmd == "check":
    akun, live = sys.argv[2], sha_file(sys.argv[3]); src = sha_file(SRC)
    last = T.get("layout_publish", {}).get(akun, {}).get("sha")
    print("SAMA" if live == src else "DS_LEBIH_BARU" if live == last else "LIVE_BERUBAH",
          f"(live {live[:10]} | index_src {src[:10]} | terakhir dipublish ke {akun} {(last or '-')[:10]})")
elif cmd == "mark":
    akun = sys.argv[2]; T.setdefault("layout_publish", {})[akun] = dict(sha=sha_file(sys.argv[3]), at=now())
    json.dump(T, open(TGT, "w"), indent=1, ensure_ascii=False); print("tercatat", akun, T["layout_publish"][akun])
elif cmd == "adopt":
    open(SRC, "w", encoding="utf-8").write(norm(open(sys.argv[2], encoding="utf-8").read()) + "\n")
    T["layout"] = dict(sha=sha_file(SRC), updated=now(), note="diambil dari artefak live"); json.dump(T, open(TGT, "w"), indent=1, ensure_ascii=False)
    print("index_src.html diganti; sha", T["layout"]["sha"][:10])
else:
    print(__doc__)
