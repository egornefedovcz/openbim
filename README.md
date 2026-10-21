# openbim – otevřený český SEO nástroj (pracovní název)

Cíl: funkce placených SEO nástrojů (sledování klíčových slov, hledanost, mezery v obsahu oproti konkurenci) **zdarma a z oficiálních zdrojů**, s důrazem na český trh (Seznam, Sklik). Nejdřív ho používá ArtMoment, ověřené části postupně zveřejníme jako šablonu, kterou si kdokoli zprovozní sám přes GitHub.

> Stav: **interní pilot** (repozitář je soukromý). Co je ověřené a co ne, je v [`docs/poznatky/`](docs/poznatky/).

## Co umí teď
| Funkce | Zdroj | Stav |
|---|---|---|
| Naše pozice, zobrazení a kliky na Googlu | Google Search Console API | ✅ ověřeno |
| Hledanost a sezónnost na Seznamu, CPC, návrhy slov | Sklik API | ✅ ověřeno |
| Obsah konkurence (témata z URL) | sitemapy podle robots.txt | ✅ ověřeno (jen weby, které to povolují) |
| Hledanost na Googlu | Google Ads API (Keyword Planner) | ⏳ čeká na vývojářský přístup |
| Report: mezery v obsahu, kousek od 1. stránky, špatná stránka | z dat výše | ✅ |
| Export ve formátu Collabimu | CSV | ✅ |

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
```

## Zásady
- Jen oficiální API a to, co weby v robots.txt povolují. Žádné obcházení ochran ani stahování výsledků vyhledávačů, které to zakazují.
- Šetrně: pauzy mezi požadavky, strop počtu URL.
- Klíče nikdy v repozitáři – jen `.env` lokálně nebo GitHub Secrets.

## Plán
Viz [`docs/plan.md`](docs/plan.md).

## Licence
MIT – viz [LICENSE](LICENSE).
