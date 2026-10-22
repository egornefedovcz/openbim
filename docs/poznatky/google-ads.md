# Google Ads API – hledanost na Googlu

*2026-10-22 – ⚠️ čeká na úroveň přístupu*

- REST: `POST https://googleads.googleapis.com/<verze>/customers/<id>:generateKeywordHistoricalMetrics`, hlavičky `Authorization: Bearer <OAuth>`, `developer-token`, volitelně `login-customer-id` (účet správce). Tělo: `keywords` (≤ 1000 na dotaz zde), `geoTargetConstants: ["geoTargetConstants/2203"]` (Česko), `language: "languageConstants/1021"` (čeština), `keywordPlanNetwork: "GOOGLE_SEARCH"`.
- Verze API se rychle mění: v22 už vrací `UNSUPPORTED_VERSION`, aktuální byla v25 → konektor zkouší verze od nejnovější.
- OAuth: klient typu Desktop v Google Cloud + jednorázové přihlášení (`tools/google_ads_login.py`, loopback 127.0.0.1) → refresh token do `.env`. Scope `https://www.googleapis.com/auth/adwords`.
- **Nový developer token má úroveň „Test“** → na skutečném účtu chyba `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION`: „The Google Cloud project is only approved for use with test accounts. To access non-test accounts, apply for Explorer, Basic or Standard access.“ Je potřeba požádat v Google Ads → Nástroje → Centrum API.
