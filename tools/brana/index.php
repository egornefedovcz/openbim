<?php
// Volitelná brána s heslem před vygenerovaným webem (data/web/index.html) pro běžný PHP hosting.
// Nastavení ve složce data/ vedle tohoto souboru (web na ni nesmí – viz .htaccess):
//   data/heslo.txt  – hash sdíleného hesla: php -r 'echo password_hash("HESLO", PASSWORD_DEFAULT);'
//   data/zdroj.txt  – (volitelně) odkud brát index.html: cesta nebo http://… (výchozí ./web/index.html)
// Poslední úspěšně načtená verze se ukládá do data/cache.html (když zdroj neodpoví, ukáže se ta).
declare(strict_types=1);
header('Content-Type: text/html; charset=utf-8');
header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');

$DATA = __DIR__ . '/data';
$BASE = rtrim(dirname($_SERVER['SCRIPT_NAME']), '/') . '/';
$sessDir = $DATA . '/sessions';
if (!is_dir($sessDir)) @mkdir($sessDir, 0700);
if (is_dir($sessDir) && is_writable($sessDir)) session_save_path($sessDir);
ini_set('session.gc_maxlifetime', (string)(30 * 86400));
session_set_cookie_params(['lifetime' => 30 * 86400, 'path' => $BASE, 'secure' => true, 'httponly' => true, 'samesite' => 'Lax']);
session_start();

$hash = is_file("$DATA/heslo.txt") ? trim((string)file_get_contents("$DATA/heslo.txt")) : '';
if ($hash === '') { http_response_code(503); exit('Přehled není nastavený (chybí heslo).'); }
if (isset($_GET['odhlasit'])) { $_SESSION = []; session_destroy(); header("Location: $BASE", true, 303); exit; }
$err = '';
if (empty($_SESSION['seo_ok']) && $_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['heslo'])) {
  usleep(400000);   // zpomalení hádání hesla
  if (password_verify((string)$_POST['heslo'], $hash)) {
    session_regenerate_id(true);
    $_SESSION['seo_ok'] = 1;
    header("Location: $BASE", true, 303); exit;
  }
  $err = 'Nesprávné heslo.';
}
if (empty($_SESSION['seo_ok'])) {
  http_response_code(401); ?>
<!DOCTYPE html><html lang="cs"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light dark"><title>SEO přehled – přihlášení</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root { color-scheme: light dark; --navy:#253848; --navy-700:#1b2a37; --focus:#a9cae9; --ink:#16202a; --muted:#5b6670; --line:#e7eaed; --line-strong:#cfd5db; --surface:#f5f6f7; --card:#fff; --error:#b3261e; }
  @media (prefers-color-scheme: dark) { :root { --navy:#3d5d78; --navy-700:#4a6d8b; --focus:#c3d7e8; --ink:#f3f6f8; --muted:#d3dbe2; --line:#27343f; --line-strong:#3d4c59; --surface:#0f161d; --card:#151f28; --error:#f08a80; } }
  * { box-sizing:border-box; }
  body { margin:0; min-height:100vh; display:grid; place-items:center; padding:16px; background:var(--surface); color:var(--ink); font-family:'Manrope', system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif; }
  form { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:28px 24px; width:min(360px,100%); }
  h1 { font-size:22px; margin:0 0 6px; } p { color:var(--muted); margin:0 0 18px; font-size:14px; line-height:1.5; }
  label { display:block; font-weight:700; font-size:14px; margin:14px 0 6px; }
  input { width:100%; font:inherit; font-size:16px; padding:11px 12px; border:1px solid var(--line-strong); border-radius:8px; background:var(--card); color:var(--ink); }
  :focus-visible { outline:3px solid var(--focus); outline-offset:2px; }
  button { margin-top:18px; width:100%; min-height:48px; border:0; border-radius:8px; background:var(--navy); color:#fff; font:inherit; font-weight:700; font-size:13px; letter-spacing:.12em; text-transform:uppercase; cursor:pointer; }
  button:hover { background:var(--navy-700); }
  .err { color:var(--error); margin:12px 0 0; font-size:14px; }
</style></head>
<body><form method="post"><h1>SEO přehled</h1><p>Interní přehled klíčových slov a pozic pro marketing.</p>
<label for="h">Heslo</label><input id="h" name="heslo" type="password" autocomplete="current-password" required autofocus>
<?= $err ? '<p class="err" role="alert">' . htmlspecialchars($err, ENT_QUOTES, 'UTF-8') . '</p>' : '' ?><button type="submit">Přihlásit</button></form></body></html>
<?php exit; }

$zdroj = is_file("$DATA/zdroj.txt") ? trim((string)file_get_contents("$DATA/zdroj.txt")) : __DIR__ . '/web/index.html';
$ctx = stream_context_create(['http' => ['timeout' => 10]]);
$html = @file_get_contents($zdroj, false, $ctx);
if ($html !== false && strlen($html) > 1000) {
  @file_put_contents("$DATA/cache.html.tmp", $html) && @rename("$DATA/cache.html.tmp", "$DATA/cache.html");
} else {
  $html = is_file("$DATA/cache.html") ? (string)file_get_contents("$DATA/cache.html") : '';
  if ($html === '') { http_response_code(503); exit('Data přehledu jsou teď nedostupná – zkuste to prosím za chvíli.'); }
}
echo $html;
