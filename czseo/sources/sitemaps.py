"""Obsah konkurence ze sitemap: URL + slova ze slugu. Šetrně – respektuje robots.txt, 1 požadavek / PAUZA s, strop URL."""
import gzip, re, time, urllib.error, urllib.parse, urllib.request, urllib.robotparser

UA = 'openbim/0.1 (+https://github.com/egornefedovcz/openbim)'
PAUZA = 2.0


def _get(url):
    time.sleep(PAUZA)
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
        b = r.read()
    return (gzip.decompress(b) if url.endswith('.gz') or b[:2] == b'\x1f\x8b' else b).decode('utf-8', 'replace')


def urls(domain, limit=20000):
    """všechny URL ze sitemap domény (přes robots.txt), max `limit`"""
    base = 'https://' + domain
    rp = urllib.robotparser.RobotFileParser(base + '/robots.txt')
    try:   # vlastní stažení s naším User-Agentem (rp.read() posílá Python-urllib, který weby často blokují)
        rp.parse(_get(base + '/robots.txt').splitlines())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429) or e.code >= 500:
            raise RuntimeError(f'{domain}: robots.txt vrací {e.code} – web automatický přístup nepovoluje, přeskakuji') from None
        rp.parse([])   # 404 = bez omezení
    except Exception as e:
        raise RuntimeError(f'{domain}: robots.txt nedostupný ({e})') from None
    queue = list(rp.site_maps() or []) or [base + '/sitemap.xml']
    seen, out = set(), []
    while queue and len(out) < limit:
        sm = queue.pop(0)
        if sm in seen or not rp.can_fetch(UA, sm):
            continue
        seen.add(sm)
        try:
            xml = _get(sm)
        except Exception:
            continue
        locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', xml)
        if '<sitemapindex' in xml:
            queue += locs
        else:
            out += [u for u in locs if rp.can_fetch(UA, u)][: limit - len(out)]
    return out


def slova(url):
    """slova ze slugu URL (bez diakritiky, malá písmena)"""
    p = urllib.parse.unquote(urllib.parse.urlsplit(url).path).lower()
    return [w for w in re.split(r'[^a-z0-9]+', p) if len(w) > 2 and not w.isdigit()]
