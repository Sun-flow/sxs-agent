# Research notes: where Sword x Staff information comes from, and how to keep getting it

<!-- index: Read before adding a source, fetching a site, or looking for facts about future seasons: survey of every public source, fetch recipes, hosts to allow -->

> **Summary:** Sword x Staff (global, package `com.zjcs.android.us`) is the Western release of the Chinese game
> 杖剑传说 ("Zhang Jian Chuan Shuo", G-bits; mainland launch 2025-05-29), which also runs in Japan as 杖と剣の伝説
> since 2025-07-15 [S-66][S-67]. Those older versions are about a year and four class tiers ahead of global, and
> their community sites (TapTap CN, BWIKI, Gamerch) are the best source for future seasons, tiers and kingdoms.
> For the global game today the useful English sources are Prydwen, eog.gg, zeroluck.gg and Loot & Waifus (player
> sites with tools), the Fandom wiki (frozen since 2026-05-30) and YouTube creators; the SEO sites are noise.
> **Applies:** all seasons
> **Related:** [CONVENTIONS](../CONVENTIONS.md), `scripts/kb_fetch.py`, [seasons](../systems/seasons.md), [codes](../systems/codes.md), [world and kingdoms](../systems/world-and-kingdoms.md)

Research done 2026-11-18 from the cloud session. Non-ASCII game titles are kept on purpose: they are the search keys.

## How this was checked

- `curl` from this session reaches only two game hosts: `swordxstaff.fandom.com` (`api.php` only) and
  `www.sword-x-staff.wiki`. `www.reddit.com/robots.txt` also answered. Every other host below returned
  **CONNECT 403 from our network proxy** (policy denial) and was not retried: `www.prydwen.gg`,
  `sword-x-staff-wiki.pages.dev`, `zeroluck.gg`, `eog.gg`, `www.bluestacks.com`, `swordxstaff.ltgamesglobal.com`,
  `www.pocketgamer.com`, `www.pockettactics.com`, `progameguides.com`, `play.google.com`, `apps.apple.com`,
  `www.taptap.io`, `apps.qoo-app.com`, `www.ldplayer.net`, `www.mumuplayer.com`, `www.youtube.com`.
- Pages on blocked hosts were read through the WebFetch tool (a separate service that returns a summary of the
  page) or only through search-result titles. Recipes for those hosts are therefore **untested with curl**.
- The WebFetch budget (100 calls an hour, shared by all agents) ran out near the end. Not read: Gamepedia JP,
  Loot & Waifus hub and map pages (site error), topuplist.com, the BWIKI copyright page, Google Play, TapTap
  global, QooApp, Reddit, Discord, X, Facebook, YouTube pages (titles only).
- `www.prydwen.gg` shows a bot check: only search-result titles and URLs are used, nothing was fetched.

## Source tags used on this page

| Tag | Source | Tier | How it was read |
|---|---|---|---|
| S-60 | Fandom MediaWiki API metadata (revision history, statistics, licence) | C | curl, 2026-11-18 |
| S-61 | Official site swordxstaff.boltray.com / swordxstaff.ltgamesglobal.com | official (rank with B for facts it states) | WebFetch |
| S-62 | App Store listing, app id 6751270546 | official | WebFetch |
| S-63 | TapTap CN strategy hub for 杖剑传说, app 717836 | B for the CN version; C when applied to global | WebFetch |
| S-64 | BWIKI wiki.biligame.com/zjcswiki | C (CN version) | WebFetch, home page only |
| S-65 | Gamerch JP wiki gamerch.com/sceptersword | C (JP version) | WebFetch, one page |
| S-66 | 4Gamer game page G091380 | press | WebFetch |
| S-67 | baijing.cn article 56139 (2026-07-27), industry news | press | WebFetch |
| S-68 | 17173.com article 2026-05-07, reposted fan guide | C (CN version) | WebFetch |
| S-69 | eog.gg/games/sword-x-staff | C | WebFetch |
| S-70 | zeroluck.gg/sword-x-staff | C | WebFetch, index only |
| S-71 | lootandwaifus.com Sword x Staff pages | C | WebFetch, API page only |
| S-72 | sword-x-staff-wiki.pages.dev | D | WebFetch, one page |
| S-73 | pockettactics.com/sword-x-staff/codes | C for codes | WebFetch |
| S-74 | pocketgamer.com Sword x Staff pages | D (sponsored) | WebFetch |
| S-75 | invenglobal.com Korean launch news | press | WebFetch |
| S-76 | bluestacks.com blog | D | WebFetch |
| S-77 | YouTube videos | B or C per creator | search-result titles only |
| S-78 | Other SEO guide sites (topuplist, allthings.how, narcosis-the-game, allclash, oslink, mobi.gg...) | D | search-result titles only |
| S-79 | Search-result listings for anything else (18183, appgoblin, gamepedia.jp, Google Play event pages) | unrated | titles only |

## 1. The game's lineage (the most useful finding)

