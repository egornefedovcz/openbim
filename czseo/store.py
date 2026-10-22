"""Úložiště: jeden SQLite soubor (data/seo.db). Na GitHubu se ukládá do větve `data`."""
import os, sqlite3, unicodedata

SCHEMA = '''
create table if not exists keywords (keyword text primary key, tag text, target_url text, source text);
create table if not exists sklik (date text, keyword text, avg_search int, cpc real, months text, primary key (date, keyword));
create table if not exists gsc (date_from text, date_to text, query text, page text, clicks int, impressions int, position real);
create table if not exists google_ads (date text, keyword text, avg_search int, competition text, cpc_low real, cpc_high real, months text, primary key (date, keyword));
create table if not exists competitor_urls (date text, domain text, url text);
'''


def db(path='data/seo.db'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = sqlite3.connect(path)
    c.executescript(SCHEMA)
    return c


def norm(s):
    """malá písmena bez diakritiky a nadbytečných mezer – klíč pro párování frází"""
    s = unicodedata.normalize('NFKD', (s or '').lower())
    return ' '.join(''.join(ch for ch in s if not unicodedata.combining(ch)).split())
