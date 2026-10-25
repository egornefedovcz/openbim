# openbim – otevřený český SEO nástroj (pracovní název)

Cíl: funkce placených SEO nástrojů (sledování klíčových slov, hledanost, mezery v obsahu oproti konkurenci) **zdarma a z oficiálních zdrojů**, s důrazem na český trh (Seznam, Sklik). Nejdřív ho používá ArtMoment, ověřené části postupně zveřejníme jako šablonu, kterou si kdokoli zprovozní sám přes GitHub.

> Stav: **pilot** – běží u ArtMomentu, veřejně od 21. 10. 2026. Co je ověřené a co ne, je v [`docs/poznatky/`](docs/poznatky/).

## Co umí teď
| Funkce | Zdroj | Stav |
|---|---|---|
| Naše pozice, zobrazení a kliky na Googlu | Google Search Console API | ✅ ověřeno |
| Hledanost a sezónnost na Seznamu, CPC, návrhy slov | Sklik API | ✅ ověřeno |
| Obsah konkurence (témata z URL) | sitemapy podle robots.txt | ✅ ověřeno (jen weby, které to povolují) |
| Hledanost na Googlu | Google Ads API (Keyword Planner) | ✅ ověřeno (Basic access) |
| Report: mezery v obsahu, kousek od 1. stránky, špatná stránka | z dat výše | ✅ |
| Export ve formátu Collabimu | CSV | ✅ |
| Denní měření pozic (Google) | Search Console po dnech | ✅ od 22. 10. 2026 |
| Web s přehledem jako Collabim + export CSV/XLSX | statický HTML | ✅ |

## Spuštění
Python 3.11+, žádné další balíčky (JWT pro Search Console podepisuje `openssl`).

```bash
cp seo.example.toml seo.toml          # doména, konkurenti, semena
# .env: SKLIK_TOKEN=…   GSC_SA_JSON=/cesta/ke/klici.json (nebo obsah JSON)
# keywords.csv: sloupec keyword (export z Collabimu jde rovnou)
python3 run.py doctor                  # ověří přístupy
python3 run.py sber                    # stáhne data do data/seo.db
python3 run.py report                  # data/report-RRRR-MM-DD.md
python3 run.py export                  # data/export.csv
python3 run.py denne                   # denně: Search Console po dnech + web
python3 run.py web                     # jen web: data/web/index.html
```

**Další web:** `python3 run.py <příkaz> --config seo.jiny.toml`. V TOML lze nastavit `data_dir` (výchozí `data`) a `env_file` (výchozí `.env`; jeho klíče mají přednost, chybějící se doplní z `.env`). Příklad: `seo.objevcesko.toml` → `data/objevcesko/`, `GSC_SA_JSON` v `.env.objevcesko`.

## Denní měření
`run.py denne` stahuje Search Console po dnech (`date × query × page`) do tabulky `gsc_daily` a součty webu do `gsc_totals`. GSC má zpoždění ~2–3 dny a poslední dny dopočítává, proto se každý den znovu stáhne okno posledních 5 dní a přepíše; první běh doplní 90 dní zpět. Hledanost (Google Ads, Sklik) a konkurence se dál sbírají týdně (`run.py sber`).

**Pozice slova** = vážený průměr pozic podle zobrazení pro přesnou frázi (malá písmena, bez diakritiky). Denní pozice je v grafu detailu slova; seznam, rozložení pozic a teoretická návštěvnost berou 7denní okno, protože většina slov nemá zobrazení každý den. Slovo bez zobrazení pozici nemá. **Pozice na Seznamu neměříme** – search.seznam.cz robotům v robots.txt vyhledávání zakazuje.

## Web (UI)
`run.py web` vyrobí jediný soubor `data/web/index.html` s vloženými daty (JSON) a vanilla JS, grafy přes Chart.js z cdnjs. Bez serveru – jde otevřít lokálně, dát na GitHub Pages nebo za heslo (`tools/brana/index.php` pro PHP hosting).
- **Hlavní přehled**: důležité změny pozic (poslední den, 14 dní), aktuální rozložení pozic (TOP 3 / 4–10 / 11–20 / 21+), rozložení v čase, teoretická návštěvnost, kliky a zobrazení ze Search Console, stránky se zobrazením (náhrada „indexovaných stránek“), poslední změny cílových stránek.
- **Klíčová slova**: hledání, filtr štítku a pozice, řazení; detail slova s grafem pozice v čase.
- **Štítky**: souhrn podle štítků. **Konkurence**: mezery v obsahu.
- **Export**: CSV (UTF-8 s BOM, sloupce jako import Collabimu + pozice) a XLSX, podle aktuálních filtrů; export štítků.
- **Teoretická návštěvnost** = Σ hledanost Google × CTR podle pozice: 1. 28 %, 2. 15,7 %, 3. 11 %, 4. 8 %, 5. 7,2 %, 6. 5,1 %, 7. 4 %, 8. 3,2 %, 9. 2,8 %, 10. 2,5 %, 11.–20. 1 %, horší 0 (zaokrouhlené veřejné studie organického CTR, `czseo/web.py`).
- **Vzhled**: `web_tema = "neutral"` (CSS proměnné, světlý i tmavý režim) nebo vlastní téma doplněním proměnných v `czseo/web.html`.

## Zásady
- Jen oficiální API a to, co weby v robots.txt povolují. Žádné obcházení ochran ani stahování výsledků vyhledávačů, které to zakazují.
- Šetrně: pauzy mezi požadavky, strop počtu URL.
- Klíče nikdy v repozitáři – jen `.env` lokálně nebo GitHub Secrets.

## Plán
Viz [`docs/plan.md`](docs/plan.md).

## Licence
MIT – viz [LICENSE](LICENSE).
