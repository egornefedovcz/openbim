"""Google Search Console – dotazy, pozice, stránky. Servisní účet (JSON klíč) přidaný jako uživatel ve vlastnosti GSC.

Bez závislostí: JWT podepisuje `openssl` (je na macOS, Linuxu i na GitHub Actions).
"""
import base64, json, os, subprocess, tempfile, time, urllib.parse, urllib.request


def _b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()


def _token(sa):
    now = int(time.time())
    head = _b64(json.dumps({'alg': 'RS256', 'typ': 'JWT'}).encode())
    claim = _b64(json.dumps({'iss': sa['client_email'], 'scope': 'https://www.googleapis.com/auth/webmasters.readonly',
                             'aud': 'https://oauth2.googleapis.com/token', 'iat': now, 'exp': now + 3600}).encode())
    with tempfile.NamedTemporaryFile('w', suffix='.pem', delete=False) as k:
        k.write(sa['private_key']); key = k.name
    try:
        sig = subprocess.run(['openssl', 'dgst', '-sha256', '-sign', key], input=f'{head}.{claim}'.encode(), capture_output=True, check=True).stdout
    finally:
        os.unlink(key)
    body = urllib.parse.urlencode({'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion': f'{head}.{claim}.{_b64(sig)}'}).encode()
    return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', body, timeout=30))['access_token']


def _sa():
    v = os.environ.get('GSC_SA_JSON', '').strip().strip("'\"")
    if not v:
        raise RuntimeError('chybí GSC_SA_JSON (cesta k JSON klíči servisního účtu, nebo jeho obsah)')
    try:   # chybová hláška nesmí obsahovat hodnotu (je v ní soukromý klíč)
        return json.loads(v) if v.startswith('{') else json.load(open(v))
    except Exception:
        raise RuntimeError('GSC_SA_JSON není platný JSON ani cesta k souboru') from None


def query(site, start, end, dimensions=('query', 'page'), country=None):
    """řádky {query, page, clicks, impressions, position} za období (YYYY-MM-DD)"""
    tok = _token(_sa())
    url = 'https://www.googleapis.com/webmasters/v3/sites/%s/searchAnalytics/query' % urllib.parse.quote(site, safe='')
    rows, start_row = [], 0
    while True:
        body = {'startDate': start, 'endDate': end, 'dimensions': list(dimensions), 'rowLimit': 25000, 'startRow': start_row, 'type': 'web'}
        if country:
            body['dimensionFilterGroups'] = [{'filters': [{'dimension': 'country', 'expression': country}]}]
        req = urllib.request.Request(url, json.dumps(body).encode(), {'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
        got = json.load(urllib.request.urlopen(req, timeout=120)).get('rows', [])
        for r in got:
            rows.append({**dict(zip(dimensions, r['keys'])), 'clicks': r['clicks'], 'impressions': r['impressions'], 'position': r['position']})
        if len(got) < 25000:
            return rows
        start_row += 25000
