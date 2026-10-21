# Google Search Console API bez knihoven

*Ověřeno 2026-10-21*

- Servisní účet (Google Cloud → IAM → Servisní účty → JSON klíč), jeho e-mail přidat v Search Console jako uživatele (stačí „Omezený“).
- Token: JWT RS256 `{iss: client_email, scope: webmasters.readonly, aud: oauth2.googleapis.com/token}` podepsaný `openssl dgst -sha256 -sign` → `POST oauth2.googleapis.com/token` (grant `jwt-bearer`). Žádný `google-auth` není potřeba.
- `POST /webmasters/v3/sites/{site}/searchAnalytics/query`, `rowLimit` 25 000 + `startRow` stránkování, filtr země `country = cze`.
- Data mají zpoždění ~2–3 dny; bereme 28 dní končících před 3 dny.
- Výsledek pilotu: 6 084 dotazů (1.–14. 10. 2026, Česko), 15 668 řádků dotaz×stránka za 28 dní.

## Pozor
- Hodnota klíče se nesmí objevit v chybových hláškách ani logu (incident 21. 10. – klíč se vypsal, rotace).
- Proměnná `GSC_SA_JSON` může být cesta k souboru nebo přímo obsah JSON (i v uvozovkách z `.env`).
