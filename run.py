#!/usr/bin/env python3
"""openbim – český SEO nástroj zdarma (Search Console + Sklik + sitemapy konkurence).

  python3 run.py doctor            ověří nastavení a přístupy ke zdrojům
  python3 run.py sber              stáhne data (Sklik, Search Console, konkurence 1× týdně)
  python3 run.py report            Markdown report do data/report-RRRR-MM-DD.md
  python3 run.py export            CSV ve formátu Collabimu do data/export.csv
"""
import csv, datetime as dt, json, os, sys, tomllib
from collections import defaultdict

from czseo.store import db, norm

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
CFG = tomllib.load(open('seo.toml', 'rb'))
DNES = dt.date.today().isoformat()


def env():
    if os.path.exists('.env'):
        for l in open('.env'):
            if '=' in l and not l.startswith('#'):
                k, v = l.strip().split('=', 1)
                os.environ.setdefault(k, v)


def nacti_slova(c):
    """keywords.csv → tabulka keywords (sloupce keyword|Klíčové slovo, tag|Štítky, target_url|URL cílové stránky)"""
    f = CFG['klicova_slova']
    if not os.path.exists(f):
        return 0
    rows = list(csv.DictReader(open(f, encoding='utf-8-sig')))
    pick = lambda r, *ks: next((r[k] for k in ks if r.get(k)), '')
    for r in rows:
        kw = pick(r, 'keyword', 'Klíčové slovo').strip()
        if kw:
            c.execute('insert or replace into keywords values (?,?,?,?)', (kw, pick(r, 'tag', 'Štítky'), pick(r, 'target_url', 'URL cílové stránky'), 'csv'))
    c.commit()
    return len(rows)


def sber_sklik(c):
    from czseo.sources.sklik import Sklik
    s = Sklik()
    slova = [k for (k,) in c.execute("select keyword from keywords")]
    # návrhy ze semen → nová slova (source=sklik) nad prahem hledanosti
    for sem in CFG.get('semena', []):
        for x in s.suggest(sem, limit=300):
            if x['avgSearchCount'] >= CFG.get('min_hledanost', 5):
                c.execute("insert or ignore into keywords values (?,?,?,?)", (x['query'], 'navrh', '', 'sklik'))
    c.commit()
    slova = [k for (k,) in c.execute("select keyword from keywords")]
    for x in s.stats(slova):
        c.execute('insert or replace into sklik values (?,?,?,?,?)', (DNES, x['query'], x['avgSearchCount'], (x.get('avgCpc') or 0) / 100,
                                                                     json.dumps([m['searchCount'] for m in x.get('searchCountInTime', [])])))
    c.commit()
    return len(slova)


def sber_gsc(c):
    from czseo.sources import gsc
    end = dt.date.today() - dt.timedelta(days=3)          # GSC má zpoždění ~2–3 dny
    start = end - dt.timedelta(days=27)
    rows = gsc.query(CFG['gsc_vlastnost'], start.isoformat(), end.isoformat(), country=CFG.get('gsc_zeme') or None)
    c.execute('delete from gsc where date_from=? and date_to=?', (start.isoformat(), end.isoformat()))
    c.executemany('insert into gsc values (?,?,?,?,?,?,?)', [(start.isoformat(), end.isoformat(), r['query'], r['page'], r['clicks'], r['impressions'], r['position']) for r in rows])
    c.commit()
    return len(rows)


def sber_konkurence(c, vynutit=False):
    from czseo.sources import sitemaps
    posl = c.execute('select max(date) from competitor_urls').fetchone()[0]
    if posl and not vynutit and (dt.date.today() - dt.date.fromisoformat(posl)).days < 7:
        return 'přeskočeno (poslední sběr %s)' % posl
    n = 0
    for d in CFG.get('konkurenti', []):
        try:
            u = sitemaps.urls(d, CFG.get('max_url_konkurenta', 20000))
        except RuntimeError as e:
            print(f'  ⚠️ {e}'); continue
        c.execute('delete from competitor_urls where domain=?', (d,))
        c.executemany('insert into competitor_urls values (?,?,?)', [(DNES, d, x) for x in u])
        c.commit(); n += len(u)
        print(f'  {d}: {len(u)} URL')
    return n


