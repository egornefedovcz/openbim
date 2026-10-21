"""Sklik API (Seznam): hledanost klíčových slov. Token v .env (SKLIK_TOKEN)."""
import json, os, time, urllib.request

API = 'https://api.sklik.cz/drak/json/v5/'


def _token():
    if os.environ.get('SKLIK_TOKEN'):
        return os.environ['SKLIK_TOKEN']
    return [l.split('=', 1)[1].strip() for l in open(os.path.join(os.path.dirname(__file__), '.env')) if l.startswith('SKLIK_TOKEN=')][0]


class Sklik:
    def __init__(self):
        self.session = self._call('client.loginByToken', [_token()])['session']

    def _call(self, method, args):
        for i in range(5):
            req = urllib.request.Request(API + method, data=json.dumps(args).encode(), headers={'Content-Type': 'application/json'})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if r.get('status') == 429:
                time.sleep(10 * (i + 1)); continue
            if r.get('status') not in (200, 206):
                raise RuntimeError(f"{method}: {r.get('status')} {r.get('statusMessage')} {r.get('diagnostics')}")
            if r.get('session'):
                self.session = r['session']
            return r
        raise RuntimeError(f'{method}: 429 opakovaně')

    def stats(self, queries):
        """hledanost pro seznam frází (po 100)"""
        out = []
        for i in range(0, len(queries), 100):
            out += self._call('keywords.suggest.stats', [{'session': self.session}, queries[i:i + 100]])['stats']
            time.sleep(1)
        return out

    def suggest(self, query, limit=200, related=True):
        """návrhy frází podle hledanosti"""
        return self._call('keywords.suggest', [{'session': self.session}, query, {'limit': limit, 'related': related}])['suggestions']


if __name__ == "__main__":
    import sys
    s = Sklik()
    for x in s.stats(sys.argv[1:] or ['malování obrazů', 'zážitkové malování', 'malování s vínem']):
        print(x['query'], x['avgSearchCount'], round((x.get('avgCpc') or 0) / 100, 2), 'Kč', [m['searchCount'] for m in x.get('searchCountInTime', [])])
    for x in s.suggest('malování s vínem', limit=10):
        print('  návrh:', x['query'], x['avgSearchCount'])
