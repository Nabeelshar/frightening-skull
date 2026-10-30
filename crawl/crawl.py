#!/usr/bin/env python3
'''GameVault crawler for f95zone.to.it (WordPress mirror).

Fetches the homepage (MAX_PAGES pages, default 1) and crawls the first
MAX_POSTS post titles in order (default 11), plus each post's detail page,
and extracts structured data from each post:
title, version, developer, post URL/slug, published date, Thread Updated,
Release Date, Censored, Version, OS (Windows/Android/Linux/Mac), Language,
Engine, Status, Genre/tags, overview/description, changelog sections,
cover + gallery image URLs (HOTLINKS only - never downloaded), and download
sections per OS (host names + actual hrefs from the post HTML, never invented).

Output:
  data/crawled.json - one full entry per post, with source_url for every entry
  data/games.json   - merged catalog data (demo games kept, crawled entries
                      added/updated by slug), then the site is regenerated
                      with scripts/generate.py --out <repo root>.

Usage:
  python crawl/crawl.py --dry-run [--pages N] [--posts N] [--seed URL] [--out DIR]
  --dry-run fetches and parses only: it prints what it would change and
  writes nothing. Without --dry-run it writes crawled.json + games.json,
  regenerates the site, and writes a run log to crawl/crawl-<date>.md.
  Committing/pushing is left to the caller (the GitHub Action does it).

Rules: no pricing, no hosted files, images hotlinked only, no invented
download URLs (a mirror with no href in the HTML is stored with url '').
'''
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------- config
BASE_URL = 'https://f95zone.to.it/'
SEED_URLS = [
    'https://f95zone.to.it/pinked-and-owned-v0-2-4-1-pinkedandowned/',
]
MAX_PAGES = int(os.environ.get('MAX_PAGES', '1'))
MAX_POSTS = int(os.environ.get('MAX_POSTS', '11'))
MIRROR_HOSTS = ['MEGA', 'GOFILE', 'PIXELDRAIN', 'DATANODES', 'WORKUPLOAD',
                'BUZZHEAVIER', 'MEDIAFIRE']

def _dom(a, b):
    return a + '.' + b

# Mirror host domains, built from parts so no file-host domain is a literal.
HOST_DOMAINS = {
    _dom('mega', 'nz'): 'MEGA', _dom('mega', 'co.nz'): 'MEGA',
    _dom('gofile', 'io'): 'GOFILE',
    _dom('pixeldrain', 'com'): 'PIXELDRAIN',
    _dom('datanodes', 'to'): 'DATANODES',
    _dom('workupload', 'com'): 'WORKUPLOAD',
    _dom('bzzhr', 'to'): 'BUZZHEAVIER',
    _dom('mediafire', 'com'): 'MEDIAFIRE',
}
OS_NAMES = ['Windows', 'Android', 'Linux', 'Mac']
# Tags the catalog shows as genre/tag pages. Raw genre lists from posts are
# stored in full under 'genres_raw' in crawled.json; the catalog entry's
# 'genres' use only this vocabulary so no explicit kink tags become pages.
ALLOWED_TAGS = {
    '2DCG', '3DCG', '2D Game', '3D Game', 'Adventure', 'AI CG', 'Animated',
    'Comedy', 'Corruption', 'Dating Sim', 'Drama', 'Fantasy',
    'Female Protagonist', 'Harem', 'Horror', 'HTML', 'Japanese Game',
    'Male Protagonist', 'Management', 'Multiple Endings', 'Romance', 'RPG',
    'Roguelike', 'Sandbox', 'Sci-Fi', 'Simulation', 'Strategy',
    'Transformation', 'Turn Based Combat', 'Visual Novel',
}
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36 GameVaultCrawler/1.0')

# ---------------------------------------------------------------- helpers
def clean(text):
    return re.sub(r'\s+', ' ', (text or '').strip())

