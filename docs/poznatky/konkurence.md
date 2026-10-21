# Obsah konkurence ze sitemap

*Ověřeno 2026-10-21*

Postup: `robots.txt` (stažený **vlastním User-Agentem** – `urllib.robotparser.read()` posílá „Python-urllib“, který weby blokují a parser pak zakáže vše) → `Sitemap:` → index → URL, pauza 2 s, strop 20 000 URL. Témata = slova ze slugu URL.

| Web | Výsledek |
|---|---|
| allegria.cz | ✅ 1 975 URL |
| zazitky.cz | ✅ 958 URL |
| kudyznudy.cz | ❌ robots.txt 429 |
| slevomat.cz | ❌ robots.txt 403 |

Párování: fráze (bez diakritiky, slova > 2 znaky) je „pokrytá“ konkurentem, když všechna její slova jsou ve slugu některé jeho URL. Hrubé, ale funguje (např. „dárky pro muže“ → obě domény).

## Limity
Shoptet (a podobné WAF) blokují IP při rychlé sérii požadavků: 21. 10. 2026 kontrola ~1 100 odkazů (8 vláken) + 523 obrázků (12 vláken) → blok celé IP na ~4 h (web, CDN, administrace). Hromadné kontroly jen sériově s pauzou.