| Version | Title | Publisher as shown | Launch | Notes |
|---|---|---|---|---|
| Mainland China | 杖剑传说 (full store title 杖剑传说:异世界冒险RPG) | G-bits (吉比特); Leiting (雷霆游戏) is G-bits' publishing brand (the Leiting part is my guess from the `ltgamesglobal` domain and search hits, not read on a page) | 2025-05-29 [S-67] | Has a test server ("先遣服") that gets tiers about a month early [S-68] |
| Hong Kong / Taiwan / Macau | 杖劍傳說 (guess: traditional spelling; not confirmed on a page) | ❓ | 2025-07-15 [S-67] | No Bahamut board found by search |
| Japan | 杖と剣の伝説 (English slug "sceptersword", package `com.zjcs.android.jp`) | Boltray Games [S-66] | 2025-07-15 [S-66] | Official site game.boltray.com/sceptersword, X account @tsueken_JP [S-66][S-79] |
| Global / West | Sword x Staff (`com.zjcs.android.us`, App Store 6751270546) | BOLTRAY PTE. LTD. [S-62] | 2026-05-19 [S-61][S-67] | App Store version history starts at 1.0.22 on 2026-03-26, and Fandom edits start 2026-03-03, so a test or soft launch ran from March 2026 [S-60][S-62] |
| Korea | 소드 x 스태프 | Boltray Games | 2026-11-04 [S-75] | |
| Southeast Asia | Sword x Staff | Boltray Games | 2026-11-04 [S-74] | |

`zjcs` in the package name is the pinyin initials of 杖剑传说. The same company therefore runs every version, and
global content follows the CN content in order.

What the older versions already have (as of autumn 2026):

- **Class tiers:** CN guides talk about the "8th class change" (八转) for Sage in September-October 2026, and the
  7th reached the CN test server in April 2026 [S-63][S-68]. CN "N转" lines up with global "Tier N": the CN
  beginner guide puts the 4th change at "Dragon 5, Lv 106" and eog.gg gives global Tier 4 at Lv 106 [S-63][S-69].
  CN uses four class names at every tier (术士 Sorcerer line, 贤者 Sage line, 斗士 fighter line, 骑士 Knight
  line) [S-63][S-68].
- **Kingdoms:** 森之国 (forest = Verdantglade), 山之国 (mountain = Cinder Ridge), 泽之国 (marsh/water = Aqualis),
  龙之国 (dragon = Loong Haven), 羽之国 (feather; guess: Aethyris), then 哈帕迪 and 伊格尼斯 (two later areas;
  English names unknown ❓) [S-63][S-64]. The English matches are my inference from order and meaning.
- **After Loong Haven:** 羽之国 unlocks "Bond Adventure" (羁绊冒险), which replaces tower climbing after the 5th
  class change [S-63]. JP players say 羽の国 needs the tower (通天塔) cleared [S-65].
- **Seasons:** CN had a season start on 2026-07-30 and another expected in spring 2026 [S-63][S-68]. CN separates
  permanent growth ("white power") from season growth ("green power") [S-63].
- **Global tier-4 names:** Prydwen has build guides titled Guardian, Destroyer, Dominator and Conqueror, and a
  YouTube title calls Dominator a "new Tier 4 class" [S-05][S-77]. Which base class each belongs to: ❓.

Caution: the global version may change numbers, names and timing. Use CN/JP facts as forecasts and mark them ❓
until the global game or a tier B source confirms them.

## 2. Survey of sources

Tier: B = experienced players of the live game, C = community wiki or player site, D = SEO or machine-written.

### English, global version