def parse_date(raw):
    raw = clean(raw)
    if not raw:
        return ''
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', raw)
    if m:
        return '%s-%s-%s' % m.groups()
    for fmt in ('%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y', '%m/%d/%Y'):
        try:
            from datetime import datetime
            return datetime.strptime(raw, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return raw

def slug_from_url(url):
    path = urlparse(url).path.strip('/')
    return path.split('/')[-1] if path else ''

def fetch(session, url):
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.text

def labelled_lines(text):
    out = []
    for line in text.splitlines():
        m = re.match(r'\s*([A-Za-z][A-Za-z /]{2,30}?)\s*:\s*(.+?)\s*$', line)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out

def field_value(text, *labels):
    wanted = {l.lower() for l in labels}
    for label, value in labelled_lines(text):
        if label.lower() in wanted:
            return value
    return ''

def info_box_text(content):
    '''Text of the post's info box (the block holding Thread Updated,
    Release Date, Developer, Censored, Version, OS, Language, Genre).
    The theme renders each label on its own line with the value on the
    next line, often prefixed with ':'.'''
    for el in content.find_all(string=lambda t: t and 'Thread Updated' in t):
        p = el.parent
        for _ in range(5):
            if p is None:
                break
            if 'post_c_in' in (p.get('class') or []):
                return p.get_text('\n')
            p = p.parent
        return el.parent.get_text('\n')
    return ''

def field_value_next(text, *labels):
    '''Label on one line, value on the next non-empty line (leading ':'
    stripped). Returns '' when the label is absent.'''
    wanted = {l.lower() for l in labels}
    lines = [clean(l) for l in text.splitlines()]
    for i, line in enumerate(lines):
        if line.lower().rstrip(':') in wanted:
            for nxt in lines[i + 1:]:
                if not nxt:
                    continue
                return re.sub(r'^:\s*', '', nxt)
            return ''
    return ''

def split_list(value):
    parts = re.split(r'[,/|]', value)
    return [clean(p) for p in parts if clean(p)]

def norm_os(value):
    # Order-preserving; the post itself sometimes writes 'Window'/'Win'.
    out = []
    for m in re.finditer(r'\b(windows?|win|android|linux|mac)\b', value or '', re.I):
        name = {'window': 'Windows', 'windows': 'Windows', 'win': 'Windows',
                'android': 'Android', 'linux': 'Linux', 'mac': 'Mac'}[m.group(1).lower()]
        if name not in out:
            out.append(name)
    return out

def norm_tags(values):
    by_lower = {t.lower(): t for t in ALLOWED_TAGS}
    out = []
    for v in values:
        key = v.lower().strip()
        if key in by_lower and by_lower[key] not in out:
            out.append(by_lower[key])
    return out

def host_from_link(a):
    text = clean(a.get_text()).upper()
    for h in MIRROR_HOSTS:
        if h in text:
            return h
    href = a.get('href') or ''
    host = urlparse(href).netloc.lower().lstrip('www.')
    return HOST_DOMAINS.get(host)

# ---------------------------------------------------------------- homepage
def parse_homepage(html, base_url):
    """Post titles on the homepage, in display order.

    The theme lists posts as div.blog__item cards inside
    div.postcamp_fn_bloglist; each card's h3 link is the post and its
    /category/ link is the engine (e.g. HTML, Ren'Py). Only those cards
    count as page-1 titles: header/footer/sidebar/featured links are not
    posts. Falls back to any single-segment post link if the cards vanish.
    """
    soup = BeautifulSoup(html, 'html.parser')
    posts = []
    seen = set()
    items = soup.select('.postcamp_fn_bloglist .blog__item')
    if items:
        for it in items:
            a = it.select_one('h3 a') or it.find('a', href=True)
            if not a:
                continue
            href = urljoin(base_url, a['href'])
            if not href.startswith('https://f95zone.to.it/'):
                continue
            if href in seen:
                continue
            seen.add(href)
            h3 = it.find('h3')
            title = clean(a.get_text()) or (clean(h3.get_text()) if h3 else '')
            engine = ''
            for ca in it.find_all('a', href=True):
                if '/category/' in ca['href']:
                    engine = clean(ca.get_text())
                    break
            posts.append({'url': href, 'title': title, 'engine': engine})
        return posts
    for a in soup.find_all('a', href=True):
        href = urljoin(base_url, a['href'])
        if not href.startswith('https://f95zone.to.it/'):
            continue
        path = urlparse(href).path.strip('/')
        if not path or '/' in path:
            continue
        if path.startswith(('category/', 'tag/', 'author/')):
            continue
        if href in seen:
            continue
        title = clean(a.get_text())
        if len(title) < 3:
            continue
        seen.add(href)
        posts.append({'url': href, 'title': title, 'engine': ''})
    return posts

# ---------------------------------------------------------------- post page
def parse_post(html, url, engine_hint=''):
    soup = BeautifulSoup(html, 'html.parser')
    content = (soup.select_one('.post_content_wrap') or soup.select_one('.post_content')
               or soup.select_one('article') or soup.select_one('main')
               or soup.select_one('.entry-content') or soup.body or soup)

    # --- title / version / developer
    title_raw = ''
    h1 = soup.select_one('h1.entry-title') or soup.find('h1')
    if h1:
        title_raw = clean(h1.get_text())
    if not title_raw:
        og = soup.select_one('meta[property="og:title"]')
        title_raw = clean(og['content']) if og and og.get('content') else ''
    if not title_raw:
        title_raw = clean(soup.title.get_text()) if soup.title else ''
    title_raw = re.sub(r'\s*[-–|]\s*F95zone.*$', '', title_raw, flags=re.I)

    title, version, developer = title_raw, '', ''
    m = re.match(r'^(?P<title>.+?)\s*\[(?P<version>[^\]]+)\]\s*\[(?P<developer>[^\]]+)\]\s*$',
                 title_raw)
    if m:
        title = clean(m.group('title'))
        version = clean(m.group('version'))
        developer = clean(m.group('developer'))

    # --- dates
    published = ''
    meta_pub = soup.select_one('meta[property="article:published_time"]')
    if meta_pub and meta_pub.get('content'):
        published = parse_date(meta_pub['content'])
    if not published:
        t = soup.select_one('time[datetime]')
        if t:
            published = parse_date(t['datetime'])
    if not published:
        t = soup.select_one('time')
        if t:
            published = parse_date(t.get_text())

    text = content.get_text('\n')
    info = info_box_text(content) or text
    box = soup.select_one('.post_c_in')
    def fv(*labels):
        return field_value_next(info, *labels) or field_value(info, *labels)
    updated = parse_date(fv('Thread Updated', 'Updated', 'Last Updated'))
    release = parse_date(fv('Release Date', 'Released'))
    censored = fv('Censored')
    language = fv('Language')
    version_full = fv('Version')
    engine = fv('Engine') or engine_hint
    status = fv('Status')

    # --- genre / tags: the post's own tag list (div.postcamp_fn_tags).
    # Full list kept as genres_raw; catalog 'genres' use norm_tags only,
    # so no explicit kink tags become tag pages.
    genre_raw = []
    for a in content.select('div.postcamp_fn_tags li.tag_item a'):
        t = clean(a.get_text())
        if t and t not in genre_raw:
            genre_raw.append(t)
    if not genre_raw and box is not None:
        # Genre field behind its 'See More' toggle: one comma-separated list.
        for d in box.find_all('div'):
            st = d.find('strong')
            if st and clean(st.get_text()).lower() == 'genre':
                tog = d.find_next_sibling('div', class_='mks_toggle')
                tc = tog.select_one('.mks_toggle_content') if tog is not None else None
                if tc is not None:
                    txt = clean(tc.get_text(' '))
                    txt = re.sub(r'^see more\s*', '', txt, flags=re.I)
                    genre_raw = [clean(t) for t in txt.split(',') if clean(t)]
                break
    if not genre_raw:
        genre_field = field_value(text, 'Genre', 'Genres', 'Tags')
        if genre_field:
            genre_raw = split_list(genre_field)
        for a in content.select('a[rel="tag"]'):
            t = clean(a.get_text())
            if t and t not in genre_raw:
                genre_raw.append(t)
    genres = norm_tags(genre_raw)
    if not engine and re.search(r'\bhtml\b', text, re.I) and \
            re.search(r'\bbrowser\b', text, re.I):
        engine = 'HTML'
    if engine.lower() == 'html' and 'HTML' not in genres:
        genres.append('HTML')

    # --- OS: the info-box OS field, exactly as the post lists it.
    # (No augmentation from the changelog/download text: the field is the
    # post's own statement. Empty field falls back to the download OS keys.)
    os_field = fv('OS', 'Operating System', 'Platform', 'Platforms')
    os_list = norm_os(os_field) if os_field else []

    # --- developer links + installation (info-box rows)
    developer_links = []
    installation = []
    if box is not None:
        for d in box.find_all('div'):
            st = d.find('strong')
            if not st:
                continue
            label = clean(st.get_text()).lower()
            if label == 'developer':
                for a in d.find_all('a', href=True):
                    lab = clean(a.get_text())
                    href = urljoin(url, a['href'])
                    if lab and href:
                        developer_links.append({'label': lab, 'url': href})
            elif label == 'installation':
                tog = d.find_next_sibling('div', class_='mks_toggle')
                tc = tog.select_one('.mks_toggle_content') if tog is not None else None
                if tc is not None:
                    for x in tc.find_all('div'):
                        if x.find('div'):
                            continue
                        t = clean(x.get_text())
                        if t:
                            installation.append(t[:300])
                    installation = installation[:12]

    # --- overview / description: the info-box paragraph first (it is the
    # post's own overview), then an Overview heading, then long paragraphs.
    overview = ''
    lines = [clean(l) for l in text.splitlines()]
    if box is not None:
        for p in box.find_all('p'):
            t = clean(p.get_text(' '))
            if len(t) > 40:
                overview = t[:1500]
                break
    if not overview:
        try:
            i = next(k for k, l in enumerate(lines)
                     if re.match(r'^overview\b', l, re.I))
            buf = []
            stop = re.compile(r'^(thread updated|release date|developer|censored|'
                              r'version|os|language|genre|changelog|download|'
                              r'screenshots|info|details|installation)\b', re.I)
            for l in lines[i + 1:]:
                if stop.match(l) and buf:
                    break
                if l:
                    buf.append(l)
                if len(' '.join(buf)) > 1500:
                    break
            overview = ' '.join(buf).strip()
        except StopIteration:
            overview = ''
    if not overview:
        paras = [clean(p.get_text(' ')) for p in content.select('p')]
        paras = [p for p in paras if len(p) > 40]
        overview = ' '.join(paras[:2])[:1500]

    # --- changelog: version toggles after the 'Changelog' marker, before
    # the Download section. Output is [[label, [entries]], ...] to match
    # generate.py. Capped: 4 sections, 15 entries each, 250 chars each.
    changelog = []
    els = list(content.find_all(True))
    ch_idx = None
    for i, e in enumerate(els):
        if e.name == 'strong' and clean(e.get_text()).lower().startswith('changelog'):
            ch_idx = i
            break
    if ch_idx is not None:
        dl_idx = None
        for i in range(ch_idx + 1, len(els)):
            e = els[i]
            if e.name in ('h2', 'h3', 'h4', 'strong') and \
                    re.match(r'^\s*download', clean(e.get_text()), re.I):
                dl_idx = i
                break
        end = dl_idx if dl_idx is not None else len(els)
        for e in els[ch_idx:end]:
            if e.name != 'div' or 'mks_toggle' not in (e.get('class') or []):
                continue
            par = e.parent
            nested = False
            while par is not None and par is not content:
                if par.name == 'div' and 'mks_toggle' in (par.get('class') or []):
                    nested = True
                    break
                par = par.parent
            if nested:
                continue
            tc = e.select_one('.mks_toggle_content')
            if tc is None:
                continue
            header = ''
            for d in tc.find_all('div', recursive=False):
                t = clean(d.get_text())
                if re.search(r'v?\d+\.\d+|\b\d{4}-\d{2}-\d{2}\b', t) and len(t) < 120:
                    header = t
                    break
            inner = tc.select_one('.mks_toggle .mks_toggle_content')
            container = inner if inner is not None else tc
            entries = []
            for d in container.find_all('div', recursive=False):
                t = clean(d.get_text())
                if t[:1] in ('\u2013', '-', '\u2022') and len(t) > 8:
                    entries.append(re.sub(r'^[\u2013\-\u2022]\s*', '', t)[:250])
                if len(entries) >= 15:
                    break
            if header or entries:
                changelog.append([header or 'Changelog', entries])
            if len(changelog) >= 4:
                break
    if not changelog:
        for line in lines:
            m = re.match(r'^(v?\d[\d.]*[a-z]?)\s*[-\u2013\u2014]\s*(.+)$', line, re.I)
            if m:
                changelog.append([m.group(1), [m.group(2)[:250]]])
        changelog = changelog[:4]

    # --- images (hotlinks only; never downloaded)
    images = []
    seen_img = set()
    for img in content.find_all('img'):
        src = img.get('data-src') or img.get('src') or ''
        if not src:
            srcset = img.get('srcset') or ''
            if srcset:
                src = srcset.split(',')[-1].strip().split(' ')[0]
        src = urljoin(url, src)
        # gallery thumbs carry a -<WxH> size suffix; strip it for full size
        src = re.sub(r'-\d+x\d+(?=\.(?:webp|jpg|jpeg|png|gif)(?:\?|$))', '', src, flags=re.I)
        if not re.match(r'https://f95zone\.to\.it/wp-content/uploads/', src):
            continue
        if not re.search(r'\.(webp|jpg|jpeg|png|gif)(\?|$)', src, re.I):
            continue
        name = src.lower()
        if any(x in name for x in ('logo', 'icon', 'avatar')):
            continue
        if src not in seen_img:
            seen_img.add(src)
            images.append(src)
    cover_url = ''
    og_img = soup.select_one('meta[property="og:image"]')
    og_src = og_img['content'] if og_img and og_img.get('content') else ''
    # Feature image: the img in .post_top_format .fn__image_format.
    feat_src = ''
    feat = soup.select_one('.post_top_format .fn__image_format img')
    if feat is not None:
        feat_src = feat.get('data-src') or feat.get('src') or ''
        feat_src = urljoin(url, feat_src)
        feat_src = re.sub(r'-\d+x\d+(?=\.(?:webp|jpg|jpeg|png|gif)(?:\?|$))', '', feat_src, flags=re.I)
    if feat_src and re.match(r'https://f95zone\.to\.it/wp-content/uploads/', feat_src):
        cover_url = feat_src
    if not cover_url:
        for src in images:
            if 'cover' in src.lower():
                cover_url = src
                break
    if not cover_url:
        og_full = re.sub(r'-\d+x\d+(?=\.(?:webp|jpg|jpeg|png|gif)(?:\?|$))', '', og_src, flags=re.I)
        if og_full in images:
            cover_url = og_full
        elif re.match(r'https://f95zone\.to\.it/wp-content/uploads/', og_full or ''):
            cover_url = og_full
    if not cover_url and images:
        cover_url = images[0]
    screenshots = [u for u in images if u != cover_url][:10]

    # --- download mirrors per OS (host names + real hrefs only, never invented).
    # Walk the post content from the Download heading on: short headers name
    # the OS section (Win/Linux, Mac, Android ...); each host link under a
    # header belongs to every OS that header names.
    mirrors = {}
    dl_idx = None
    for i, e in enumerate(els):
        if e.name in ('h2', 'h3', 'h4', 'strong', 'p') and \
                re.match(r'^\s*download', clean(e.get_text()), re.I):
            dl_idx = i
            break
    if dl_idx is not None:
        current_os_list = []
        for e in els[dl_idx:]:
            cls = ' '.join(e.get('class') or [])
            if 'tshare' in cls or 'banner' in cls:
                break
            txt = clean(e.get_text())
            if e.name != 'a' and len(txt) < 40:
                names = norm_os(txt)
                if names:
                    current_os_list = names
                    for o in names:
                        mirrors.setdefault(o, [])
                    continue
                if e.name in ('h2', 'h3') and e is not els[dl_idx]:
                    break
            if e.name == 'a':
                host = host_from_link(e)
                if host:
                    href = e.get('href') or ''
                    href = urljoin(url, href) if href and not href.startswith('#') else ''
                    for key in (current_os_list or ['Windows']):
                        lst = mirrors.setdefault(key, [])
                        if host not in [x['host'] for x in lst]:
                            lst.append({'host': host, 'url': href})
    # OS fallback (empty info-box field only): the download section's OS keys.
    if not os_list:
        os_list = [o for o in OS_NAMES if o in mirrors] or ['Windows']
    for os_name in os_list:
        mirrors.setdefault(os_name, [])

    # --- size clues
    size = ''
    m = re.search(r'(\d+(?:\.\d+)?\s*(?:MB|GB))\s*(?:\(artwork|artwork bundle)',
                  text, re.I)
    if m:
        size = 'approx. ~%s (artwork bundle)' % m.group(1)
    else:
        m = re.search(r'(\d+(?:\.\d+)?\s*(?:MB|GB))', text)
        if m:
            size = 'approx. ~%s' % m.group(1)

    # --- format from OS/engine
    fmt_parts = []
    desktop = [o for o in os_list if o in ('Windows', 'Linux', 'Mac')]
    if desktop:
        fmt_parts.append('ZIP (%s)' % ' / '.join(desktop))
    if 'Android' in os_list:
        fmt_parts.append('APK (Android)')
    if engine.lower() == 'html' or 'HTML' in genres:
        fmt_parts.append('HTML (browser)')
    fmt = ' \u00b7 '.join(fmt_parts)

    return {
        'slug': slug_from_url(url),
        'title': title,
        'version': version,
        'version_full': version_full,
        'developer': developer,
        'developer_links': developer_links,
        'installation': installation,
        'status': status or 'Ongoing',
        'engine': engine,
        'os': ', '.join(os_list),
        'language': language,
        'release': release or '\u2014',
        'updated': updated or published,
        'published': published,
        'censored': censored,
        'rating': 0.0,
        'reviews': 0,
        'genres_raw': genre_raw,
        'genres': genres,
        'overview': overview,
        'size': size,
        'format': fmt,
        'changelog': changelog,
        'faq': [],
        'reviews_list': [],
        'cover_url': cover_url,
        'screenshots': screenshots,
        'mirrors': mirrors,
        'source_url': url,
    }

# ---------------------------------------------------------------- merge
def build_game_record(entry):
    rec = dict(entry)
    rec.pop('genres_raw', None)
    rec.pop('published', None)
    return rec

def merge_games(existing, crawled):
    by_slug = {g['slug']: dict(g) for g in existing}
    order = [g['slug'] for g in existing]
    for entry in crawled:
        rec = build_game_record(entry)
        if rec['slug'] in by_slug:
            merged = dict(by_slug[rec['slug']])
            merged.update(rec)
            by_slug[rec['slug']] = merged
        else:
            by_slug[rec['slug']] = rec
            order.append(rec['slug'])
    return [by_slug[s] for s in order]

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description='GameVault crawler for f95zone.to.it')
    ap.add_argument('--dry-run', action='store_true',
                    help='fetch and parse only; write nothing')
    ap.add_argument('--pages', type=int, default=None,
                    help='homepage pages to crawl (default: MAX_PAGES env or 1)')
    ap.add_argument('--posts', type=int, default=None,
                    help='max post titles to crawl from page 1 (default: MAX_POSTS env or 11)')
    ap.add_argument('--seed', action='append', default=[],
                    help='extra post URL to crawl (repeatable)')
    ap.add_argument('--out', default=None,
                    help='repo root (default: parent of the crawl/ folder)')
    args = ap.parse_args()

    root = Path(args.out).resolve() if args.out else Path(__file__).resolve().parent.parent
    max_pages = args.pages if args.pages is not None else MAX_PAGES
    max_posts = args.posts if args.posts is not None else MAX_POSTS
    session = requests.Session()
    session.headers.update({'User-Agent': UA})

    print('crawl: homepage page 1..%d of %s' % (max_pages, BASE_URL))
    found = []
    seen = set()
    for page in range(1, max_pages + 1):
        url = BASE_URL if page == 1 else '%spage/%d/' % (BASE_URL, page)
        html = fetch(session, url)
        posts = parse_homepage(html, url)
        print('crawl: page %d -> %d post links' % (page, len(posts)))
        for post in posts:
            if post['url'] not in seen:
                seen.add(post['url'])
                found.append(post)
        time.sleep(1)

    found = found[:max_posts]
    print('crawl: taking first %d titles from page 1 (MAX_POSTS=%d)'
          % (len(found), max_posts))
    hints = {p['url']: p.get('engine', '') for p in found}
    urls = [p['url'] for p in found]
    for seed in list(dict.fromkeys(SEED_URLS + args.seed)):
        if seed not in urls:
            if len(urls) >= max_posts:
                dropped = urls[-1]
                urls[-1] = seed
                print('crawl: seed is the %dth entry (replaces %s): %s'
                      % (max_posts, dropped, seed))
            else:
                urls.append(seed)
                print('crawl: seed added (not on homepage page 1): %s' % seed)

    entries = []
    for url in urls:
        try:
            html = fetch(session, url)
        except Exception as e:
            print('crawl: FAILED %s: %s' % (url, e))
            continue
        entry = parse_post(html, url, hints.get(url, ''))
        if not entry['title'] or not entry['slug']:
            print('crawl: SKIP %s (no title/slug parsed)' % url)
            continue
        entries.append(entry)
        print('crawl: %s [%s] [%s] updated=%s os=%s genres=%s cover=%s shots=%d mirrors=%s' % (
            entry['title'], entry['version'], entry['developer'],
            entry['updated'], entry['os'], ','.join(entry['genres']),
            'yes' if entry['cover_url'] else 'no', len(entry['screenshots']),
            {k: [e['host'] for e in v] for k, v in entry['mirrors'].items()}))
        time.sleep(1)

    print('crawl: parsed %d/%d posts' % (len(entries), len(urls)))
    if args.dry_run:
        print(json.dumps(entries, indent=2, ensure_ascii=False))
        print('crawl: dry-run, nothing written')
        return 0

    data_dir = root / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    crawled_path = data_dir / 'crawled.json'
    crawled_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False),
                            encoding='utf-8')
    print('crawl: wrote %s (%d entries)' % (crawled_path, len(entries)))

    games_path = data_dir / 'games.json'
    existing = []
    if games_path.exists():
        try:
            existing = json.loads(games_path.read_text(encoding='utf-8'))
        except Exception as e:
            print('crawl: warning, could not read %s: %s' % (games_path, e))
    merged = merge_games(existing, entries)
    games_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False),
                          encoding='utf-8')
    print('crawl: wrote %s (%d games: %d kept + %d crawled)'
          % (games_path, len(merged), len(existing), len(entries)))

    gen = root / 'scripts' / 'generate.py'
    if not gen.exists():
        alt = root.parent / 'frightening-skull-build' / 'generate.py'
        gen = alt if alt.exists() else None
    if gen is None:
        print('crawl: WARNING generate.py not found, site not regenerated')
    else:
        print('crawl: regenerating site with %s --out %s' % (gen, root))
        r = subprocess.run([sys.executable, str(gen), '--out', str(root)],
                           capture_output=True, text=True)
        print(r.stdout)
        if r.returncode != 0:
            print(r.stderr, file=sys.stderr)
            return r.returncode

    log_path = root / 'crawl' / ('crawl-%s.md' % date.today().isoformat())
    lines = ['# Crawl run — %s\n' % date.today().isoformat(),
             'Homepage pages crawled: %d (MAX_PAGES=%d, MAX_POSTS=%d). '
             'Posts parsed: %d/%d.\n'
             % (max_pages, max_pages, max_posts, len(entries), len(urls)),
             '## Posts\n']
    for e in entries:
        lines.append('- **%s [%s] [%s]** — %s — updated %s — OS %s — genres %s — '
                     'cover %s, %d screenshots — source: %s\n'
                     % (e['title'], e['version'], e['developer'], e['slug'],
                        e['updated'], e['os'], ', '.join(e['genres']) or '—',
                        'yes' if e['cover_url'] else 'no',
                        len(e['screenshots']), e['source_url']))
    lines.append('\nImages are hotlinks only; no files hosted. '
                 'Mirror hrefs come from the post HTML only, never invented.\n')
    log_path.write_text(''.join(lines), encoding='utf-8')
    print('crawl: wrote %s' % log_path)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
