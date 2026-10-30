#!/usr/bin/env python3
"""Generate the static GameVault catalog for GitHub Pages.

Source data: 8 ORIGINAL demo games (hardcoded below) plus real entries added
by crawl/crawl.py from f95zone.to.it post pages (see data/crawled.json).
The generator loads data/games.json when present and merges it over the
hardcoded demo games, so crawler updates survive regeneration.
Crawled images are HOTLINKS to the source post (never copied into the repo);
download sections are external mirror links (host names + hrefs from the
post, never invented). No pricing, no cart, no discount badges anywhere.
"""
import json, os, html, argparse
from pathlib import Path

OUT = Path.home() / "workspace" / "frightening-skull"
SITE = "https://nabeelshar.github.io/frightening-skull"

GAMES = [
    {
        "slug": "starfall-academy", "title": "Starfall Academy", "version": "0.8.2",
        "developer": "Northlight Games", "status": "Ongoing", "engine": "Ren'Py",
        "os": "Windows, Android, Linux, Mac",
        "size": "820 MB", "format": "ZIP (Windows / Linux / Mac) · APK (Android)", "language": "English",
        "release": "2025-11-14", "updated": "2026-10-28", "rating": 4.6, "reviews": 128,
        "genres": ["Visual Novel", "Adventure", "2DCG", "2D Game", "Dating Sim", "Romance", "Drama", "Multiple Endings", "Harem", "Animated"],
        "overview": "A new student arrives at a remote academy built beneath a fallen star, and the school's quiet routines start to unravel. Build friendships, uncover the academy's old secret, and choose which side of it you stand on.",
        "changelog": [
            ("v0.8.2", ["New evening route with two endings", "Added gallery scene for chapter 7", "Fixed save files failing to load after chapter 6"]),
            ("v0.8.0", ["Chapter 7 released", "Reworked the library event chain", "New background art for the observatory"]),
        ],
        "faq": [
            ("Is Starfall Academy finished?", "No — it is in active development at version 0.8.2, with new chapters released every few weeks."),
            ("What engine does it use?", "Ren'Py, and it runs on Windows, Linux and Mac."),
        ],
        "reviews_list": [
            ("LanternReader", 5, "Slow start, but chapter 7 pays off. The academy mystery is genuinely well written."),
            ("quietfox", 4, "Good art and a likeable cast. Waiting on the next chapter already."),
        ],
    },
    {
        "slug": "kingdom-of-ashes", "title": "Kingdom of Ashes", "version": "1.0",
        "developer": "Emberworks Studio", "status": "Completed", "engine": "Unity",
        "os": "Windows, Android, Linux, Mac",
        "size": "1.4 GB", "format": "ZIP (Windows / Linux / Mac) · APK (Android)", "language": "English",
        "release": "2024-06-02", "updated": "2026-09-19", "rating": 4.8, "reviews": 214,
        "genres": ["RPG", "Fantasy", "Adventure", "3D Game", "3DCG", "Strategy", "Management", "Multiple Endings", "Male Protagonist"],
        "overview": "The ember crown has burned out and the kingdom's provinces are choosing new rulers. Lead a small band across a war-scarred realm, forge alliances, and decide what rises from the ashes.",
        "changelog": [
            ("v1.0", ["Final chapter and true ending added", "New game+ mode with carried-over relics", "Full balance pass on the last two regions"]),
            ("v0.9", ["Epilogue scenes for every companion", "Fixed the Ashen Gate soft-lock"]),
        ],
        "faq": [
            ("Is Kingdom of Ashes finished?", "Yes — version 1.0 is the complete game, including the true ending and new game+ mode."),
            ("How long is it?", "A first playthrough takes roughly 25–30 hours."),
        ],
        "reviews_list": [
            ("emberfan", 5, "A complete, polished RPG. The companion endings alone are worth the playthrough."),
            ("mapmaker", 5, "Best worldbuilding in the catalog. Every province feels distinct."),
        ],
    },
    {
        "slug": "neon-horizon", "title": "Neon Horizon", "version": "0.6.1",
        "developer": "Pixel Drift", "status": "Ongoing", "engine": "Godot",
        "os": "Windows, Android, Linux",
        "size": "960 MB", "format": "ZIP (Windows / Linux) · APK (Android)", "language": "English",
        "release": "2026-01-20", "updated": "2026-10-27", "rating": 4.4, "reviews": 96,
        "genres": ["Sci-Fi", "Adventure", "2DCG", "2D Game", "Sandbox", "Simulation", "Comedy", "Animated"],
        "overview": "A courier pilot takes one last contract across a neon-lit orbital ring — and the cargo turns out to be a person. Outrun patrols, pick your clients, and keep your ship flying.",
        "changelog": [
            ("v0.6.1", ["New dockside district with three side jobs", "Improved controller support", "Fixed cargo missions failing on reload"]),
            ("v0.6.0", ["Ring sector 4 opened", "New ship upgrade: ion shielding"]),
        ],
        "faq": [
            ("Is Neon Horizon finished?", "Not yet — it is at version 0.6.1 with new sectors still being added."),
            ("Does it work on Linux?", "Yes, Windows and Linux builds are both provided."),
        ],
        "reviews_list": [
            ("driftking", 4, "Great sense of speed and a fun courier loop. A few rough edges in the new sector."),
            ("novapilot", 5, "The orbital ring is a fantastic setting. Soundtrack is excellent too."),
        ],
    },
    {
        "slug": "echoes-of-tomorrow", "title": "Echoes of Tomorrow", "version": "0.9.3",
        "developer": "Lantern Fox", "status": "Ongoing", "engine": "Ren'Py",
        "os": "Windows, Android, Linux, Mac",
        "size": "1.1 GB", "format": "ZIP (Windows / Linux / Mac) · APK (Android)", "language": "English",
        "release": "2025-08-08", "updated": "2026-10-29", "rating": 4.7, "reviews": 167,
        "genres": ["Visual Novel", "Sci-Fi", "AI CG", "2D Game", "Drama", "Multiple Endings", "Romance", "Animated"],
        "overview": "A time-loop archivist wakes up on the same morning for the forty-first time. Each loop leaves a new message behind — and someone else in the city is looping too.",
        "changelog": [
            ("v0.9.3", ["Loop 41 route completed", "Added codex entries for the second looper", "Fixed a loop-counter bug on day 12"]),
            ("v0.9.0", ["New ending branch: break the loop", "Reworked the archive puzzle"]),
        ],
        "faq": [
            ("Is Echoes of Tomorrow finished?", "Almost — version 0.9.3 is the penultimate release, with the finale in progress."),
            ("What does AI CG mean here?", "Some of the game's artwork was produced with AI-assisted tools; it is listed as a tag so players know."),
        ],
        "reviews_list": [
            ("looper", 5, "The time-loop mystery is tightly plotted. Every loop recontextualises the last."),
            ("archivist", 4, "Clever structure and strong writing. Hoping the finale lands."),
        ],
    },
    {
        "slug": "emberfall-chronicles", "title": "Emberfall Chronicles", "version": "0.4.0",
        "developer": "Ashen Quill", "status": "Ongoing", "engine": "RPG Maker",
        "os": "Windows, Android, Mac",
        "size": "640 MB", "format": "ZIP (Windows / Mac) · APK (Android)", "language": "English",
        "release": "2026-03-11", "updated": "2026-10-21", "rating": 4.3, "reviews": 74,
        "genres": ["RPG", "Fantasy", "Adventure", "2D Game", "Sandbox", "Simulation", "Management", "Comedy"],
        "overview": "When the ember falls, the old roads wake. Guide a cartographer mapping a kingdom that rearranges itself each season, and chart what no one else has survived to draw.",
        "changelog": [
            ("v0.4.0", ["Autumn region opened with a new town", "Added the seasonal road-shifting mechanic", "Fixed fast-travel breaking after chapter 3"]),
        ],
        "faq": [
            ("Is Emberfall Chronicles finished?", "No — it is at version 0.4.0 and updated regularly."),
            ("What engine does it use?", "RPG Maker, on Windows and Mac."),
        ],
        "reviews_list": [
            ("cartographer", 4, "Charming old-school RPG. The shifting-roads idea is a neat hook."),
            ("quillfan", 4, "Relaxing pace, good music, and the autumn region looks lovely."),
        ],
    },
    {
        "slug": "voidrunner-protocol", "title": "Voidrunner Protocol", "version": "1.2.0",
        "developer": "Orbital Nine", "status": "Completed", "engine": "Unreal",
        "os": "Windows, Android, Linux",
        "size": "2.1 GB", "format": "ZIP (Windows / Linux) · APK (Android)", "language": "English",
        "release": "2025-02-17", "updated": "2026-08-30", "rating": 4.5, "reviews": 189,
        "genres": ["Sci-Fi", "Roguelike", "AI CG", "3D Game", "3DCG", "Strategy", "Sandbox", "Simulation", "Male Protagonist"],
        "overview": "Pilot a salvage runner through dead stations on the edge of known space. Every run reshuffles the wrecks, the hazards, and the things still living inside them.",
        "changelog": [
            ("v1.2.0", ["Final balance pass and hard mode", "New wreck type: the reliquary station", "Fixed salvage scoring on failed runs"]),
            ("v1.0", ["Full release: 12 wreck types, 3 endings"]),
        ],
        "faq": [
            ("Is Voidrunner Protocol finished?", "Yes — version 1.2.0 is the complete game, including hard mode."),
            ("Is every run different?", "Yes, wrecks, hazards and loot are reshuffled each run."),
        ],
        "reviews_list": [
            ("salvager", 5, "Tense, replayable, and fair. Hard mode is a real test."),
            ("voidwalker", 4, "Great atmosphere. Runs stay fresh for a long time."),
        ],
    },
    {
        "slug": "lanterns-of-the-deep", "title": "Lanterns of the Deep", "version": "0.3.5",
        "developer": "Tidepool Interactive", "status": "On Hold", "engine": "Godot",
        "os": "Windows, Android",
        "size": "480 MB", "format": "ZIP (Windows) · APK (Android)", "language": "English",
        "release": "2025-12-05", "updated": "2026-07-12", "rating": 4.1, "reviews": 58,
        "genres": ["Horror", "Adventure", "2DCG", "2D Game", "Drama", "Female Protagonist", "Animated"],
        "overview": "A lighthouse keeper's daughter rows out to relight the dark lanterns of a drowned town. Something down there keeps the lights for itself.",
        "changelog": [
            ("v0.3.5", ["Second lantern route added", "New ambient audio for the drowned streets", "Fixed the rowboat getting stuck at the pier"]),
        ],
        "faq": [
            ("Is Lanterns of the Deep still being updated?", "It is currently on hold at version 0.3.5 — the developer has paused work on it."),
            ("Is it scary?", "It is a slow, atmospheric horror game rather than a jump-scare game."),
        ],
        "reviews_list": [
            ("deepdiver", 4, "Wonderfully eerie. The drowned town is unforgettable."),
            ("lanternkeeper", 4, "Short so far, but the mood is perfect. Hope it resumes."),
        ],
    },
    {
        "slug": "ashenvale-pact", "title": "Ashenvale Pact", "version": "0.7.0",
        "developer": "Moss & Ember", "status": "Ongoing", "engine": "Unity",
        "os": "Windows, Android, Linux, Mac",
        "size": "1.8 GB", "format": "ZIP (Windows / Linux / Mac) · APK (Android)", "language": "English",
        "release": "2026-05-24", "updated": "2026-10-26", "rating": 4.6, "reviews": 143,
        "genres": ["Fantasy", "Roguelike", "Turn Based Combat", "3D Game", "3DCG", "Strategy", "Management"],
        "overview": "Sign a pact with the Ashenvale and lead a warband through a forest that fights back. Turn-based battles, shifting terrain, and a bargain that grows more expensive every chapter.",
        "changelog": [
            ("v0.7.0", ["New pact tier with two warband abilities", "Forest terrain now shifts mid-battle", "Fixed pact costs not scaling after chapter 4"]),
            ("v0.6.0", ["Warband camp system added", "New enemy: the hollow dryad"]),
        ],
        "faq": [
            ("Is Ashenvale Pact finished?", "No — it is at version 0.7.0 with more pact tiers planned."),
            ("How does combat work?", "Turn-based, position-based battles with terrain that changes during the fight."),
        ],
        "reviews_list": [
            ("pactmaker", 5, "The pact system is a brilliant risk-reward hook. Combat stays fresh."),
            ("forestwalker", 4, "Tough but fair. The shifting terrain keeps every battle tense."),
        ],
    },
]