| Source | URL | Covers | Current as of | Tier | Who writes it, how it gets information |
|---|---|---|---|---|---|
| Fandom wiki (S-03) | https://swordxstaff.fandom.com | 56 articles: classes, class skills, class change, companions, fantomons, maps, Chaos Invasion, launch FAQ | First edit 2026-03-03, last edit 2026-05-30; no content edits since [S-60] | C | Hand-written by players. 466 revisions by 5 accounts; two accounts made 422 of them (one 205 edits all in March, one 217 edits March-May). 228 images uploaded March-May (skill icons, maps, store art) [S-60]. Pre-Season 2; stale but honest |
| sword-x-staff.wiki (S-04) | https://www.sword-x-staff.wiki | 78 English pages (plus pt/es/ja copies, 312 URLs): guides, class pages, platform and "review" pages | Pages dated 2026-05-20 to 05-27; sitemap home lastmod 2026-10-16 | D | Machine-written, see the evidence below |
| Prydwen (S-05) | https://www.prydwen.gg/sword-x-staff | Guides, build guide per class up to tier 4, skills list, tier list | Has tier-4 build guides, so updated after Season 2 | C (could be B: Prydwen normally uses named player writers) | Bot check: not read. Search titles only |
| eog.gg (Eden of Gaming) | https://eog.gg/games/sword-x-staff/ | 10 guides, 6 tools (stamina calculator, season star calculator, 4 maps), tier list, codes | Guides dated 2026-05-22 to 07-06; star calculator covers Seasons 1-3 [S-69] | C | "EOG Analyst Team"; cites a YouTube creator (QY Maple) for Season 1/2 material and one named player for DPS tests. No statement on where tool data comes from [S-69] |
| zeroluck.gg | https://zeroluck.gg/sword-x-staff/ | 13 topic guides (classes, companions, bestiary, friendship, gear, combat stats, game modes, currencies, life skills, reroll, relics, battle pass, banners), relic page, codes | ❓ (no dates shown) | C | Unnamed. Says guides are "verified in-game" and use the game's own English labels [S-70] |
| Loot & Waifus | https://lootandwaifus.com/sword-x-staff | Relic database, ingredient database with drop sources, interactive map, custom tier list, codes | API page dated 2026-07-04 [S-71] | C | One named maintainer. Publishes JSON dumps of relics and ingredients "used by community tools"; does not say how the data was obtained (structured ids, sets and drop chances suggest game files: guess) [S-71] |
| sword-x-staff-wiki.pages.dev | https://sword-x-staff-wiki.pages.dev | Beginner guide, classes, builds, skill tier list, "skills DB", codes, updates | Lists a "global launch" on 2024-12-20 and events through 2025-04 [S-72] | D | Unnamed static site. Its dates and codes do not match reality (global launch was 2026-05-19), so treat as invented. Do not use |
| Official site | https://swordxstaff.boltray.com (same content at swordxstaff.ltgamesglobal.com; game.boltray.com/SwordxStaff redirects here) | News, Lore, Guide tabs; redeem-code page; APK download; top-up | 10 posts, ids 192-203, 2026-05-14 to 2026-06-05; nothing newer [S-61] | official | Publisher. Three "Adventurer's Handbook / Tips" guide posts (ids 196, 198, 199) are official early-game advice. No patch notes, no FAQ page of substance [S-61] |
| App Store listing | https://apps.apple.com/us/app/6751270546 | Version numbers and dates, size (3.7 GB), languages, IAP price points | 1.0.45 on 2026-10-31 [S-62] | official | Publisher. Every "What's New" entry says only "User experience optimization", so store notes carry no patch information [S-62] |
| Google Play listing | https://play.google.com/store/apps/details?id=com.zjcs.android.us | Listing, plus "Major update" event cards under play.google.com/store/apps/eventdetails/... [S-79] | ❓ not read | official | Publisher. The event cards may name each content update: worth reading once the host is allowed |
| Official Discord | https://discord.gg/swordxstaff (the Fandom wiki also links discord.gg/b6xekW7U8z and discord.gg/RQcTyr66Y3) | Announcements, patch notes, codes, player guides (the SOF guides are of this kind) | live | B/official | Needs a login. Not joined, not read. Very likely where patch notes actually live, since the site and stores have none (guess) |
| Official Facebook | https://www.facebook.com/profile.php?id=61579592385490 | Announcements, codes | live | official | Pocket Tactics names Facebook and Discord as where codes appear [S-73]. Login wall likely |
| Official X | https://x.com/SwordxStaff | Announcements | ❓ | official | Linked from the Fandom wiki. Login wall for timelines |
| YouTube creators | search "Sword x Staff Season 2" | Season prep, tier-4 unlocks, dungeons, F2P progress series | Season 2 videos exist [S-77] | B to C | Players of the live game; eog.gg builds on one of them (QY Maple) [S-69]. Titles seen are listed in section 5 |
| Reddit | https://www.reddit.com/r/SwordxStaff | ❓ | ❓ | ❓ | Search found no indexed threads. A code `SXSREDDIT` exists, so an official Reddit presence exists [S-73]. robots.txt disallows all crawling |
| Pocket Tactics | https://www.pockettactics.com/sword-x-staff | Codes page (16 active, 14 expired, with rewards), tier list | Updated 2026-10-07 [S-73] | C for codes, D for tier list | Staff writer; codes collected from Facebook/Discord. Uses correct item names |
| Pocket Gamer | https://www.pocketgamer.com/sword-x-staff/ | Launch news, codes, class tier list | Updated November 2026 [S-74] | D | Launch piece is labelled a paid partner feature [S-74] |
| BlueStacks blog | https://www.bluestacks.com/blog/game-guides/sword-x-staff/ | Beginner, class, fantomon, tier list, best skills, codes | 2026-08-27 on the class guide [S-76] | D | Emulator vendor's content team; promotional |
| LDPlayer / MuMu blogs | https://www.ldplayer.net/codes/sword-x-staff-redeem-codes.html, https://www.mumuplayer.com/blog/sword-x-staff-beginner-guide.html | Codes, beginner guide | ❓ | D | Emulator vendors. sxswiki cites the MuMu page as a source |
| Pro Game Guides | https://progameguides.com/sword-x-staff/ | Beginner guide, tier list, codes | Titles say May-June 2026 [S-78] | D | Staff writers at launch; not updated for Season 2 by title |
| GamesRadar, Beebom, Twinfinite, Destructoid, GamingOnPhone, nerdschalk, gamertweak | search "Sword x Staff codes" | Codes, launch tier lists | mixed | D | Code-list journalism. Useful only to cross-check codes |
| topuplist, allthings.how, narcosis-the-game.com, allclash, oslink.io, mobi.gg, games.gg | search | "Season 2 guide", build pages in 15+ languages | 2026-06 to 09 by title | D | Top-up shops and content farms; mass-translated. Leads only |
| Inven Global, GameMeca | https://www.invenglobal.com/tag/Sword+X+Staff | Korean launch news | 2026-10 | press | Press releases |
| TapTap global, QooApp | https://www.taptap.io, https://apps.qoo-app.com | Store pages, user reviews | ❓ not read | ❓ | QooApp has a timeline for app 21632 [S-79]; which regional version it is: ❓ |

### Older regional versions (forecast material)

