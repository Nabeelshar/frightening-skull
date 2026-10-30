# GameVault — Games Catalog (GitHub Pages static mirror)

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
Demo Download section (OS badges, version, file size as demo metadata, format).
No game files are hosted here: GitHub blocks single files over 100 MB and
recommends repos / Pages sites under 1 GB, and most games are hundreds of MB to
several GB. The download link field is a placeholder for the owner's own link.
Cover art is generated placeholder SVG (gradient + title initials) in assets/covers/.

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
- The "Spotted on f95zone.to.it" list on the home page is **metadata only**
  (title, version, developer, date, non-explicit genre tags), spotted on the
  public https://f95zone.to.it/ homepage on 2026-10-30. See `crawl/crawl-2026-10-30.md`.
- No files are hosted here, nothing is for sale, and no download links exist
  anywhere on this site.

## Live site

https://nabeelshar.github.io/frightening-skull/