# The "Crawled from f95zone.to.it" home-page list is built from the catalog
# itself (games with a source_url, added by crawl/crawl.py).

def tag_slug(t):
    return t.lower().replace(" ", "-")

def esc(s):
    return html.escape(str(s))

def stars(r):
    full = int(round(r))
    return "★" * full + "☆" * (5 - full)

def status_class(s):
    return {"Completed": "st-completed", "Ongoing": "st-ongoing", "On Hold": "st-onhold"}.get(s, "st-ongoing")

COVER_COLORS = {
    "starfall-academy": ("#3d6a8c", "#1b2838"),
    "kingdom-of-ashes": ("#8c4a2f", "#2b1a12"),
    "neon-horizon": ("#0f766e", "#171a21"),
    "echoes-of-tomorrow": ("#5b4a8c", "#1b2838"),
    "emberfall-chronicles": ("#8c6a2f", "#2b2412"),
    "voidrunner-protocol": ("#2f5b8c", "#0f1922"),
    "lanterns-of-the-deep": ("#2f4a5b", "#0a141a"),
    "ashenvale-pact": ("#4a6b2f", "#16210f"),
    "pinked-and-owned": ("#8c2f5b", "#22101a"),
}

def initials(title):
    words = [w for w in title.replace("-", " ").split() if w and w[0].isalpha()]
    return "".join(w[0] for w in words[:2]).upper()

def cover_svg(title, slug, label="Placeholder cover art"):
    c1, c2 = COVER_COLORS.get(slug, ("#3d6a8c", "#1b2838"))
    ini = initials(title)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="338" viewBox="0 0 600 338" role="img" aria-label="{html.escape(title)} — {label}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>
