"""Google Ads API – historická hledanost (Keyword Planner). .env: GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CUSTOMER_ID,
GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN, volitelně GOOGLE_ADS_LOGIN_CUSTOMER_ID (účet správce).
Přihlášení: python3 tools/google_ads_login.py"""
import json, os, urllib.error, urllib.parse, urllib.request

VERZE = ('v25', 'v24', 'v23', 'v22', 'v21', 'v20')   # zkouší od nejnovější; nepodporovanou přeskočí
CZ, CESTINA = 'geoTargetConstants/2203', 'languageConstants/1021'


def _token():
    body = urllib.parse.urlencode({'client_id': os.environ['GOOGLE_ADS_CLIENT_ID'], 'client_secret': os.environ['GOOGLE_ADS_CLIENT_SECRET'],
                                   'refresh_token': os.environ['GOOGLE_ADS_REFRESH_TOKEN'], 'grant_type': 'refresh_token'}).encode()
    return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', body, timeout=30))['access_token']


def historie(slova, geo=CZ, jazyk=CESTINA):
    """{slovo: {hledanost, konkurence, cpc_od, cpc_do, mesice:[...]}} – po 1000 slovech"""
    tok, cid = _token(), os.environ['GOOGLE_ADS_CUSTOMER_ID'].replace('-', '')
    hl = {'Authorization': 'Bearer ' + tok, 'developer-token': os.environ['GOOGLE_ADS_DEVELOPER_TOKEN'], 'Content-Type': 'application/json'}
    if os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID'):
        hl['login-customer-id'] = os.environ['GOOGLE_ADS_LOGIN_CUSTOMER_ID'].replace('-', '')
    out = {}
    for i in range(0, len(slova), 1000):
        body = json.dumps({'keywords': slova[i:i + 1000], 'geoTargetConstants': [geo], 'language': jazyk, 'keywordPlanNetwork': 'GOOGLE_SEARCH'}).encode()
        for v in VERZE:
            try:
                r = json.load(urllib.request.urlopen(urllib.request.Request(
                    f'https://googleads.googleapis.com/{v}/customers/{cid}:generateKeywordHistoricalMetrics', body, hl), timeout=120))
                break
            except urllib.error.HTTPError as e:
                txt = e.read().decode('utf-8', 'replace')
                if e.code == 404 or 'UNSUPPORTED_VERSION' in txt:
                    continue          # verze API neexistuje / už není podporovaná → zkus další
                raise RuntimeError(f'Google Ads {v} HTTP {e.code}: {txt[:2500]}') from None
        else:
            raise RuntimeError('žádná verze Google Ads API neodpověděla')
        for x in r.get('results', []):
            m = x.get('keywordMetrics', {})
            out[x['text']] = {'hledanost': int(m.get('avgMonthlySearches', 0) or 0), 'konkurence': m.get('competition'),
                              'cpc_od': int(m.get('lowTopOfPageBidMicros', 0) or 0) / 1e6, 'cpc_do': int(m.get('highTopOfPageBidMicros', 0) or 0) / 1e6,
                              'mesice': [int(z.get('monthlySearches', 0) or 0) for z in m.get('monthlySearchVolumes', [])]}
    return out
