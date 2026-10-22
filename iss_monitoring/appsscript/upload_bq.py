"""Upload data ISS Monitoring ke BigQuery (rg-crm.inside_sales.iss_monitoring_payload) untuk web app Apps Script.
Satu baris per halaman: key, data (gzip JSON dalam base64), raw_bytes, updated_at. Tabel ditimpa (WRITE_TRUNCATE).
Pakai: python3 upload_bq.py   (tanpa paket tambahan; login dari DS/_creds/application_default_credentials.json)
Jalur Drive (upload_drive.py) tidak dipakai: Drive API butuh quota project, akun tidak punya serviceusage."""
import os, sys, json, gzip, base64, uuid, time, datetime, urllib.request, urllib.parse, urllib.error
H = os.path.dirname(os.path.abspath(__file__))
DS = os.path.abspath(os.path.join(H, "..", "..", ".."))
PROJECT, DATASET, TABLE = "rg-crm", "inside_sales", "iss_monitoring_payload"
SRC = {
    "weekly": "_master/weekly/weekly_data.json",
    "today": "_master/today/today.json",
    "daily": "_master/daily/daily.json",
    "calleffort": "_master/call_effort/calleffort.json",
}

def token():
    d = json.load(open(os.path.join(DS, "_creds", "application_default_credentials.json")))
    body = urllib.parse.urlencode({"client_id": d["client_id"], "client_secret": d["client_secret"],
                                   "refresh_token": d["refresh_token"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", body))["access_token"]

def req(method, url, tok, data=None, ctype="application/json"):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=data, method=method,
                                   headers={"Authorization": "Bearer " + tok, "Content-Type": ctype}))
        return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"GAGAL {e.code}: {e.read().decode()[:400]}")

def main():
    tok = token()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    rows, info = [], []
    for k, p in SRC.items():
        raw = open(os.path.join(DS, p), "rb").read()
        b64 = base64.b64encode(gzip.compress(raw, mtime=0)).decode()
        rows.append(json.dumps({"key": k, "data": b64, "raw_bytes": len(raw), "updated_at": now}))
        info.append(f"{k} {len(raw):,} -> {len(b64):,}")
    cfg = {"configuration": {"load": {
        "destinationTable": {"projectId": PROJECT, "datasetId": DATASET, "tableId": TABLE},
        "sourceFormat": "NEWLINE_DELIMITED_JSON", "writeDisposition": "WRITE_TRUNCATE",
        "createDisposition": "CREATE_IF_NEEDED",
        "schema": {"fields": [{"name": "key", "type": "STRING"}, {"name": "data", "type": "STRING"},
                              {"name": "raw_bytes", "type": "INT64"}, {"name": "updated_at", "type": "TIMESTAMP"}]}}}}
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(cfg)}\r\n"
            f"--{b}\r\nContent-Type: application/octet-stream\r\n\r\n").encode() + "\n".join(rows).encode() + f"\r\n--{b}--".encode()
    job = req("POST", f"https://bigquery.googleapis.com/upload/bigquery/v2/projects/{PROJECT}/jobs?uploadType=multipart",
              tok, body, f"multipart/related; boundary={b}")
    jid, loc = job["jobReference"]["jobId"], job["jobReference"].get("location", "")
    for _ in range(60):
        st = req("GET", f"https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT}/jobs/{jid}?location={loc}", tok)["status"]
        if st["state"] == "DONE":
            if st.get("errorResult"): sys.exit("GAGAL load: " + json.dumps(st["errorResult"]))
            break
        time.sleep(2)
    print(f"UPLOAD_BQ OK {PROJECT}.{DATASET}.{TABLE} ({now} UTC): " + "; ".join(info))

if __name__ == "__main__":
    main()
