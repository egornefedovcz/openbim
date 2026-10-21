# Sklik API (Seznam) – hledanost

*Ověřeno 2026-10-21*

- Endpoint JSON: `https://api.sklik.cz/drak/json/v5/<metoda>`, tělo = JSON pole argumentů.
- Přihlášení: `client.loginByToken` s API tokenem (Sklik → Nastavení → API) → `session`; každá odpověď vrací obnovenou session.
- `keywords.suggest` – `[{session}, "fráze", {limit ≤ 10000, related, orderBy: avgSearchCount|cpc|score|keyword}]` → `suggestions[]{query, avgSearchCount, cpc (haléře), searchCountInTime[12]}`.
- `keywords.suggest.stats` – `[{session}, [≤ 100 frází], {granularity: monthly|daily}]` → `stats[]{query, avgSearchCount, avgCpc, searchCountInTime}`.
- 429 = moc požadavků → čekat (my: 10 s × pokus, mezi dávkami 1 s).
- `avgSearchCount` = průměr posledních 2 měsíců; `searchCountInTime` = 12 měsíců.

## Srovnání s Collabimem (Google)
| Fráze | Collabim | Sklik |
|---|---:|---:|
| jak namalovat kocku | 1 000 | 4 |
| jak namalovat psa | 720 | 9 |
| jak namalovat koně | 390 | 6 |

→ Sklik = jen Seznam, nenahrazuje hledanost z Googlu. Užitečný pro sezónnost (např. „dárek pro maminku“ květen 244 vs. průměr 24), CPC a návrhy frází.

Dokumentace: https://api.sklik.cz/drak/