| Source | URL | Covers | Current as of | Tier | Notes |
|---|---|---|---|---|---|
| TapTap CN strategy hub | https://www.taptap.cn/app/717836/strategy | Curated player guides in sections: current-version events, beginner, daily, the four classes (Knight guides from 2nd to 7th change), long-term and season growth (relics, skills, pets, companions, gems, gear affixes), puzzles per kingdom, encyclopedia (maps, trading, recipes), dungeons | Posts dated 2025-06 to 2026-10-25 [S-63] | B for CN | The CN game's main forum; hand-written by players, pinned by moderators. Individual posts are at taptap.cn/moment/{id} |
| BWIKI | https://wiki.biligame.com/zjcswiki/ | Database: 1,140 relics, 1,430 weapons, 273 sets, 513 skills, characters, dungeons, maps, events; relics by kingdom | Updated 2026-11-17; data from "client version 1.3.0" [S-64] | C | Created 2025-08-04 by one editor plus one helper. The exact client version label means the tables are extracted from the game client [S-64]. BWIKI runs MediaWiki, so an `api.php` probably exists (guess, untested) |
| Gamerch JP | https://gamerch.com/sceptersword/ | Skill list and effects, strongest skill/fantomon rankings, builds, class change, "time-space gacha", Astral Pact item, friendship coins, events, gift codes | Page read was updated 2026-03-05 [S-65] | C | Hand-written by a small number of editors, with comments. Covers tiers 1-3 only |
| Gamepedia JP, appmatch | https://gamepedia.jp/apps/112421/wiki, https://games.appmatch.jp/gamewiki/tsuetokennodensetsu/ | Beginner guides | ❓ not read | D? | |
| 17173, 18183 | https://news.17173.com, https://m.18183.com/yxzt/8911899/ | Reposted fan guides (17173: per-tier class state from a fan WeChat account), SEO guides (18183) | 2025-06 to 2026-05 | C / D | 17173 reposts are genuine player analysis; 18183 is content-farm |
| 4Gamer | https://www.4gamer.net/games/913/G091380/ | JP press: launch, collaborations (KonoSuba, Bocchi the Rock, Luo Xiao Hei) | 2026-08-16 [S-66] | press | Collaboration order in JP hints at global event order (KonoSuba came first in both) |
| NGA, Bahamut, GameKee, Game8, GameWith | - | - | - | - | Searched; no dedicated board or wiki found for this game |

### Why sword-x-staff.wiki (S-04) is machine-written

Verdict: generated from YouTube video transcripts and store text by a language model, published in a batch, never
maintained. Evidence from the local copy in `raw/sxswiki/`:

1. **A leaked generator note.** `guide-sword-x-staff-fortburg.txt` contains: "(Note: As no relevant YouTube videos
   were found ... a placeholder ... is used. In a real scenario, this would be replaced ...)".
2. **Speech-to-text spellings of item names**, inconsistent between and inside pages. Counts across the 78 pages:

   | Game term (our rules) | Wrong forms on the site (occurrences) | Correct form on the site |
   |---|---|---|
   | Rolla (R-019) | "Rolo" 32, "Rola" 7, "Rollo" 6 | "Rolla" 14 |
   | Dawnium (R-018) | "Donium" 10, "Dan (premium currency)" 6 | "Dawnium" 28 |
   | Stellatie | "Stellalites" 19, "Stellatite" 2 | "Stellatie(s)" 18 |
   | Fantomon | "Phantomon(s)" 8 | "Fantomon(s)" 235 |

   Examples: "Spend gold (Rolo) liberally ... save premium currency (Donium)" (beginner guide) and "Stellalites
   (skill summons), Dan (premium currency), and Rolo (gold)" (F2P guide). The codes page, written from store
   text, spells all three correctly.
3. **Pages for search keywords that mean nothing in the game.** "Karlos" is described as a hybrid hero who mixes
   warrior and mage skills: no such playable character exists (the Fandom wiki mentions Karlos only on the
   companions page). The "Qin" and "AI" pages are generic filler. There are pages for PS5 and Steam releases
   that do not exist.
4. **One byline** ("Sword X Staff Wiki Team") on 77 pages, all dated within 8 days (2026-05-20 to 05-27, 42 on the
   first day), every page with the same skeleton: "Quick Guide" bullets, tables, FAQ.
5. No licence, no author, no edit history, no update after Season 2.

Use: leads only. Its numbers sometimes come from real creator videos (e.g. "200-pull pity" for skills), which is
why some of it is right, but nothing on it can be trusted alone.

## 3. Fetch recipes for the most valuable sources

General manners for all of them: one request at a time, at least 1 second apart (2 seconds for small fan sites),
a User-Agent that names the tool (kb_fetch.py already sends `sxs-knowledge-fetch/1.0`), obey robots.txt, fetch
only what changed, stop on a bot check or a 403/429 and report it. Store text, the URL, the fetch time and the
page's own date. Commit only text whose licence allows it; keep the rest in the gitignored cache.

### 3.1 Fandom wiki (tested, works)

- **Structure:** MediaWiki 1.43. 444 pages in all namespaces, 56 articles, 984 edits, 228 files, 5 admins [S-60].
- **API:** `https://swordxstaff.fandom.com/api.php` answered normally to curl, including with `maxlag=5`.
- **robots.txt:** `https://swordxstaff.fandom.com/robots.txt` returned a Cloudflare bot-check page (HTTP 403) to
  curl, so it could not be read, and HTML pages under `/wiki/` should be assumed to be behind the same check. Use
  only `api.php`, which is the interface MediaWiki offers to programs. Do not fetch `/wiki/` HTML.
- **Licence:** API `rightsinfo` says CC-BY-SA, linking https://www.fandom.com/licensing [S-60]. Text may be
  stored and paraphrased with credit. Fandom's terms of use were not read (host not reachable for HTML).
