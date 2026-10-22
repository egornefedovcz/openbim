# Poznatky – co je ověřené

Každý poznatek: datum, co jsme zkusili, výsledek, zdroj. Stav: ✅ ověřeno / ❌ nejde / ⚠️ částečně / ❓ neověřeno.

| Datum | Téma | Stav | Shrnutí | Detail |
|---|---|---|---|---|
| 2026-10-21 | Jak fungují placené nástroje | ✅ | Data jsou veřejná; platí se za infrastrukturu (proxy, prohlížeče, parsery) a databázi frází. Hledanost mají z reklamních API. | [jak-funguji-nastroje.md](jak-funguji-nastroje.md) |
| 2026-10-21 | Sklik API – hledanost | ✅ | `keywords.suggest` + `keywords.suggest.stats` fungují s tokenem; jen Seznam, čísla ~100× menší než Google. | [sklik.md](sklik.md) |
| 2026-10-21 | Search Console API bez knihoven | ✅ | JWT servisního účtu podepsaný `openssl`; 6 084 dotazů za 14 dní. | [search-console.md](search-console.md) |
| 2026-10-21 | Pozice na Seznamu | ❌ | `search.seznam.cz/robots.txt` zakazuje robotům výsledky vyhledávání. | [seznam.md](seznam.md) |
| 2026-10-21 | Google Custom Search API | ❌ | Uzavřené pro nové zákazníky, konec 1. 1. 2027. | [google-serp.md](google-serp.md) |
| 2026-10-21 | Sitemapy konkurence | ⚠️ | Allegria 1 975 URL, Zážitky.cz 958 ✅; Kudy z nudy 429, Slevomat 403 ❌. | [konkurence.md](konkurence.md) |
| 2026-10-21 | Rychlost dotazů na Shoptet | ❌ | Paralelní kontrola (~1 600 požadavků) → WAF zablokoval IP na ~4 h. | [konkurence.md](konkurence.md#limity) |
| 2026-10-22 | Google Ads API – Keyword Planner | ⚠️ | Explorer nestačí, Keyword Planner vyžaduje Basic access (projekt v Google Cloud). | [google-ads.md](google-ads.md) |
