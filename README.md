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