- **Recipe (already in kb_fetch.py):** `action=query&generator=allpages&gaplimit=50&gapfilterredir=nonredirects&prop=revisions|categories&rvprop=content|timestamp|ids&rvslots=main`, follow `continue`, 1 s apart. About 2 requests for the whole wiki.
- **Cheap change check (tested):** `action=query&list=recentchanges&rcprop=timestamp|title|ids&rclimit=50&rcnamespace=0`. If the newest `revid` equals the largest `revid` in our manifest (984 today), nothing changed: skip the full fetch. Run weekly; the wiki has been silent since 2026-05-30.
- **Credits (tested):** `action=query&list=allrevisions&arvnamespace=0&arvprop=timestamp|user|size|ids&arvlimit=500` gives every revision's author for CC BY-SA attribution. One request.
- **Images (tested listing only):** `action=query&list=allimages&ailimit=500&aiprop=url|timestamp|size|mime` lists 228 files, 187 MB in total, including skill icons named after the skill (`Blade_Tempest.png`, `Dark_Bullet.png`). These could label skill icons for the bot's detector. They are game art (the publisher's copyright, not CC BY-SA), and the image host `static.wikia.nocookie.net` is not allowed here: fetch only on mae's decision, into the gitignored cache.

### 3.2 sword-x-staff.wiki (tested, works)

- **Structure:** `sitemap.xml` with 312 URLs: 78 English pages under `/guide/`, `/classes/`, `/platforms/`,
  `/release/`, `/review/`, `/codes/`, and the same under `/pt`, `/es`, `/ja`. Each `<url>` has a `<lastmod>`.
- **robots.txt:** `User-Agent: * / Allow: /` and the sitemap line. No terms page, no licence found.
- **Recipe (already in kb_fetch.py):** sitemap, English pages only, one page per second, text only, gitignored.
- **Change check:** compare each `<lastmod>` with the stored one; today only 4 URLs (the home pages) changed
  after May. A re-fetch is worth it only if `lastmod` moves. Low value: monthly at most.

### 3.3 Official site (curl blocked by our proxy; read through WebFetch)

- **Structure:** list pages `/news`, `/news/news`, `/news/lore`, `/news/guide`; articles at
  `https://swordxstaff.boltray.com/news/{id}` with numeric ids (192-203 seen). No pagination, no API or feed
  seen. `swordxstaff.ltgamesglobal.com` serves the same site.
- **robots.txt / terms:** not readable from here. The page links only a privacy policy
  (`agreement.boltray.net/privacy`). Content is the publisher's copyright: store as a working cache, cite by URL.
- **Recipe (untested):** fetch `/news` once a week; for each article id not yet stored fetch `/news/{id}`; store
  title, date, text. About 1-3 requests a week. Do not walk the id range blindly: only ids linked from the list.

### 3.4 eog.gg (curl blocked; read through WebFetch)

- **Structure:** hub `https://eog.gg/games/sword-x-staff/` with anchors (`#tier-list`, `#guides`, `#builds`,
  `#database`, `#roadmap`, `#codes`); guides at `/games/sword-x-staff/guides/{slug}/`; tools at
  `/games/sword-x-staff/tools/{slug}/`. Each guide card shows an "updated" date.
- **robots.txt / terms / licence:** not read. No licence stated on the pages read: cache only, cite by URL.
- **Recipe (untested):** fetch the hub; fetch each guide whose "updated" date is newer than stored; 2 s apart;
  about 17 pages. The tools are JavaScript pages: their data (map points, calculator rates) sits in script or
  JSON files that a text fetch will not capture. Record the tool URLs; do not scrape their scripts without
  asking the site.

### 3.5 zeroluck.gg and Loot & Waifus (curl blocked)

- **zeroluck.gg:** index `https://zeroluck.gg/sword-x-staff/guides/`, sections `/sword-x-staff/relics/`,
  `/sword-x-staff/codes/`. Guide URLs were not shown by the reader. Recipe (untested): fetch the index, then each
  linked page under `/sword-x-staff/`, 2 s apart. robots/terms not read.
- **Loot & Waifus:** `https://lootandwaifus.com/sword-x-staff` (hub), `/sword-x-staff-ingredient-database/`,
  `/sword-x-staff-interactive-map/`, `/sword-x-staff-custom-tier-list`, `/guides/sword-x-staff-codes`,
  `/guides/sword-x-staff-api/`. The API page documents two JSON dumps (relics: id, name, rarity, element, region,
  description, stats, set, set_bonus, icon; ingredients: id, name, rarity, regions, sources with monsters and
  drop chances) and invites requests for more data through the maintainer's Discord [S-71]. The dump URLs were
  not captured. Recipe (untested): read the API page for the two URLs and fetch each once per game version. This
  is the single best machine-readable dataset found for the global game: ask the maintainer about reuse before
  committing any of it, since no licence is stated.

### 3.6 TapTap CN strategy hub (reachable through WebFetch; curl untested)

- **Structure:** `https://www.taptap.cn/app/717836/strategy` lists sections and post titles with dates; posts at
  `https://www.taptap.cn/moment/{id}`. The site is a JavaScript app; a plain fetch may return little text.
- **robots.txt / terms:** not read. Posts are the authors' copyright: take facts, not text.
- **Recipe (untested):** monthly, fetch the hub, list new post titles, fetch only the few that answer an open
  question (new tier, new kingdom, season rules). Store a short English fact list with the post URL and date,
  not the Chinese text. Chinese terms to search: 转职 (class change), 赛季 (season), 圣物/古遗物 (relic),
  幻兽/宠物 (fantomon), 材料秘境 (material realm, guess), 先遣服 (test server).

