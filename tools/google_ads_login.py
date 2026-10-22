#!/usr/bin/env python3
"""Jednorázové přihlášení ke Google Ads API → refresh token do .env (GOOGLE_ADS_REFRESH_TOKEN).
Spustí lokální server na 127.0.0.1:8765, vypíše odkaz; po přihlášení uloží token. Token nevypisuje."""
import http.server, json, os, secrets, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.path.join(ROOT, '.env')
cfg = dict(l.strip().split('=', 1) for l in open(ENV) if '=' in l and not l.startswith('#'))
CID, SEC = cfg['GOOGLE_ADS_CLIENT_ID'], cfg['GOOGLE_ADS_CLIENT_SECRET']
PORT, STATE = 8765, secrets.token_urlsafe(16)
REDIR = f'http://127.0.0.1:{PORT}/'
url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode({'client_id': CID, 'redirect_uri': REDIR, 'response_type': 'code',
      'scope': 'https://www.googleapis.com/auth/adwords', 'access_type': 'offline', 'prompt': 'consent', 'state': STATE})
print('Otevřete a přihlaste se účtem s přístupem k Google Ads ArtMoment CZ:\n' + url, flush=True)
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(self.path).query))
        ok = q.get('state') == STATE and 'code' in q
        if ok:
            body = urllib.parse.urlencode({'code': q['code'], 'client_id': CID, 'client_secret': SEC, 'redirect_uri': REDIR, 'grant_type': 'authorization_code'}).encode()
            try:
                t = json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', body, timeout=30))
                rt = t.get('refresh_token')
                if rt:
                    lines = [l for l in open(ENV) if not l.startswith('GOOGLE_ADS_REFRESH_TOKEN=')]
                    open(ENV, 'w').write(''.join(lines) + f'GOOGLE_ADS_REFRESH_TOKEN={rt}\n')
                    msg = 'Hotovo – token uložen, okno můžete zavřít.'; print('✅ refresh token uložen do .env', flush=True)
                else:
                    msg = 'Google nevrátil refresh token.'; print('❌ bez refresh tokenu', flush=True)
            except Exception as e:
                msg = 'Chyba při výměně kódu.'; print('❌', str(e)[:150], flush=True)
        else:
            msg = 'Neplatná odpověď.'; print('❌ neplatný state/kód', q.get('error', ''), flush=True)
        self.send_response(200); self.send_header('Content-Type', 'text/plain; charset=utf-8'); self.end_headers(); self.wfile.write(msg.encode())
        raise SystemExit
try:
    http.server.HTTPServer(('127.0.0.1', PORT), H).handle_request()
except SystemExit:
    pass
