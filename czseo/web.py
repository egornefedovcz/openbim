"""Statický web s přehledem (jako hlavní přehled Collabimu): data/web/index.html s vloženými daty (JSON) a vanilla JS.

Žádný server – soubor jde otevřít lokálně, nahrát na GitHub Pages nebo schovat za heslo.

Pozice slova = vážený průměr pozic ze Search Console podle zobrazení pro přesnou (normalizovanou) frázi.
- denní pozice: za jeden den (graf v detailu slova, „Důležité změny pozic“ za den),
- aktuální pozice: za posledních 7 dní (klouzavě) – Search Console má u většiny slov zobrazení jen některé dny,
  sedmidenní okno dává stabilní číslo pro seznam slov, rozložení pozic a teoretickou návštěvnost.
"""
import datetime as dt, json, os
from html import escape as html_esc
from collections import defaultdict

from czseo.store import norm

# Odhad podílu prokliků (CTR) podle pozice na Googlu – zaokrouhlené veřejné studie organického CTR
# (Advanced Web Ranking / Backlinko 2023–2025, desktop+mobil). Pozice 11–20 ≈ 1 %, 21+ ≈ 0.
CTR = {1: .28, 2: .157, 3: .11, 4: .08, 5: .072, 6: .051, 7: .04, 8: .032, 9: .028, 10: .025}
OKNO = 7


def ctr(pos):
    if pos is None:
        return 0
    p = max(1, round(pos))
    return CTR.get(p, .01 if p <= 20 else 0)


def _kos(pos):
    return 0 if pos <= 3.5 else 1 if pos <= 10.5 else 2 if pos <= 20.5 else 3


def generuj(c, cfg, tabulka, out='data/web'):
    t, _, _ = tabulka(c)
    dny = [d for (d,) in c.execute('select distinct date from gsc_daily order by date')]
    if not dny:
        raise RuntimeError('chybí denní data Search Console – spusťte nejdřív `python3 run.py denne`')
    ix = {d: i for i, d in enumerate(dny)}
    N = len(dny)
    sledovana = {norm(r['keyword']): r for r in t}

    # denní agregace pro sledovaná slova: [zobrazení, kliky, Σ pozice×zobrazení, {stránka: zobrazení}]
    den = defaultdict(lambda: defaultdict(lambda: [0, 0, 0.0, defaultdict(int)]))
    stranky = defaultdict(set)
    for d, q, page, cl, im, pos in c.execute('select date, query, page, clicks, impressions, position from gsc_daily'):
        if im:
            stranky[d].add(page)
        n = norm(q)
        if n not in sledovana or not im:
            continue
        a = den[n][ix[d]]
        a[0] += im; a[1] += cl; a[2] += pos * im; a[3][page] += im

    kw, rozl, navst, cil_zmeny, poc = [], [[0, 0, 0, 0] for _ in range(N)], [0.0] * N, [], [0] * N
    for n, r in sledovana.items():
        dd = den.get(n, {})
        denni = [[i, round(a[2] / a[0], 1), a[0], a[1]] for i, a in sorted(dd.items())]
        # klouzavé 7denní okno: pozice a převažující stránka
        r7, top7 = [None] * N, [None] * N
        for i in range(N):
            im = s = 0; pg = defaultdict(int)
            for j in range(max(0, i - OKNO + 1), i + 1):
                a = dd.get(j)
                if a:
                    im += a[0]; s += a[2]
                    for p, v in a[3].items():
                        pg[p] += v
            if im:
                r7[i] = s / im; top7[i] = max(pg, key=pg.get)
        for i in range(OKNO - 1, N):
            if r7[i] is not None:
                rozl[i][_kos(r7[i])] += 1; poc[i] += 1
                navst[i] += (r['google_hledanost'] or 0) * ctr(r7[i])
        # změna cílové stránky: převažující stránka (7 dní) se změnila a nová vydržela aspoň 2 dny
        for i in range(OKNO, N):
            if top7[i] and top7[i - 1] and top7[i] != top7[i - 1] and i + 1 < N and top7[i + 1] == top7[i]:
                cil_zmeny.append([i, r['keyword'], top7[i - 1], top7[i]])
        L = N - 1
        im28 = sum(a[0] for i, a in dd.items() if i > L - 28)
        cl28 = sum(a[1] for i, a in dd.items() if i > L - 28)
        pg28 = defaultdict(int)
        for i, a in dd.items():
            if i > L - 28:
                for p, v in a[3].items():
                    pg28[p] += v
        kw.append(dict(k=r['keyword'], t=r['tag'] or '', src=r['source'], u=r['target_url'] or '',
                       g=r['google_hledanost'], kg=r['konkurence_google'] or '', s=r['seznam_hledanost'], cpc=r['cpc'],
                       p=round(r7[L], 1) if r7[L] is not None else None,
                       p7=round(r7[L - 7], 1) if N > 7 and r7[L - 7] is not None else None,
                       p14=round(r7[L - 14], 1) if N > 14 and r7[L - 14] is not None else None,
                       url=top7[L] or '', im=im28, cl=cl28, ko=r['konkurence'], d=denni,
                       pg=sorted(pg28.items(), key=lambda x: -x[1])[:5]))

    tot = {d: (cl, im) for d, cl, im in c.execute('select date, clicks, impressions from gsc_totals')}
    D = dict(
        domena=cfg.get('domena', ''), tema=cfg.get('web_tema', 'neutral'),
        generovano=dt.datetime.now().strftime('%Y-%m-%d %H:%M'), dny=dny, okno=OKNO,
        min_hledanost=cfg.get('min_hledanost', 5), konkurenti=cfg.get('konkurenti', []),
        konk_url={d: n for d, n in c.execute('select domain, count(*) from competitor_urls group by 1')},
        ctr=CTR, kw=kw, rozl=rozl, pocet=poc, navst=[round(x) for x in navst],
        gsc=[[tot.get(d, (None, None))[0], tot.get(d, (None, None))[1]] for d in dny],
        stranky=[len(stranky[d]) for d in dny],
        cil=sorted(cil_zmeny, key=lambda x: -x[0])[:60],
    )
    os.makedirs(out, exist_ok=True)
    tpl = open(os.path.join(os.path.dirname(__file__), 'web.html'), encoding='utf-8').read()
    data = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    font = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">') if D['tema'] == 'artmoment' else ''
    html = (tpl.replace('<!--FONT-->', font).replace('{{DOMENA}}', html_esc(D['domena'])).replace('{{TEMA}}', html_esc(D['tema']))
            .replace('/*DATA*/null', data))
    f = os.path.join(out, 'index.html')
    open(f, 'w', encoding='utf-8').write(html)
    return f'{f} ({len(html) // 1024} kB, {len(kw)} slov, {N} dní)'