### 3.7 BWIKI (reachable through WebFetch; curl untested)

- **Structure:** `https://wiki.biligame.com/zjcswiki/` with page names in Chinese (`首页`, relic lists per
  kingdom, skill lists for 术师 / 战士). MediaWiki-based, so `https://wiki.biligame.com/zjcswiki/api.php` is
  the likely program interface (guess).
- **Licence:** not stated on the home page; a "disclaimer and copyright" page exists and must be read first.
  Many BWIKI wikis use CC BY-NC-SA 4.0 (seen on other BWIKI sites in search results), which forbids commercial
  reuse but allows a private knowledge base with credit.
- **Recipe (untested):** same as Fandom: `allpages` generator with revisions, 50 a request, 1-2 s apart; store
  wikitext in the gitignored cache until the licence is confirmed. Its relic, set and skill tables have stable
  ids that can be matched to global names through icons or order.

### 3.8 Prydwen: do not fetch

Bot check on every page. Use only titles and snippets that a web search returns, tagged [S-05]. If mae wants its
content, the clean route is for mae to read a page in a normal browser and paste what matters.

### Recommended additions to `scripts/kb_fetch.py` (not edited)

1. `fandom --if-changed`: one `recentchanges` call first; skip when the newest revid is already in the manifest.
2. Store editors per page (`allrevisions`) in the manifest as `contributors`, for CC BY-SA credit.
3. `fandom-images --list`: write the file list (name, URL, size) without downloading; download only with an
   explicit flag.
4. `sxswiki`: keep `<lastmod>` per URL in the manifest and fetch only pages whose `lastmod` changed.
5. New sources as separate subcommands, each with its own robots.txt check, cache folder and licence note:
   `official` (news list, then new ids), `eog`, `zeroluck`, `lnw` (the two JSON dumps), `bwiki` (MediaWiki
   API), `taptapcn` (hub titles only).
6. `get()`: send `maxlag=5` on MediaWiki calls; honour `Retry-After`; treat HTTP 403 with a Cloudflare page as
   `BotCheck` (today only the "Just a moment" title on a 200 response is detected; Fandom's robots.txt came back
   as a 403, which raises `HTTPError` instead).
7. `status`: print the age in days and the newest page date per source, and flag a source older than 30 days.
8. A `hosts` subcommand that tries one HEAD request per configured host and prints which are blocked by the
   proxy, so a session learns in seconds what it can reach.

## 4. Can game data be obtained directly?

Only what public sources say; no APK was downloaded or opened.

- **Engine and file format:** no public source names the engine (Unity, Cocos or other) or describes the package
  contents. Searches in English and Chinese for datamining or unpacking of this game found nothing specific. ❓
- **Size:** the iOS app is 3.7 GB [S-62], so assets ship with the app or download on first run.
- **Indirect evidence that tables are extractable:** BWIKI states its data is from "client version 1.3.0" and
  holds 1,140 relics, 1,430 weapons, 273 sets and 513 skills [S-64]; Loot & Waifus serves relic and ingredient
  dumps with internal ids and drop chances [S-71]. Someone reads the client data in both communities. Neither
  says how.
- **Public datamine repositories:** none found (no GitHub project, no named tool).
- **Community spreadsheets:** none found by search. The Google Sheets hits were for other games (one checked:
  Tap Titans). Spreadsheets shared inside the Discord would not be indexed; mae could look in the server's
  guide or resources channel.
- **Calculators and tools (public):** eog.gg stamina and gathering calculator, season Primordial Star calculator
  (Seasons 1-3), unlock-resource map, kingdom map, Lucky Roulette map, Prayer Statue map [S-69]; Loot & Waifus
  interactive map, ingredient database, custom tier-list maker [S-71]; Prydwen skills list and tier list [S-05].
- **Recommendation:** take structured data from Loot & Waifus (global names) and BWIKI (complete tables, CN
  names) with permission and credit, rather than opening the game package ourselves. Our own screenshots stay
  the tier A check.

## 5. Best individual pages per topic

"Not read" means the title and URL come from search results only.