<rect width="600" height="338" fill="url(#g)"/>
<circle cx="480" cy="70" r="90" fill="#ffffff" opacity="0.08"/>
<circle cx="80" cy="280" r="120" fill="#ffffff" opacity="0.06"/>
<text x="300" y="175" text-anchor="middle" font-family="Arial, sans-serif" font-size="96" font-weight="bold" fill="#ffffff" opacity="0.9">{ini}</text>
<text x="300" y="225" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="#c7d5e0">{html.escape(title)}</text>
<text x="300" y="255" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#8f98a3">{label}</text>
</svg>
"""

ALL_TAGS = sorted({t for g in GAMES for t in g["genres"]}, key=str.lower)

GAME_FIELDS = ("slug", "title", "version", "version_full", "developer",
               "developer_links", "installation", "status", "engine", "os",
               "language", "release", "updated", "rating", "reviews", "genres",
               "overview", "size", "format", "changelog", "faq", "reviews_list",
               "cover_url", "screenshots", "mirrors", "source_url", "censored")

def full_record(g):
    r = {k: g.get(k) for k in GAME_FIELDS}
    r["rating"] = float(r.get("rating") or 0.0)
    r["reviews"] = int(r.get("reviews") or 0)
    r["genres"] = list(r.get("genres") or [])
    cl = r.get("changelog") or []
    norm_cl = []
    for item in cl:
        if isinstance(item, dict):
            label = item.get("version") or "Changelog"
            if item.get("date"):
                label = label + " \u2014 " + item["date"]
            norm_cl.append([label, list(item.get("entries") or [])])
        else:
            v, n = item
            norm_cl.append([v, list(n)])
    r["changelog"] = norm_cl
    r["version_full"] = r.get("version_full") or ""
    dl = []
    for d in (r.get("developer_links") or []):
        if isinstance(d, dict):
            dl.append([d.get("label", ""), d.get("url", "")])
        elif isinstance(d, (list, tuple)) and len(d) == 2:
            dl.append([d[0], d[1]])
    r["developer_links"] = dl
    r["installation"] = list(r.get("installation") or [])
    r["faq"] = [[q, a] for q, a in (r.get("faq") or [])]
    r["reviews_list"] = [[a, rr, t] for a, rr, t in (r.get("reviews_list") or [])]
    r["cover_url"] = r.get("cover_url") or ""
    r["screenshots"] = list(r.get("screenshots") or [])
    r["mirrors"] = r.get("mirrors") or {}
    r["source_url"] = r.get("source_url") or ""
    r["censored"] = r.get("censored") or ""
    return r

def load_games():
    base = {g["slug"]: full_record(g) for g in GAMES}
    order = [g["slug"] for g in GAMES]
    jf = OUT / "data" / "games.json"
    if jf.exists():
        try:
            for rec in json.loads(jf.read_text(encoding="utf-8")):
                slug = rec.get("slug")
                if not slug:
                    continue
                if slug in base:
                    merged = dict(base[slug])
                    merged.update(full_record(rec))
                    base[slug] = merged
                else:
                    base[slug] = full_record(rec)
                    order.append(slug)
        except Exception as e:
            print("warning: could not load %s: %s" % (jf, e))
    return [base[slug] for slug in order]

def cover_thumb(g):
    if g.get("cover_url"):
        return '<img class="coverimg" src="' + esc(g["cover_url"]) + '" alt="' + esc(g["title"]) + ' \u2014 cover art hotlinked from source post" loading="lazy">'
    return '<img class="coverimg" src="/frightening-skull/assets/covers/' + g["slug"] + '.svg" alt="' + esc(g["title"]) + ' \u2014 placeholder cover art" loading="lazy">'

def mirrors_html(g):
    out = []
    for o in g["os"].split(","):
        o = o.strip()
        entries = (g.get("mirrors") or {}).get(o)
        if entries:
            parts = []
            for e in entries:
                host = e.get("host", "")
                url = e.get("url") or "#"
                extra = ' target="_blank" rel="nofollow noopener"' if e.get("url") else ""
                tip = host + " mirror link" + ("" if e.get("url") else " \u2014 not set yet, fill from the post")
                parts.append('<a class="mirror" href="' + esc(url) + '"' + extra + ' data-os="' + esc(o) + '" data-host="' + esc(host) + '" title="' + esc(tip) + '">' + esc(host) + '</a>')
            links = " \u2013 ".join(parts)
        else:
            links = " \u2013 ".join(
                '<a class="mirror" href="#" data-os="' + esc(o) + '" data-host="' + h + '" title="' + h + ' mirror link \u2014 not set yet, fill from the post">' + h + '</a>'
                for h in MIRROR_HOSTS)
        out.append('<p class="mirrors"><strong>' + esc(o) + ':</strong> ' + links + '</p>')
    return "".join(out)

MIRROR_HOSTS = ["MEGA", "GOFILE", "PIXELDRAIN", "DATANODES", "WORKUPLOAD"]

CSS = """/* GameVault — Steam-style storefront, no pricing. Dark blue theme. */
:root{--bg:#171a21;--bg2:#1b2838;--panel:#2a475e;--panel2:#22394f;--text:#c7d5e0;--muted:#8f98a3;--accent:#66c0f4;--accent2:#1a9fff;--line:#2a475e}
*{box-sizing:border-box}
body{margin:0;background:linear-gradient(180deg,#1b2838 0%,#171a21 240px);color:var(--text);font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5}
a{color:var(--accent);text-decoration:none}a:hover{color:#fff}
header.site{background:#171a21;border-bottom:1px solid #000;padding:0 16px;position:sticky;top:0;z-index:50}
.wrap{max-width:1060px;margin:0 auto}
.nav{display:flex;align-items:center;gap:22px;min-height:56px;flex-wrap:wrap}
.logo{font-size:22px;font-weight:700;letter-spacing:1px;color:#fff;white-space:nowrap}.logo span{color:var(--accent)}
.nav a.nl{color:#dbe2e6;font-size:14px;text-transform:uppercase;letter-spacing:.4px}.nav a.nl:hover{color:#fff}
.nav .spacer{flex:1}
.searchbox{display:flex;gap:6px}.searchbox input{background:#316282;border:1px solid #000;color:#fff;padding:7px 10px;border-radius:2px;width:210px;font-size:14px}.searchbox input::placeholder{color:#9fc3d8}.searchbox button{background:#1a9fff;color:#fff;border:0;padding:7px 12px;border-radius:2px;cursor:pointer}
.subnav{background:#1b2838;border-bottom:1px solid var(--line);padding:10px 16px}
.subnav .wrap{display:flex;gap:18px;flex-wrap:wrap;font-size:14px}
.subnav a{color:#c7d5e0}.subnav a:hover{color:#fff}
main{padding:20px 16px 60px}
h1{color:#fff;font-size:26px;margin:6px 0 4px}h2{color:#fff;font-size:20px;margin:28px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}h3{color:#fff;font-size:16px;margin:0 0 6px}
.lede{color:var(--muted);margin:0 0 14px}
.hero{border-radius:4px;overflow:hidden;border:1px solid #000;margin:10px 0 6px;position:relative}
.slide{display:none;padding:34px 26px;min-height:210px;background:linear-gradient(120deg,#2a475e,#1b2838 60%,#0f1922)}
.slide.active{display:block}
.slide .kicker{color:var(--accent);text-transform:uppercase;font-size:12px;letter-spacing:1.5px}
.slide h2{border:0;margin:8px 0;font-size:30px}
.slide p{max-width:640px;color:#dbe2e6}
.slide .cta{display:inline-block;background:var(--accent2);color:#fff;padding:9px 16px;border-radius:2px;margin-top:10px}
.dots{text-align:center;margin:8px 0}.dots button{background:#2a475e;border:0;width:26px;height:6px;margin:0 3px;cursor:pointer;border-radius:3px}.dots button.on{background:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px}
.card{background:var(--panel2);border:1px solid #000;border-radius:3px;overflow:hidden}
.card .art{height:108px;display:flex;align-items:flex-end;padding:10px;background:linear-gradient(135deg,#3d6a8c,#1b2838 70%);color:#fff;font-weight:700;font-size:17px;text-shadow:0 1px 3px #000}
.card .body{padding:10px 12px 12px}
.card .meta{color:var(--muted);font-size:13px;margin:2px 0 6px}
.card .ov{font-size:13.5px;color:#b8c4cf;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin:0 0 8px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{background:#3d6a8c;color:#dbe2e6;font-size:12px;padding:3px 8px;border-radius:2px}
.chip:hover{background:var(--accent2);color:#fff}
.badge{display:inline-block;font-size:12px;padding:2px 8px;border-radius:2px;color:#fff}
.st-completed{background:#4c6b22}.st-ongoing{background:#1a9fff}.st-onhold{background:#7a6a2f}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.tile{background:var(--panel2);border:1px solid #000;border-radius:3px;padding:16px 12px;text-align:center}
.tile b{display:block;color:#fff;font-size:16px}.tile span{color:var(--muted);font-size:13px}
.rows .row{display:flex;gap:12px;align-items:center;background:var(--panel2);border:1px solid #000;border-radius:3px;padding:9px 12px;margin-bottom:8px}
.rows .rank{color:var(--accent);font-weight:700;width:26px}.rows .t{flex:1}.rows .t b{color:#fff}
table.info{border-collapse:collapse;width:100%;max-width:640px}
table.info td{border-bottom:1px solid var(--line);padding:7px 4px;vertical-align:top}
table.info td:first-child{color:var(--muted);width:150px}
.crawl{font-size:13.5px}.crawl li{margin-bottom:8px}
.note{background:#22394f;border-left:3px solid var(--accent);padding:10px 14px;margin:14px 0;font-size:14px}
footer{border-top:1px solid var(--line);padding:22px 16px 40px;color:var(--muted);font-size:13px}
.filters{display:flex;gap:16px;flex-wrap:wrap;margin:12px 0}
.filters fieldset{border:1px solid var(--line);border-radius:3px;padding:8px 12px}
.filters legend{color:#fff;font-size:13px}
.filters label{display:block;font-size:14px;margin:3px 0}
.breadcrumb{color:var(--muted);font-size:13px;margin-bottom:6px}
.review{background:var(--panel2);border:1px solid #000;border-radius:3px;padding:12px;margin-bottom:10px}
details{background:var(--panel2);border:1px solid #000;border-radius:3px;padding:10px 12px;margin-bottom:8px}
details summary{cursor:pointer;color:#fff;font-weight:700}
@media(max-width:640px){.searchbox input{width:140px}.slide h2{font-size:22px}}
.coverimg{display:block;width:100%;height:108px;object-fit:cover}
.coverlarge{display:block;width:100%;max-width:640px;height:auto;border:1px solid #000;border-radius:3px}
.post_top_format{margin:10px 0}.fn__image_format img{display:block;width:100%;max-width:640px;height:auto;border:1px solid #000;border-radius:3px}
.shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin:10px 0}
.shots img{width:100%;height:auto;border:1px solid #000;border-radius:3px}
.shots figcaption{font-size:12px;color:var(--muted);text-align:center}
.osbadge{display:inline-block;background:#3d6a8c;color:#fff;font-size:12px;padding:3px 9px;border-radius:2px;margin:0 4px 4px 0}
.dl{background:#22394f;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:3px;padding:14px;margin:14px 0}
.dl .btn{display:inline-block;background:#3d6a8c;color:#dbe2e6;padding:9px 16px;border-radius:2px;margin-top:8px;cursor:not-allowed;opacity:.75}
.dl code{background:#171a21;padding:2px 6px;border-radius:2px}
.mirrors{margin:10px 0}
.mirror{display:inline-block;background:#1a9fff;color:#fff;font-size:13px;font-weight:700;padding:6px 12px;border-radius:2px;margin:0 4px 4px 0}
.mirror:hover{background:#66c0f4;color:#fff}
"""


JS_CAROUSEL = """let cur=0;const slides=document.querySelectorAll('.slide'),dots=document.querySelectorAll('.dots button');
function show(i){cur=(i+slides.length)%slides.length;slides.forEach((s,j)=>s.classList.toggle('active',j===cur));dots.forEach((d,j)=>d.classList.toggle('on',j===cur));}
dots.forEach((d,j)=>d.addEventListener('click',()=>show(j)));
document.getElementById('prev')?.addEventListener('click',()=>show(cur-1));
document.getElementById('next')?.addEventListener('click',()=>show(cur+1));
setInterval(()=>show(cur+1),6000);
"""

JS_BROWSE = """const cards=[...document.querySelectorAll('.card')];
const q=document.getElementById('q'),sort=document.getElementById('sort');
function apply(){
 const term=(q.value||'').toLowerCase();
 const gens=[...document.querySelectorAll('input[data-genre]:checked')].map(e=>e.value);
 const st=[...document.querySelectorAll('input[data-status]:checked')].map(e=>e.value);
 const eng=[...document.querySelectorAll('input[data-engine]:checked')].map(e=>e.value);
 const min=parseFloat(document.getElementById('minrating').value||'0');
 let vis=cards.filter(c=>{
  const hay=(c.dataset.title+' '+c.dataset.dev).toLowerCase();
  if(term&&!hay.includes(term))return false;
  if(gens.length&&!gens.some(g=>c.dataset.genres.split('|').includes(g)))return false;
  if(st.length&&!st.includes(c.dataset.status))return false;
  if(eng.length&&!eng.includes(c.dataset.engine))return false;
  if(parseFloat(c.dataset.rating)<min)return false;
  return true;
 });
 if(sort.value==='rating')vis.sort((a,b)=>b.dataset.rating-a.dataset.rating);
 if(sort.value==='newest')vis.sort((a,b)=>b.dataset.updated.localeCompare(a.dataset.updated));
 if(sort.value==='title')vis.sort((a,b)=>a.dataset.title.localeCompare(b.dataset.title));
 const grid=document.getElementById('grid');vis.forEach(c=>grid.appendChild(c));
 cards.forEach(c=>c.style.display=vis.includes(c)?'':'none');
 document.getElementById('count').textContent=vis.length+(vis.length===1?' game':' games');
}
document.querySelectorAll('input,select').forEach(e=>e.addEventListener('input',apply));
const p=new URLSearchParams(location.search);if(p.get('tag')){const cb=document.querySelector('input[data-genre="'+p.get('tag')+'"]');if(cb){cb.checked=true;}}
if(p.get('q')){q.value=p.get('q');}
if(p.get('sort')&&[...sort.options].some(o=>o.value===p.get('sort'))){sort.value=p.get('sort');}
apply();
"""

def head(title, desc, path, jsonld=None):
    j = ""
    if jsonld:
        j = '<script type="application/ld+json">\n' + json.dumps(jsonld, indent=2) + "\n</script>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<link rel="stylesheet" href="/frightening-skull/assets/style.css">
{j}
</head>
<body>"""

HEADER = """<header class="site"><div class="wrap nav">
<a class="logo" href="/frightening-skull/">GAME<span>VAULT</span></a>
<a class="nl" href="/frightening-skull/">Store</a>
<a class="nl" href="/frightening-skull/browse.html">Browse</a>
<a class="nl" href="/frightening-skull/browse.html">Genres</a>
<a class="nl" href="/frightening-skull/browse.html?sort=rating">Top Rated</a>
<a class="nl" href="/frightening-skull/browse.html">Wishlist</a>
<span class="spacer"></span>
<form class="searchbox" action="/frightening-skull/browse.html" method="get"><input name="q" type="search" placeholder="Search games" aria-label="Search games"><button type="submit">Search</button></form>
</div></header>
<div class="subnav"><div class="wrap">
<a href="/frightening-skull/">Latest Updates</a><a href="/frightening-skull/browse.html">All Games</a><a href="/frightening-skull/tags/adventure.html">Adventure</a><a href="/frightening-skull/tags/2dcg.html">2DCG</a><a href="/frightening-skull/tags/ai-cg.html">AI CG</a><a href="/frightening-skull/sitemap.html">Sitemap</a>
</div></div>"""

FOOTER = """<footer><div class="wrap">
<p><strong style="color:#fff">GameVault</strong> — a demo games catalog. All catalog games are original demo listings created for this site; no files are hosted here and nothing is for sale. No pricing is shown anywhere on this site.</p>
<p>Catalog data is crawled from the public <a href="https://f95zone.to.it/">f95zone.to.it</a> homepage and post pages by crawl/crawl.py (see <a href="/frightening-skull/crawl/crawl-2026-10-30.html">crawl log</a> and data/crawled.json). Images are hotlinked from the source posts, mirror links come from the post HTML, no files are hosted here and nothing is for sale. No pricing is shown anywhere on this site.</p>
<p><a href="/frightening-skull/sitemap.html">Sitemap</a> · <a href="/frightening-skull/robots.txt">robots.txt</a></p>
</div></footer>
</body>
</html>"""

def card(g, show_overview=True):
    ov = f'<p class="ov">{esc(g["overview"])}</p>' if show_overview else ""
    return f"""<article class="card" data-title="{esc(g['title'])}" data-dev="{esc(g['developer'])}" data-genres="{'|'.join(g['genres'])}" data-status="{esc(g['status'])}" data-engine="{esc(g['engine'])}" data-rating="{g['rating']}" data-updated="{g['updated']}">
<a href="/frightening-skull/games/{g['slug']}.html">{cover_thumb(g)}</a>
<div class="body"><h3><a href="/frightening-skull/games/{g['slug']}.html">{esc(g['title'])} [{esc(g['version'])}] [{esc(g['developer'])}]</a></h3>
<p class="meta">{(stars(g['rating']) + f" {g['rating']} \u00b7 {g['reviews']} reviews") if g['reviews'] else "No rating yet"} · Updated {g['updated']} · <span class="badge {status_class(g['status'])}">{esc(g['status'])}</span></p>
{ov}
<div class="chips">{''.join(f'<a class="chip" href="/frightening-skull/tags/{tag_slug(t)}.html">{esc(t)}</a>' for t in g['genres'])}</div>
</div></article>"""

def write(path, content):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def related(g):
    out = []
    for o in GAMES:
        if o["slug"] == g["slug"]:
            continue
        shared = len(set(o["genres"]) & set(g["genres"]))
        if shared:
            out.append((shared, o))
    out.sort(key=lambda x: (-x[0], -x[1]["rating"]))
    return [o for _, o in out[:4]]

def game_page(g):
    ld = {
        "@context": "https://schema.org", "@type": "VideoGame",
        "name": g["title"], "author": {"@type": "Organization", "name": g["developer"]},
        "applicationCategory": "Game",
        "operatingSystem": g["os"], "inLanguage": "en",
        "genre": g["genres"],
        "url": f"{SITE}/games/{g['slug']}.html",
    }
    if g["release"] != "\u2014":
        ld["datePublished"] = g["release"]
    if g["reviews"]:
        ld["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": g["rating"], "reviewCount": g["reviews"]}
    desc = f"{g['title']} [{g['version']}] by {g['developer']} — {g['status']} {', '.join(g['genres'])} game. {g['overview']}"
    rel = related(g)
    changelog = "".join(
        f"<h3>{esc(v)}</h3><ul>{''.join(f'<li>{esc(n)}</li>' for n in notes)}</ul>"
        for v, notes in g["changelog"])
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in g["faq"])
    revs = "".join(
        f"<div class=\"review\"><strong>{esc(a)}</strong> · {stars(r)} {r}/5<p>{esc(t)}</p></div>"
        for a, r, t in g["reviews_list"])
    mirrors = mirrors_html(g)
    has_real = any(e.get("url") for entries in (g.get("mirrors") or {}).values() for e in entries)
    dev_links = (' \u00b7 ' + ' \u2013 '.join(f'<a href="{esc(u)}" target="_blank" rel="nofollow noopener">{esc(l)}</a>' for l, u in g["developer_links"]) if g.get("developer_links") else "")
    ver_cell = esc(g["version_full"]) if g.get("version_full") else esc(g["version"])
    install_block = ""
    if g.get("installation"):
        install_block = ('<h2>Installation</h2>\n<details><summary>See more</summary><ol>' +
            "".join(f"<li>{esc(step)}</li>" for step in g["installation"]) + "</ol></details>")
    cover_large = ('<div class="post_top_format"><div class="fn__image_format"><img src="' + esc(g["cover_url"]) + '" alt="' + esc(g["title"]) + ' [' + esc(g["version"]) + '] [' + esc(g["developer"]) + ']"></div></div>'
                   if g.get("cover_url") else
                   '<img class="coverlarge" src="/frightening-skull/assets/covers/' + g["slug"] + '.svg" alt="' + esc(g["title"]) + ' \u2014 placeholder cover art">')
    listing_note = ("Real catalog entry from the source post \u2014 no files are hosted here and nothing is for sale. No pricing is shown on this site."
                    if g.get("source_url") else
                    "Demo listing \u2014 no files are hosted here and nothing is for sale. No pricing is shown on this site.")
    source_note = ('<p class="lede">Source: <a href="' + esc(g["source_url"]) + '">f95zone.to.it post</a> \u2014 details and images hotlinked from the source post, not hosted here.</p>'
                   if g.get("source_url") else "")
    censored_row = ('<tr><td>Censored</td><td>' + esc(g["censored"]) + '</td></tr>' if g.get("censored") else "")
    if g.get("screenshots"):
        shots_block = ('<h2>Screenshots</h2>\n<p class="lede">Screenshots hotlinked from the source post \u2014 not hosted here.</p>\n<div class="shots">\n' +
            "".join('<figure><img src="' + esc(u) + '" alt="' + esc(g["title"]) + ' \u2014 screenshot ' + str(i + 1) + '" loading="lazy"><figcaption>Screenshot ' + str(i + 1) + ' \u2014 hotlinked from source</figcaption></figure>' for i, u in enumerate(g["screenshots"])) + "\n</div>")
    else:
        shots_block = ('<h2>Screenshots</h2>\n<p class="lede">Placeholder screenshots \u2014 generated cover art, not game screenshots. No images were copied from f95zone.to.it.</p>\n<div class="shots">\n' +
            '<figure><img src="/frightening-skull/assets/covers/' + g["slug"] + '-shot1.svg" alt="' + esc(g["title"]) + ' \u2014 placeholder screenshot 1"><figcaption>Screenshot 1 \u2014 placeholder</figcaption></figure>' +
            '<figure><img src="/frightening-skull/assets/covers/' + g["slug"] + '-shot2.svg" alt="' + esc(g["title"]) + ' \u2014 placeholder screenshot 2"><figcaption>Screenshot 2 \u2014 placeholder</figcaption></figure>' + "\n</div>")
    body = f"""
<main><div class="wrap">
<p class="breadcrumb"><a href="/frightening-skull/">Home</a> / <a href="/frightening-skull/browse.html">Games</a> / {esc(g['title'])}</p>
<h1>{esc(g['title'])} [{esc(g['version'])}] [{esc(g['developer'])}]</h1>
<p class="meta">{(stars(g['rating']) + f" {g['rating']} \u00b7 {g['reviews']} reviews") if g['reviews'] else "No rating yet"} · Thread Updated {g['updated']} · <span class="badge {status_class(g['status'])}">{esc(g['status'])}</span> · {esc(g['engine'])}</p>
{cover_large}
<p>{esc(g['overview'])}</p>
<p>{''.join(f'<span class="osbadge">{esc(o.strip())}</span>' for o in g['os'].split(','))}</p>
<div class="chips">{''.join(f'<a class="chip" href="/frightening-skull/tags/{tag_slug(t)}.html">{esc(t)}</a>' for t in g['genres'])}</div>
<div class="note">{listing_note}</div>
{source_note}
<h2>About this game</h2>
<table class="info">
<tr><td>Developer</td><td>{esc(g['developer'])}{dev_links}</td></tr>
<tr><td>Version</td><td>{ver_cell}</td></tr>
<tr><td>Status</td><td>{esc(g['status'])}</td></tr>
<tr><td>Engine</td><td>{esc(g['engine'])}</td></tr>
<tr><td>OS</td><td>{esc(g['os'])}</td></tr>
<tr><td>Language</td><td>{esc(g['language'])}</td></tr>
{censored_row}
<tr><td>Release date</td><td>{esc(g['release'])}</td></tr>
<tr><td>Thread Updated</td><td>{esc(g['updated'])}</td></tr>
<tr><td>File size</td><td>{esc(g.get('size', '—'))}{" (demo metadata)" if not g.get("source_url") else ""}</td></tr>
<tr><td>Format</td><td>{esc(g.get('format', '—'))}</td></tr>
<tr><td>Genre / Tags</td><td>{esc(', '.join(g['genres']))}</td></tr>
</table>
{shots_block}
<h2>Download</h2>
<div class="dl">
<p><strong>Download — external mirror links.</strong> No files are hosted here. Each button below takes you to another website. {"Mirror links below were taken from the source post." if has_real else "Mirror links are not set yet — fill each link from the post."}</p>
<table class="info">
<tr><td>Version</td><td>{esc(g['version'])}</td></tr>
<tr><td>File size</td><td>{esc(g.get('size', '—'))}</td></tr>
<tr><td>Format</td><td>{esc(g.get('format', '—'))}</td></tr>
</table>
{mirrors}
<p class="lede">{"Mirror links are external, taken from the source post. No files are stored on GitHub Pages, and no mirror URLs have been invented." if has_real else "Mirror links are external. No files are stored on GitHub Pages, and no mirror URLs have been invented — each link field is to be filled from the post."}</p>
</div>
{install_block}
<h2>Changelog</h2>
{changelog}
<h2>FAQ</h2>
{faq}
<h2>Customer reviews</h2>
<p class="lede">{esc("Demo reviews for this demo listing." if g["reviews_list"] else "No reviews yet — the source post lists no reviews.")}</p>
{revs}
<h2>More like this</h2>
<div class="grid">{''.join(card(o, show_overview=False) for o in rel)}</div>
</div></main>"""
    return head(f"{g['title']} [{g['version']}] [{g['developer']}] — GameVault", desc, f"/games/{g['slug']}.html", ld) + HEADER + body + FOOTER

def tag_page(t):
    games = [g for g in GAMES if t in g["genres"]]
    n = len(games)
    desc = f"Browse {n} {t} game{'s' if n != 1 else ''} on GameVault — {', '.join(g['title'] for g in games)}."
    body = f"""
<main><div class="wrap">
<p class="breadcrumb"><a href="/frightening-skull/">Home</a> / <a href="/frightening-skull/browse.html">Tags</a> / {esc(t)}</p>
<h1>{esc(t)} — {n} game{'s' if n != 1 else ''}</h1>
<p class="lede">All {esc(t)} games in the catalog. Tags work like the F95 post tags: pick one to filter the whole catalog.</p>
<div class="grid">{''.join(card(g) for g in games)}</div>
<h2>All tags</h2>
<div class="chips">{''.join(f'<a class="chip" href="/frightening-skull/tags/{tag_slug(x)}.html">{esc(x)}</a>' for x in ALL_TAGS)}</div>
</div></main>"""
    return head(f"{t} Games — GameVault", desc, f"/tags/{tag_slug(t)}.html") + HEADER + body + FOOTER

def index_page():
    featured = [GAMES[0], GAMES[1], GAMES[3]]
    slides = "".join(
        f"""<div class="slide{' active' if i == 0 else ''}"><div class="kicker">Featured &amp; Recommended</div><h2>{esc(g['title'])} [{esc(g['version'])}]</h2><p>{esc(g['overview'])}</p><p>{stars(g['rating'])} {g['rating']} · {g['reviews']} reviews · {esc(g['status'])}</p><a class="cta" href="/frightening-skull/games/{g['slug']}.html">View game</a></div>"""
        for i, g in enumerate(featured))
    dots = "".join(f"<button aria-label=\"Slide {i+1}\" class=\"{'on' if i==0 else ''}\"></button>" for i in range(len(featured)))
    latest = sorted(GAMES, key=lambda g: g["updated"], reverse=True)[:6]
    trending = sorted(GAMES, key=lambda g: g["reviews"], reverse=True)[:4]
    top = sorted(GAMES, key=lambda g: g["rating"], reverse=True)[:5]
    completed = [g for g in GAMES if g["status"] == "Completed"]
    genre_tiles = "".join(
        f"""<a class="tile" href="/frightening-skull/tags/{tag_slug(t)}.html"><b>{esc(t)}</b><span>{sum(1 for g in GAMES if t in g['genres'])} game{'s' if sum(1 for g in GAMES if t in g['genres']) != 1 else ''}</span></a>"""
        for t in ALL_TAGS)
    tag_cloud = "".join(f'<a class="chip" href="/frightening-skull/tags/{tag_slug(t)}.html">{esc(t)}</a>' for t in ALL_TAGS)
    crawled_games = [g for g in GAMES if g.get("source_url")]
    crawled = "".join(
        f"<li><strong><a href=\"/frightening-skull/games/{esc(c['slug'])}.html\">{esc(c['title'])} [{esc(c['version'])}] [{esc(c['developer'])}]</a></strong> — updated {c['updated']}" +
        (f" — tags: {esc(', '.join(c['genres']))}" if c["genres"] else "") + "</li>"
        for c in crawled_games)
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "GameVault",
          "url": SITE + "/",
          "potentialAction": {"@type": "SearchAction", "target": SITE + "/browse.html?q={search_term_string}", "query-input": "required name=search_term_string"}}
    body = f"""
<main><div class="wrap">
<h1>GameVault — Games Catalog</h1>
<p class="lede">Browse {len(GAMES)} games by genre and tag — 2DCG, 3DCG, Adventure, AI CG and more. Windows and Android, plus Linux/Mac where listed. No pricing, no cart: a catalog, F95-style.</p>
<div class="hero">{slides}</div>
<div class="dots">{dots}<button id="prev" aria-label="Previous">‹</button><button id="next" aria-label="Next">›</button></div>
<h2>Latest Updates</h2>
<div class="grid">{''.join(card(g) for g in latest)}</div>
<h2>Trending Now</h2>
<div class="rows">{''.join(f'<div class="row"><span class="rank">#{i+1}</span><span class="t"><b><a href="/frightening-skull/games/{g["slug"]}.html">{esc(g["title"])}</a></b> · {esc(g["developer"])} · {g["reviews"]} reviews</span><span>{stars(g["rating"])} {g["rating"]}</span></div>' for i, g in enumerate(trending))}</div>
<h2>Top Rated</h2>
<div class="rows">{''.join(f'<div class="row"><span class="rank">#{i+1}</span><span class="t"><b><a href="/frightening-skull/games/{g["slug"]}.html">{esc(g["title"])}</a></b> · {esc(g["developer"])}</span><span>{stars(g["rating"])} {g["rating"]}</span></div>' for i, g in enumerate(top))}</div>
<h2>Browse by Genre</h2>
<div class="tiles">{genre_tiles}</div>
<h2>Completed Games</h2>
<div class="grid">{''.join(card(g) for g in completed)}</div>
<h2>Popular Tags</h2>
<div class="chips">{tag_cloud}</div>
<h2>Crawled from f95zone.to.it — full catalog entries</h2>
<p class="lede">Fetched by crawl/crawl.py from the public f95zone.to.it homepage (page 1, first 11 titles) and each post page. Each one is a full catalog entry above, with details, hotlinked images and mirror links from its source post. Raw crawl output: data/crawled.json; run log: crawl/crawl-&lt;date&gt;.md. No files are hosted here.</p>
<ul class="crawl">{crawled}</ul>
</div></main>
<script>{JS_CAROUSEL}</script>"""
    return head("GameVault — Games Catalog | 2DCG, Adventure, AI CG Games", "GameVault is a demo games catalog: browse games by genre and tag — 2DCG, Adventure, AI CG, RPG, Roguelike and more. No pricing, no downloads hosted.", "/", ld) + HEADER + body + FOOTER

def browse_page():
    genre_boxes = "".join(
        f"<label><input type=\"checkbox\" data-genre=\"{esc(t)}\"> {esc(t)} ({sum(1 for g in GAMES if t in g['genres'])})</label>"
        for t in ALL_TAGS)
    status_boxes = "".join(
        f"<label><input type=\"checkbox\" data-status=\"{esc(s)}\"> {esc(s)}</label>"
        for s in ["Ongoing", "Completed", "On Hold"])
    engine_boxes = "".join(
        f"<label><input type=\"checkbox\" data-engine=\"{esc(e)}\"> {esc(e)}</label>"
        for e in sorted({g["engine"] for g in GAMES}))
    body = f"""
<main><div class="wrap">
<p class="breadcrumb"><a href="/frightening-skull/">Home</a> / Browse</p>
<h1>Browse All Games</h1>
<p class="lede"><span id="count">{len(GAMES)} games</span> · filter by genre, status, engine or rating. Search is live as you type.</p>
<div class="filters">
<fieldset><legend>Genre / Tag</legend>{genre_boxes}</fieldset>
<fieldset><legend>Status</legend>{status_boxes}</fieldset>
<fieldset><legend>Engine</legend>{engine_boxes}</fieldset>
<fieldset><legend>Minimum rating</legend><select id="minrating"><option value="0">Any</option><option value="4">4.0+</option><option value="4.5">4.5+</option></select></fieldset>
<fieldset><legend>Sort</legend><select id="sort"><option value="rating">Top rated</option><option value="newest">Newest updated</option><option value="title">Title A–Z</option></select></fieldset>
<fieldset><legend>Search</legend><input id="q" type="search" placeholder="Search title or developer" style="background:#316282;border:1px solid #000;color:#fff;padding:7px 10px"></fieldset>
</div>
<div class="grid" id="grid">{''.join(card(g) for g in GAMES)}</div>
</div></main>
<script>{JS_BROWSE}</script>"""
    return head("Browse All Games — GameVault", "Browse every game in the GameVault catalog. Filter by genre and tag — 2DCG, Adventure, AI CG, RPG, Roguelike — by status, engine or rating.", "/browse.html") + HEADER + body + FOOTER

def sitemap_page():
    links = ["/", "/browse.html"] + [f"/games/{g['slug']}.html" for g in GAMES] + [f"/tags/{tag_slug(t)}.html" for t in ALL_TAGS]
    rows = "".join(f'<li><a href="/frightening-skull{p}">{SITE}{p}</a></li>' for p in links)
    body = f"""
<main><div class="wrap">
<h1>Sitemap</h1>
<p class="lede">Every page in the GameVault catalog — {len(links)} pages. A machine-readable sitemap.xml is also available.</p>
<ul>{rows}</ul>
<h2>sitemap.xml preview</h2>
<p class="lede">Served at <a href="/frightening-skull/sitemap.xml">/sitemap.xml</a>.</p>
</div></main>"""
    return head("Sitemap — GameVault", "Full sitemap of the GameVault games catalog: home, browse, every game page and every genre tag page.", "/sitemap.html") + HEADER + body + FOOTER

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="output directory (default: ~/workspace/frightening-skull)")
    args = ap.parse_args()
    global OUT, GAMES, ALL_TAGS
    if args.out:
        OUT = Path(args.out).resolve()
    GAMES = load_games()
    ALL_TAGS = sorted({t for g in GAMES for t in g["genres"]}, key=str.lower)
    import shutil
    for d in ("assets", "games", "tags"):
        if (OUT / d).exists():
            shutil.rmtree(OUT / d)
    for f in ("index.html", "browse.html", "sitemap.html", "sitemap.xml", "robots.txt", "README.md"):
        fp = OUT / f
        if fp.exists():
            fp.unlink()
    for f in ("crawl/crawl-2026-10-30.md", "crawl/crawl-2026-10-30.html"):
        fp = OUT / f
        if fp.exists():
            fp.unlink()
    if (OUT / "data" / "games.json").exists():
        (OUT / "data" / "games.json").unlink()
    (OUT / "assets").mkdir(parents=True)
    (OUT / "assets" / "covers").mkdir(parents=True)
    for g in GAMES:
        if g.get("cover_url"):
            continue  # real cover is hotlinked; no placeholder SVG for this game
        (OUT / "assets" / "covers" / f"{g['slug']}.svg").write_text(cover_svg(g['title'], g['slug'], "Placeholder cover art"), encoding="utf-8")
        (OUT / "assets" / "covers" / f"{g['slug']}-shot1.svg").write_text(cover_svg(g['title'], g['slug'], "Placeholder screenshot 1"), encoding="utf-8")
        (OUT / "assets" / "covers" / f"{g['slug']}-shot2.svg").write_text(cover_svg(g['title'], g['slug'], "Placeholder screenshot 2"), encoding="utf-8")
    (OUT / "games").mkdir(parents=True)
    (OUT / "tags").mkdir(parents=True)
    (OUT / "crawl").mkdir(parents=True, exist_ok=True)
    write("assets/style.css", CSS)
    write("assets/app.js", JS_BROWSE)
    write("index.html", index_page())
    write("browse.html", browse_page())
    write("sitemap.html", sitemap_page())
    for g in GAMES:
        write(f"games/{g['slug']}.html", game_page(g))
    for t in ALL_TAGS:
        write(f"tags/{tag_slug(t)}.html", tag_page(t))
    # games.json data file
    write("data/games.json", json.dumps([full_record(g) for g in GAMES], indent=2))
    # sitemap.xml
    urls = ["/", "/browse.html", "/sitemap.html"] + [f"/games/{g['slug']}.html" for g in GAMES] + [f"/tags/{tag_slug(t)}.html" for t in ALL_TAGS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f'  <url><loc>{SITE}{u}</loc><lastmod>2026-10-30</lastmod></url>\n' for u in urls) + "</urlset>\n"
    write("sitemap.xml", sm)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: https://nabeelshar.github.io/frightening-skull/sitemap.xml\n")
    write("README.md", """# GameVault — Games Catalog (GitHub Pages static mirror)

Static mirror of the GameVault games catalog (artifact `f95zone-clone`).
Steam-style dark-blue storefront, **no pricing, no cart, no discount badges**.
Game posts are F95-style: title [version] [developer], date, short overview,
and genre/tags (2DCG, 3DCG, 2D Game, 3D Game, Adventure, AI CG, Animated, Comedy,
Dating Sim, Drama, Fantasy, Female Protagonist, Harem, Horror, Male Protagonist,
Management, Multiple Endings, Romance, RPG, Sandbox, Sci-Fi, Simulation, Strategy,
Turn Based Combat, Visual Novel).

Each game page has a full info block (Thread Updated, Release Date, Developer,
Version, OS — Windows and Android plus Linux/Mac where listed — Language, Engine,
Status, Rating, Genre line, overview, changelog, placeholder screenshots) and a
Download section with external mirror links, F95-style: per OS
(Windows / Android / Linux / Mac where listed) — MEGA, GOFILE, PIXELDRAIN,
DATANODES, WORKUPLOAD — each host a separate external link button. No files
are hosted here and no mirror URLs are invented; each link field is to be
filled from the post.
Cover art for demo games is generated placeholder SVG (gradient + title initials) in assets/covers/. Real entries use the cover hotlinked from their source post.

## What is in here

- `index.html` — catalog home: featured carousel, Latest Updates, Trending, Top Rated, Browse by Genre, Popular Tags
- `browse.html` — all games with live search + genre/status/engine/rating filters
- `games/*.html` — one SEO page per game (unique title/meta, VideoGame JSON-LD, breadcrumb, info table, changelog, FAQ, reviews, related games)
- `tags/*.html` — one page per genre/tag
- `sitemap.xml`, `robots.txt`, `sitemap.html`
- `data/games.json` — the catalog data

## Demo data vs crawled metadata

 - The 8 catalog games are **original demo listings** written for this site
  (Starfall Academy, Kingdom of Ashes, Neon Horizon, Echoes of Tomorrow,
  Emberfall Chronicles, Voidrunner Protocol, Lanterns of the Deep, Ashenvale Pact).
- Real entries: added by **crawl/crawl.py** from f95zone.to.it post pages
  (see `data/crawled.json` for the raw crawl output). The first is
  **Pinked And Owned [v0.5] [PinkedAndOwned]**
  (https://f95zone.to.it/pinked-and-owned-v0-2-4-1-pinkedandowned/).
  The crawler fetches title/version/developer/dates/OS/size clues/genre,
  overview, changelog, cover + gallery image URLs (hotlinked only) and
  download mirror host names + hrefs per OS from the post HTML. No files
  are hosted, no mirror URLs are invented.
- The "Crawled from f95zone.to.it" list on the home page is built from the
  catalog entries added by the crawler (first 11 titles on the homepage
  page 1, with the Pinked and Owned seed as the 11th). See `data/crawled.json`.
- No files are hosted here and nothing is for sale. Download sections link
  out to external mirrors listed on the source posts; no mirror URL is invented.

## Live site

https://nabeelshar.github.io/frightening-skull/
""")
    write("crawl/crawl-2026-10-30.md", """# Crawl log — f95zone.to.it — 2026-10-30

Superseded 2026-10-30: the catalog is now built by the automated crawler
crawl/crawl.py (MAX_PAGES=1, MAX_POSTS=11 — first 11 titles on homepage page 1,
with the Pinked and Owned seed as the 11th). Live entries are full catalog
entries — see data/crawled.json and the crawl/crawl-YYYY-MM-DD.md run logs.
The notes below record the earlier manual check.

Method: public homepage fetch of https://f95zone.to.it/ via the text reader
(homepage listing, ~20 posts, dated 29–30 Oct 2026), plus 2 post pages opened
from that listing to read their Genre fields. No login, no Cloudflare bypass,
no scraping of f95zone.to (the login-gated XenForo site).

## Posts examined

- Homepage listing: 20 posts scanned (titles + dates only).
- Detail pages opened (2): Chance Encounter, Forbidden Dungeon — Genre field only.

## Metadata kept (title, version, developer, date, non-explicit tags)

| Title | Version | Developer | Updated | Non-explicit tags kept |
|---|---|---|---|---|
| BangMon | v0.2.1 | BangDevMon | 2026-10-30 | — |
| Chance Encounter | v0.2.5 | Sorrow | 2026-10-29 | 3DCG, Animated, Transformation |
| Forbidden Dungeon | v0.5 | Dark Forge Studios | 2026-10-29 | 2DCG, Roguelike, AI CG, Fantasy, RPG, Turn Based Combat |
| House Rules | v1.0 Demo | Pink Lace Games | 2026-10-30 | — |
| 8 Weeks | v0.3.1 | FromPlutoGuy | 2026-10-29 | — |
| ARMS | 0.03 TL1 | Kiwi Berry | 2026-10-29 | 2D Game, 2DCG, Japanese Game, Female Protagonist |
| The World After Silence | v0.7 | Silent Shelter Games | 2026-10-29 | — |

Tag check result: **2DCG** and **AI CG** both appear in the site's genre lists
(Forbidden Dungeon), **3DCG** appears too (Chance Encounter). "Adventure" is
used as a catalog genre on this site as requested by the owner.

## Real catalog entry from a post page

- **Pinked And Owned [v0.5] [PinkedAndOwned]** — source:
  https://f95zone.to.it/pinked-and-owned-v0-2-4-1-pinkedandowned/ — version
  v0.5 WIRED, updated 2026-10-16, developer PinkedAndOwned, OS Windows /
  Android / Linux / Mac (Windows desktop client, Android app, Linux via Wine,
  browser/HTML version), size approx. ~300 MB (artwork bundle, per changelog
  clues), category HTML/browser narrative sandbox (genres Adventure, Sandbox,
  Simulation, Visual Novel, HTML). Overview is a short paraphrase; no
  description, images, changelog text or download/mirror links were copied.

## Deliberately NOT copied

- No post descriptions/overviews copied verbatim (several are explicit).
- No changelogs, developer notes, or installation instructions copied.
- No images downloaded or hotlinked.
- No download links of any kind.
- No explicit sexual genre tags reproduced (the genre lists on those pages also
  contain explicit tags — those were left out entirely).
- Titles with explicit wording were excluded from the site's "Spotted" list.

## Use of this data

Only to confirm the tag structure (2DCG / Adventure / AI CG / 3DCG / RPG /
Roguelike / Fantasy) used by the catalog. The catalog games themselves are
original demo listings, not these posts.
""")
    write("crawl/crawl-2026-10-30.html", head("Crawl log — f95zone.to.it — 2026-10-30 — GameVault", "Crawl log for the f95zone.to.it metadata check on 2026-10-30: method, posts examined, and what was deliberately not copied.", "/crawl/crawl-2026-10-30.html") + HEADER + """
<main><div class="wrap">
<h1>Crawl log — f95zone.to.it — 2026-10-30</h1>
<p class="lede"><strong>Superseded 2026-10-30:</strong> the catalog is now built by the automated crawler crawl/crawl.py (MAX_PAGES=1, MAX_POSTS=11). Live entries are full catalog entries — see data/crawled.json and the crawl/crawl-YYYY-MM-DD.md run logs. The notes below record the earlier manual check.</p>
<p class="lede">Method: public homepage fetch of the f95zone.to.it homepage listing (~20 posts, 29–30 Oct 2026), plus 2 post pages opened from that listing to read their Genre fields. No login, no Cloudflare bypass, no scraping of f95zone.to (the login-gated XenForo site).</p>
<h2>Metadata kept</h2>
<ul class="crawl">
<li><strong>BangMon [v0.2.1] [BangDevMon]</strong> — 2026-10-30</li>
<li><strong>Chance Encounter [v0.2.5] [Sorrow]</strong> — 2026-10-29 — tags: 3DCG, Animated, Transformation</li>
<li><strong>Forbidden Dungeon [v0.5] [Dark Forge Studios]</strong> — 2026-10-29 — tags: 2DCG, Roguelike, AI CG, Fantasy, RPG, Turn Based Combat</li>
<li><strong>House Rules [v1.0 Demo] [Pink Lace Games]</strong> — 2026-10-30</li>
<li><strong>8 Weeks [v0.3.1] [FromPlutoGuy]</strong> — 2026-10-29</li>
<li><strong>ARMS [0.03 TL1] [Kiwi Berry]</strong> — 2026-10-29 — tags: 2D Game, 2DCG, Japanese Game, Female Protagonist</li>
<li><strong>The World After Silence [v0.7] [Silent Shelter Games]</strong> — 2026-10-29</li>
</ul>
<h2>Deliberately NOT copied</h2>
<ul>
<li>No post descriptions or overviews copied verbatim.</li>
<li>No changelogs, developer notes, or installation instructions copied.</li>
<li>No images downloaded or hotlinked.</li>
<li>No download links of any kind.</li>
<li>No explicit sexual genre tags reproduced.</li>
<li>Titles with explicit wording were excluded from the site's "Spotted" list.</li>
</ul>
<p>Tag check result: <strong>2DCG</strong> and <strong>AI CG</strong> both appear in that site's genre lists (Forbidden Dungeon), and <strong>3DCG</strong> appears too (Chance Encounter).</p>
<h2>Real catalog entry from a post page</h2>
<ul class="crawl">
<li><strong>Pinked And Owned [v0.5] [PinkedAndOwned]</strong> — source: https://f95zone.to.it/pinked-and-owned-v0-2-4-1-pinkedandowned/ — version v0.5 WIRED, updated 2026-10-16, developer PinkedAndOwned, OS Windows / Android / Linux / Mac, size approx. ~300 MB (artwork bundle), category HTML/browser narrative sandbox (Adventure, Sandbox, Simulation, Visual Novel, HTML). Overview is a short paraphrase; no description, images, changelog text or download/mirror links were copied.</li>
</ul>
</div></main>""" + FOOTER)
    print("generated", len(list(OUT.rglob("*"))), "entries")

if __name__ == "__main__":
    main()
