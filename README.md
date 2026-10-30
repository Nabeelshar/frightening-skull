# GameVault — Games Catalog (GitHub Pages static mirror)

Static mirror of the GameVault games catalog (artifact `f95zone-clone`).
Steam-style dark-blue storefront, **no pricing, no cart, no discount badges**.
Game posts are F95-style: title [version] [developer], date, short overview,
and genre/tags (2DCG, Adventure, AI CG, 3DCG, RPG, Roguelike, Fantasy, Sci-Fi,
Visual Novel, Horror, Turn Based Combat).

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