| Topic | Page | One line |
|---|---|---|
| Classes / skills | https://www.prydwen.gg/sword-x-staff/guides/classes-and-roles | Class overview (not read; bot check) |
| | https://www.prydwen.gg/sword-x-staff/skills | Skill list (not read) |
| | https://www.prydwen.gg/sword-x-staff/guides/build-guide-sorcerer , `-sage`, `-archmage`, `-arcanist` | Mage-line build guides (not read) |
| | https://www.prydwen.gg/sword-x-staff/guides/build-guide-knight , `-duelist`, `-paladin`, `-berserker` | Warrior-line build guides (not read) |
| | https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian , `-destroyer`, `-dominator`, `-conqueror` | The four tier-4 classes (not read) |
| | https://swordxstaff.fandom.com/wiki/Mage_Skills (local `mage-skills.wiki`) | Hand-written skill tables, launch state |
| | https://gamerch.com/sceptersword/ (skill list, skill effects) | JP skill database, tiers 1-3 |
| | https://www.taptap.cn/app/717836/strategy (class sections) | CN builds up to the 8th tier |
| | https://news.17173.com/content/05072026/112211079.shtml | CN: state of each class at the 7th tier |
| Fantomons | https://www.prydwen.gg/sword-x-staff/guides/fantomon-guide | Fantomon guide (not read) |
| | https://www.bluestacks.com/blog/game-guides/sword-x-staff/sxs-fantomon-guide-en.html | Ranked pets, tier D (not read) |
| | https://www.youtube.com/watch?v=DT_hvUztZBI | Tier-4 class and adult Fantomon requirements (title only) |
| Relics | https://zeroluck.gg/sword-x-staff/relics/ | Relic page (not read) |
| | https://lootandwaifus.com/guides/sword-x-staff-api/ | Relic and ingredient JSON dumps, field list |
| | https://wiki.biligame.com/zjcswiki/ | CN relic lists per kingdom, sets |
| Material realms, stamina | https://www.prydwen.gg/sword-x-staff/guides/stamina-and-dawnium-usage | Stamina and Dawnium spending (not read) |
| | https://eog.gg/games/sword-x-staff/tools/stamina-calculator/ | Gathering yield by rank and tier, mop-up value model |
| | https://swordxstaff.boltray.com/news/198 | Official "Art of Spending" handbook |
| Dungeons and thresholds | https://www.prydwen.gg/sword-x-staff/guides/daily-dungeons | Daily dungeons (not read) |
| | https://eog.gg/games/sword-x-staff/guides/void-rifts/ , `/dps-dummy-test/` | Void Rifts, DPS test method |
| | https://www.youtube.com/watch?v=VnxdCn_6KFg | Bladeshire Dungeon, Lv 225 gear preview (title only) |
| Gear, gems | https://www.prydwen.gg/sword-x-staff/guides/gear-refinement-and-affix-transfer | Refinement and affix transfer (not read) |
| Seasons / Loong Haven | https://eog.gg/games/sword-x-staff/guides/season-2-prep/ | Checklist before the Season 2 rollover, speed-up milestones |
| | https://eog.gg/games/sword-x-staff/tools/star-calculator/ | Primordial Star conversion for Seasons 1-3 |
| | https://www.youtube.com/watch?v=1yvUysq0sg8 | "Complete Loong Haven Guide: every Season 2 unlock and resource trap" (title only) |
| | https://www.youtube.com/watch?v=yP3zwWw671g | Tips for entering S2 Loong Haven (title only) |
| | https://www.youtube.com/watch?v=l1oUFfix3Zs | SSS rating for Season 2 (title only) |
| | https://www.youtube.com/watch?v=WVpsl8p7zKM | Which skills stay good in Season 2 (title only) |
| Exploration, statues | https://eog.gg/games/sword-x-staff/tools/resource-map/ , `/kingdom-overview/`, `/lucky-roulette/`, `/prayer-statue/` | Maps of keys, potions, drills, roulettes, statues per kingdom |
| Events | https://www.prydwen.gg/sword-x-staff/guides/grand-treasure-hunt | Grand Treasure Hunt (not read) |
| | https://eog.gg/games/sword-x-staff/guides/grand-treasure-hunt/ | Same event, readable |
| | https://swordxstaff.fandom.com/wiki/A_Beginner_Chaos_Invasion_Guide | Chaos Invasion (local copy) |
| | https://www.4gamer.net/games/913/G091380/ | JP collaboration history: forecast of global events |
| Gacha | https://www.prydwen.gg/sword-x-staff/guides/gacha-system | Gacha system (not read) |
| | https://eog.gg/games/sword-x-staff/guides/gacha-and-pity/ | Pity reference |
| Beginner / tips | https://www.prydwen.gg/sword-x-staff/guides/beginner-guide , `/tips-and-tricks` | (not read) |
| | https://eog.gg/games/sword-x-staff/guides/important-tips/ , `/destiny-fruit/`, `/companion-upgrade/`, `/food-guide/`, `/reroll-guide/` | Short topic guides |
| | https://swordxstaff.boltray.com/news/196 , `/news/199` | Official early-game handbook and checklist |
| Codes | https://www.pockettactics.com/sword-x-staff/codes | 16 active and 14 expired codes with rewards, updated 2026-10-07 |
| | https://www.pocketgamer.com/sword-x-staff/codes/ , https://zeroluck.gg/sword-x-staff/codes/ , https://lootandwaifus.com/guides/sword-x-staff-codes | Cross-checks |
| Patch notes | none public | The official site has no patch notes; App Store notes are empty phrases. Discord (login) is the likely home. Google Play "Major update" cards are the nearest public record (not read) |
| Lineage / future content | https://www.baijing.cn/article/56139 | Release dates per region, revenue |
| | https://www.taptap.cn/app/717836/strategy | Everything the CN version has that global will get |

Codes seen on Pocket Tactics on 2026-10-07 (active): ISLA, THEGAMETHEORIST, SXSDCTHANKS, SXSCREATOR,
SXSAMBASSADOR, SXSPARTNER, SXSREDDIT, VANOSSTEAM, CARBOTANIMATIONS, ZJ999, ZJ888, ZJ777, SS000, SS888, SS777,
SS999 [S-73]. Android redemption path on that page: box icon bottom right > User Center > Gift Code; rewards
arrive in the mailbox [S-73]. Rewards and expiry belong on the [codes](../systems/codes.md) page.

## 6. Hosts to allow

Ranked by value for the knowledge base. All except the first two are blocked for curl today.

