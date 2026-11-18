# lootandwaifus.com Sword x Staff section: notes

<!-- index: What lootandwaifus.com had on Sword x Staff and why none of it could be read on 2026-11-18 -->

> **Summary:** The Sword x Staff section of lootandwaifus.com was gone on 2026-11-18: every page tried answered 404 and the sitemap no longer lists the game. No fact was taken from this site. The relic and ingredient tables we hoped to get here were built from eog.gg instead, without drop chances.
> **Applies:** all seasons
> **Related:** [eog notes](eog.md), [official site notes](official-site.md), [Source register](../README.md)

## What was checked

- robots.txt allows all crawlers; Content-Signal is `search=yes, ai-train=no, use=reference`. Reference use is allowed, so reading was permitted. [S-86]
- The Sword x Staff hub, relic database, ingredient database, interactive map, codes page and the API description page all answered 404. A few likely JSON paths under `/api` also answered 404. [S-86]
- `sitemap-0.xml` lists 636 URLs for four other games (NIKKE, Trickcal, MAke Drama, Whisperborne) and none for Sword x Staff. The site's API page does not mention the game either. [S-86]
- The mirror host lootandwaifus.pages.dev was refused by our network proxy (403). Per the brief it was skipped, not worked around. Earlier agents read two guides there and registered them as S-30 and S-31.
- Raw copies of what did answer (sitemaps, home page, API page) are in `knowledge/sources/raw/lootandwaifus/` (gitignored).

## What is missing because of this

- ❓ Relic drop chance per relic and per place. `relic-database.json` has every relic from eog [S-85] but no chances.
- ❓ Ingredient drop sources and chances. `ingredients.json` lists ingredients taken from eog recipes [S-85]; `drop_sources` and `drop_chance` are null.
- ❓ The site's own map markers and code list. eog map data covers markers (`map-points.json`) [S-85].

## Open questions

- ❓ Whether the section moved to another address or was withdrawn. A later check of the sitemap would tell.
- ❓ Whether the register entry S-71 (same site, read earlier through WebFetch, "API page only") saw the section alive; if so the removal happened on or before 2026-11-18.

## Sources

- [S-86] lootandwaifus.com, checked 2026-11-18: robots.txt, sitemap index, sitemap-0.xml, home page, API page; Sword x Staff URLs returned 404. Not yet in the register; row proposed to the lead.
- [S-85] eog.gg, see [eog.md](eog.md).