def tabulka(c):
    """jedna řádka na slovo: hledanost Seznam, pozice/URL Google (GSC 28 dní), pokrytí konkurencí"""
    gsc_from = c.execute('select max(date_from) from gsc').fetchone()[0]
    g = defaultdict(list)
    for q, page, cl, im, pos in c.execute('select query, page, clicks, impressions, position from gsc where date_from=?', (gsc_from,)):
        g[norm(q)].append((page, cl, im, pos))
    sk_date = c.execute('select max(date) from sklik').fetchone()[0]
    sk = {norm(k): (a, cpc, m) for k, a, cpc, m in c.execute('select keyword, avg_search, cpc, months from sklik where date=?', (sk_date,))}
    from czseo.sources.sitemaps import slova
    konk = defaultdict(set)
    for d, u in c.execute('select domain, url from competitor_urls'):
        for w in set(slova(u)):
            konk[w].add((d, u))
    out, videno = [], set()
    # varianty bez diakritiky / s velkými písmeny = jedna fráze; přednost má slovo z CSV a tvar s diakritikou
    rows_kw = sorted(c.execute('select keyword, tag, target_url, source from keywords'), key=lambda r: (r[3] != 'csv', -sum(ord(ch) > 127 for ch in r[0]), r[0] != r[0].lower()))
    for kw, tag, target, src in rows_kw:
        n = norm(kw)
        if n in videno:
            continue
        videno.add(n)
        rows = g.get(n, [])
        im = sum(r[2] for r in rows)
        top = max(rows, key=lambda r: r[2]) if rows else None
        pos = sum(r[3] * r[2] for r in rows) / im if im else None
        a, cpc, months = sk.get(n, (None, None, '[]'))
        tok = [w for w in n.split() if len(w) > 2]
        kryje = set.intersection(*[{d for d, _ in konk.get(w, set())} for w in tok]) if tok else set()
        out.append(dict(keyword=kw, tag=tag, source=src, target_url=target, seznam_hledanost=a, cpc=cpc, sezonnost=json.loads(months or '[]'),
                        google_pozice=round(pos, 1) if pos else None, google_url=top[0] if top else '', zobrazeni=im, kliky=sum(r[1] for r in rows),
                        konkurence=sorted(kryje)))
    return out, gsc_from, sk_date