| Rank | Hostname | Why |
|---|---|---|
| 1 | `swordxstaff.fandom.com` | Already allowed. CC BY-SA text through the API |
| 2 | `www.sword-x-staff.wiki` | Already allowed. Low value; keep for leads |
| 3 | `eog.gg` | Best readable English guides and the only season calculators and kingdom maps |
| 4 | `lootandwaifus.com` | Relic and ingredient JSON dumps, interactive map |
| 5 | `zeroluck.gg` | 13 system guides using the game's own labels, relics, codes |
| 6 | `www.taptap.cn` | CN strategy hub: future tiers, kingdoms, seasons |
| 7 | `wiki.biligame.com` | CN database wiki: full relic, set, skill, weapon tables |
| 8 | `swordxstaff.boltray.com` (and `swordxstaff.ltgamesglobal.com`, same site) | Official news and handbook posts; redeem-code page lives here |
| 9 | `gamerch.com` | JP wiki: skill effects, rankings, events |
| 10 | `www.pockettactics.com` | Best-kept code list with rewards |
| 11 | `play.google.com` | Listing and "Major update" event cards for `com.zjcs.android.us` |
| 12 | `apps.apple.com` | Version history (dates of every client update) |
| 13 | `www.youtube.com` | Video titles and descriptions of Season 2 creators; transcripts are not available through plain fetch, so limited value |
| 14 | `news.17173.com`, `www.4gamer.net`, `www.baijing.cn` | Occasional CN/JP articles; fetch on demand |
| - | `www.prydwen.gg` | Do not add: bot check, cannot be used politely |
| - | `www.reddit.com` | Do not crawl: robots.txt disallows everything; Reddit asks programs to use its API under its public content policy |
| - | `discord.gg`, `x.com`, `www.facebook.com` | Login walls. mae can paste announcements instead |
| - | `static.wikia.nocookie.net` | Only if mae wants the Fandom skill icons |
| - | `sword-x-staff-wiki.pages.dev`, `www.bluestacks.com`, `www.ldplayer.net`, `www.mumuplayer.com`, `progameguides.com`, `www.pocketgamer.com`, `topuplist.com` | Not worth allowing: tier D |

## Open questions

- ❓ English names of the kingdoms after Loong Haven (羽之国, 哈帕迪, 伊格尼斯). Aethyris is the fifth land named
  in global lore and shown on eog.gg's Season 2 art, so 羽之国 = Aethyris is likely. Confirm on the in-game map.
- ❓ Which base class each tier-4 name (Guardian, Destroyer, Dominator, Conqueror) belongs to, and the names of
  tiers 5-8 in English. Confirm from the in-game class tree or a Prydwen page read by mae.
- ❓ Global season calendar. eog.gg says Season 2 came with the second KonoSuba arc on 2026-07-29; CN seasons seem
  to last about 3 months. Confirm from in-game season timers.
- ❓ Game engine and data format. Not stated anywhere public.
- ❓ Whether a Traditional Chinese (HK/TW) community site exists; none found.
- ❓ Where patch notes are published. Probably Discord announcements and in-game mail: ask mae.
- ❓ Licences of eog.gg, zeroluck.gg, Loot & Waifus, BWIKI (copyright page not read).
- ❓ What ran between March 2026 (first App Store version, first Fandom edits) and the 2026-05-19 launch.

## Sources

- [S-03] local copy `raw/fandom/` and `manifest.json` (55 pages, edited 2026-03-26 to 2026-05-30)
- [S-04] local copy `raw/sxswiki/` (78 pages) and its live `robots.txt` and `sitemap.xml`
- [S-05] Prydwen page titles and URLs from web search only
- [S-60] `https://swordxstaff.fandom.com/api.php`: siteinfo (statistics, rightsinfo), allrevisions, recentchanges, allimages
- [S-61] https://swordxstaff.boltray.com/news and the home page of swordxstaff.ltgamesglobal.com
- [S-62] https://apps.apple.com/us/app/6751270546
- [S-63] https://www.taptap.cn/app/717836/strategy and https://www.taptap.cn/moment/700016190919018939
- [S-64] https://wiki.biligame.com/zjcswiki/
- [S-65] https://gamerch.com/sceptersword/932324
- [S-66] https://www.4gamer.net/games/913/G091380/
- [S-67] https://www.baijing.cn/article/56139
- [S-68] https://news.17173.com/content/05072026/112211079.shtml
- [S-69] https://eog.gg/games/sword-x-staff/ , `/tools/`, `/guides/season-2-prep/`
- [S-70] https://zeroluck.gg/sword-x-staff/guides/
- [S-71] https://lootandwaifus.com/guides/sword-x-staff-api/
- [S-72] https://sword-x-staff-wiki.pages.dev/updates
- [S-73] https://www.pockettactics.com/sword-x-staff/codes
- [S-74] https://pocketgamer.com/sword-x-staff/global-launch/ and `/southeast-asia-launch-today`
- [S-75] https://www.invenglobal.com/articles/27260/sword-x-staff-confirmed-for-official-launch-on-november-4
- [S-76] https://www.bluestacks.com/blog/game-guides/sword-x-staff/sxs-class-guide-en.html
- [S-77] YouTube search results (titles only), video ids in section 5
- [S-78] Search-result titles from topuplist.com, allthings.how, narcosis-the-game.com, allclash.com, oslink.io, mobi.gg, progameguides.com
- [S-79] Search-result titles from appgoblin.info, m.18183.com, gamepedia.jp, play.google.com event pages, m-apps.qoo-app.com
- Rules R-018, R-019 for the correct currency names
