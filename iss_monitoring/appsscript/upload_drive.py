"""Upload data ISS Monitoring (gzip) ke folder Drive yang dibaca web app Apps Script.
Pakai: python3 upload_drive.py [weekly today daily calleffort]   (default: semua)
Login: DS/_creds/application_default_credentials.json, harus punya scope Drive
(gcloud auth application-default login --scopes=...cloud-platform,...drive). Tanpa paket tambahan."""
import os, sys, json, gzip, uuid, urllib.request, urllib.parse, urllib.error
H = os.path.dirname(os.path.abspath(__file__))
DS = os.path.abspath(os.path.join(H, "..", "..", ".."))
FOLDER_ID = "1WLZpoj4W8HF36LLCw-SHJo6T7pNald1r"
SRC = {
    "weekly": "_master/weekly/weekly_data.json",
    "today": "_master/today/today.json",
    "daily": "_master/daily/daily.json",
    "calleffort": "_master/call_effort/calleffort.json",
}
IDS = os.path.join(H, "drive_ids.json")

def token():
    d = json.load(open(os.path.join(DS, "_creds", "application_default_credentials.json")))
    body = urllib.parse.urlencode({"client_id": d["client_id"], "client_secret": d["client_secret"],
                                   "refresh_token": d["refresh_token"], "grant_type": "refresh_token"}).encode()
    t = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", body))
    if "auth/drive" not in t.get("scope", ""):
        sys.exit("LOGIN_TANPA_DRIVE: login ulang ADC dengan scope Drive (lihat README).")
    return t["access_token"]

def call(method, url, tok, data=None, ctype=None):
    h = {"Authorization": "Bearer " + tok}
    if ctype: h["Content-Type"] = ctype
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h, method=method)))
    except urllib.error.HTTPError as e:
        sys.exit(f"GAGAL {e.code} {url.split('?')[0]}: {e.read().decode()[:300]}")

def main(keys):
    tok = token()
    ids = json.load(open(IDS)) if os.path.exists(IDS) else {}
    for k in keys:
        name = k + ".json.gz"
        raw = open(os.path.join(DS, SRC[k]), "rb").read()
        gz = gzip.compress(raw, mtime=0)
        fid = ids.get(k)
        if not fid:  # cari file lama di folder
            q = urllib.parse.quote(f"name='{name}' and '{FOLDER_ID}' in parents and trashed=false")
            r = call("GET", f"https://www.googleapis.com/drive/v3/files?q={q}&fields=files(id)&supportsAllDrives=true&includeItemsFromAllDrives=true", tok)
            fid = r["files"][0]["id"] if r.get("files") else None
        if fid:
            call("PATCH", f"https://www.googleapis.com/upload/drive/v3/files/{fid}?uploadType=media&supportsAllDrives=true",
                 tok, gz, "application/gzip")
            act = "update"
        else:
            b = uuid.uuid4().hex
            meta = json.dumps({"name": name, "parents": [FOLDER_ID], "mimeType": "application/gzip"}).encode()
            body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode() + meta +
                    f"\r\n--{b}\r\nContent-Type: application/gzip\r\n\r\n".encode() + gz + f"\r\n--{b}--".encode())
            fid = call("POST", "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true",
                       tok, body, f"multipart/related; boundary={b}")["id"]
            act = "baru"
        ids[k] = fid
        print(f"UPLOAD {k}: {act} {len(raw):,} -> {len(gz):,} byte (id {fid})")
    json.dump(ids, open(IDS, "w"), indent=1)

if __name__ == "__main__":
    main(sys.argv[1:] or list(SRC))