def report(c):
    t, gsc_from, sk_date = tabulka(c)
    L = [f'# SEO report {DNES} – {CFG["domena"]}', '', f'Zdroje: Search Console 28 dní od {gsc_from}, Sklik (Seznam) {sk_date}, sitemapy konkurence.', '']
    # 1) mezery: hledané na Seznamu, konkurence má stránku, my se v Google nezobrazujeme
    gap = sorted([r for r in t if (r['seznam_hledanost'] or 0) >= CFG.get('min_hledanost', 5) and not r['zobrazeni'] and r['konkurence']],
                 key=lambda r: -(r['seznam_hledanost'] or 0))[:40]
    L += ['## Mezery v obsahu', 'Fráze, které lidé hledají, konkurence na ně má stránku a my se v Googlu nezobrazujeme.', '',
          '| Fráze | Seznam/měs. | Konkurence |', '|---|---:|---|'] + [f"| {r['keyword']} | {r['seznam_hledanost']} | {', '.join(d.replace('www.', '') for d in r['konkurence'])} |" for r in gap]
    # 2) blízko první stránky: pozice 8–20 s nejvíc zobrazeními
    near = sorted([r for r in t if r['google_pozice'] and 8 <= r['google_pozice'] <= 20], key=lambda r: -r['zobrazeni'])[:25]
    L += ['', '## Kousek od první stránky (Google pozice 8–20)', '', '| Fráze | Pozice | Zobrazení | Stránka |', '|---|---:|---:|---|'] + \
         [f"| {r['keyword']} | {r['google_pozice']} | {r['zobrazeni']} | {r['google_url'].split('.cz', 1)[-1]} |" for r in near]
    # 3) špatná stránka: Google zobrazuje jinou URL než cílovou
    bad = [r for r in t if r['target_url'] and r['google_url'] and r['target_url'].rstrip('/') != r['google_url'].rstrip('/')]
    bad = sorted(bad, key=lambda r: -r['zobrazeni'])[:25]
    L += ['', '## Google ukazuje jinou stránku než cílovou', '', '| Fráze | Cílová | Zobrazuje se |', '|---|---|---|'] + \
         [f"| {r['keyword']} | {r['target_url'].split('.cz', 1)[-1]} | {r['google_url'].split('.cz', 1)[-1]} |" for r in bad]
    # 4) sezónnost: slova, kterým za 1–2 měsíce roste hledanost
    L += ['', f'Sledovaných slov {len(t)}, se zobrazením v Googlu {sum(1 for r in t if r["zobrazeni"])}, s hledaností na Seznamu {sum(1 for r in t if r["seznam_hledanost"])}.']
    f = f'data/report-{DNES}.md'
    open(f, 'w').write('\n'.join(L) + '\n')
    return f


def export(c):
    t, _, _ = tabulka(c)
    f = 'data/export.csv'
    with open(f, 'w', newline='', encoding='utf-8') as o:
        w = csv.writer(o)
        w.writerow(['Klíčové slovo', 'Štítky', 'Hledanost Seznam', 'CPC Kč', 'Pozice Google', 'URL Google', 'Zobrazení 28 d', 'Kliky 28 d', 'URL cílové stránky', 'Konkurence'])
        for r in sorted(t, key=lambda r: -(r['seznam_hledanost'] or 0)):
            w.writerow([r['keyword'], r['tag'], r['seznam_hledanost'] or '', r['cpc'] or '', r['google_pozice'] or '', r['google_url'], r['zobrazeni'], r['kliky'], r['target_url'], ' '.join(r['konkurence'])])
    return f


def doctor():
    ok = True
    for nazev, fn in [('Sklik', lambda: __import__('czseo.sources.sklik', fromlist=['Sklik']).Sklik()),
                      ('Search Console', lambda: __import__('czseo.sources.gsc', fromlist=['query']).query(CFG['gsc_vlastnost'], (dt.date.today() - dt.timedelta(days=5)).isoformat(), (dt.date.today() - dt.timedelta(days=4)).isoformat(), ('query',)))]:
        try:
            fn(); print(f'✅ {nazev}')
        except Exception as e:
            ok = False; print(f'❌ {nazev}: {str(e)[:200]}')
    print(('✅' if os.path.exists(CFG['klicova_slova']) else '⚠️') + f" seznam slov {CFG['klicova_slova']}")
    return ok


if __name__ == '__main__':
    env()
    cmd = (sys.argv[1:] or ['help'])[0]
    c = db()
    if cmd == 'doctor':
        sys.exit(0 if doctor() else 1)
    elif cmd == 'sber':
        print('slova z CSV:', nacti_slova(c))
        for nazev, fn in [('Sklik', sber_sklik), ('Search Console', sber_gsc), ('Konkurence', lambda c: sber_konkurence(c, '--konkurence' in sys.argv))]:
            try:
                print(f'{nazev}:', fn(c))
            except Exception as e:
                print(f'❌ {nazev}: {str(e)[:300]}')
    elif cmd == 'report':
        print(report(c))
    elif cmd == 'export':
        print(export(c))
    else:
        print(__doc__)
