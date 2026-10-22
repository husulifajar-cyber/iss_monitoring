// ISS Monitoring — web app. Data dari BigQuery rg-crm.inside_sales.iss_monitoring_payload (diisi upload_bq.py).
const BQ_PROJECT = 'rg-crm';
const BQ_TABLE = '`rg-crm.inside_sales.iss_monitoring_payload`';
const KEYS = ['weekly', 'today', 'daily', 'calleffort'];
const CACHE_DETIK = 300;   // data di-cache 5 menit supaya tiap buka halaman tidak query BigQuery
const POTONG = 90000;      // batas cache 100 KB per kunci

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('ISS Monitoring')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function query_(sql, params) {
  let res = BigQuery.Jobs.query({
    query: sql, useLegacySql: false, timeoutMs: 60000,
    parameterMode: 'NAMED', queryParameters: params || []
  }, BQ_PROJECT);
  const jobId = res.jobReference.jobId, loc = res.jobReference.location;
  while (!res.jobComplete) {
    Utilities.sleep(1000);
    res = BigQuery.Jobs.getQueryResults(BQ_PROJECT, jobId, { location: loc });
  }
  return res.rows || [];
}

/** Isi data (gzip JSON dalam base64) untuk satu halaman, atau null. */
function getData(key) {
  if (KEYS.indexOf(key) < 0) return null;
  const cache = CacheService.getScriptCache();
  const n = cache.get('n_' + key);
  if (n) {
    const names = [];
    for (let i = 0; i < +n; i++) names.push(key + '_' + i);
    const got = cache.getAll(names);
    if (Object.keys(got).length === +n) return names.map(function (x) { return got[x]; }).join('');
  }
  const rows = query_('SELECT data FROM ' + BQ_TABLE + ' WHERE key = @k LIMIT 1',
    [{ name: 'k', parameterType: { type: 'STRING' }, parameterValue: { value: key } }]);
  if (!rows.length) return null;
  const data = rows[0].f[0].v;
  try {
    const parts = {};
    let i = 0;
    for (let s = 0; s < data.length; s += POTONG) parts[key + '_' + (i++)] = data.slice(s, s + POTONG);
    cache.putAll(parts, CACHE_DETIK);
    cache.put('n_' + key, String(i), CACHE_DETIK);
  } catch (e) { /* cache penuh: tetap kirim data */ }
  return data;
}

/** Jalankan dari editor untuk cek akses BigQuery & kapan data terakhir di-upload. */
function cekData() {
  query_('SELECT key, raw_bytes, CAST(updated_at AS STRING) FROM ' + BQ_TABLE + ' ORDER BY key')
    .forEach(function (r) { Logger.log(r.f[0].v + ': ' + r.f[1].v + ' byte, upload ' + r.f[2].v + ' UTC'); });
}
