# Chinese version (杖剑传说): source notes and term dictionary

<!-- index: Read when you meet a Chinese game term, want to re-check a forecast on future-content.md, or need the list of Chinese-version pages worth re-reading each season -->

> **Summary:** Notes on every Chinese-version source read on 2026-11-18, a Chinese-to-English dictionary of game
> terms (marking which English names are official global terms and which are our translation), the relic sets and
> dungeons listed by the BWIKI data site, and the URLs to re-read when a new season approaches. BWIKI turned out to
> be nearly empty apart from its home page; the real substance is in TapTap CN player guides, the GameKee wiki's
> timeline and threshold tables, and 17173 reposts of a fan account.
> **Applies:** all seasons (forecast material; tier C at best when applied to global)
> **Related:** [Future content](../../systems/future-content.md), [provenance](../provenance.md), [Seasons](../../systems/seasons.md),
> data: [class-tiers-cn.json](../../data/class-tiers-cn.json), [skills-cn.json](../../data/skills-cn.json)

## Register fragment (tags S-90 to S-97; the last two tags of the assigned range are unused)

| Tag | Title | URL | Tier | Date seen/published | Notes on reliability |
|---|---|---|---|---|---|
| S-90 | BWIKI 杖剑传说 wiki ("坎斯汀之约 资料站") | https://wiki.biligame.com/zjcswiki/ | C (CN version) | fetched with curl 2026-11-18; home page states data version 1.3.0 (build 155272) | Fan wiki, licence CC BY-NC-SA 3.0 stated in its footer. Only 18 articles exist; the home page holds the useful data (relic sets and dungeon lists per kingdom). Counts on the home page (1,140 relics, 513 skills) describe a planned database, not pages that exist. One community page repeats a summary of the official stream of 2025-10-09 |
| S-91 | GameKee 杖剑传说 wiki: unlock timeline, dungeon threshold table, relic overview | https://www.gamekee.com/zjcs/687197.html ; https://www.gamekee.com/zjcs/679101.html ; https://www.gamekee.com/zjcs/689421.html | C (CN version) | read through WebFetch 2026-11-18; threshold table dated 2026-03-27 | Fan-maintained tables. Its S1 and S2 thresholds equal the global ones exactly, which is the best evidence for its accuracy. The timeline's S4 days were written before S4 began and are about 14 days early |
| S-92 | TapTap CN season and resource guides | moments 754948742896944599 (season mechanics, 2025-12-29); 696488653752369338 ("detours" S1 master post); 713549377435602271 ("detours" S3 master post); 753637991041206291 (zero-spend long-term plan, 2026-04-24); 828056536826775738 (trap-avoidance guide for paying players, 2026-07-19); 722047428533945867 (zero-spend class planning, to 2026-09-30); 728122252914066468 (Bond Adventure, 2025-10-18). URL pattern https://www.taptap.cn/moment/{id} | B for the CN version; C for global | read through WebFetch 2026-11-18 | Long-running player guides, several pinned by moderators. Opinions on balance are personal. Numbers may be outdated by patches (authors say so) |
| S-93 | TapTap CN Sorcerer guides, tiers 4-9 | moments 724835633503144997 (tier 4), 755230505036680200 and 737795120329393494 (tier 5), 762373172946276183 and 781000949056407937 (tier 6), 805421283138341912 (tier 7), 844661786425689715 and 851772280261316451 (tier 8), 832133601800751499 (tier-8 duel analysis, 2026-07-30), 869743882454173463 (tier-9 leak post, 2026-11-11) | B for CN; C for global | read through WebFetch 2026-11-18 | Three regular authors. Skill types and elements are often not stated; tier-8 and tier-9 posts include speculation, marked in our pages |
| S-94 | TapTap CN Sage guides, tiers 4-8 | moments 723599278475313353 (tier 4), 719342760796098362 (tier 5 Prophet), 779140209349492929 (tier 6), 795815913130558066 and 813437480635203957 (tier 7), 857167205320623609 and 843131669673148539 (tier 8) | B for CN; C for global | read through WebFetch 2026-11-18 | Two posts are image-only (builds unreadable); one is flagged by TapTap as possibly AI-written (813437480635203957) |
| S-95 | TapTap CN Knight, Duelist and Fantomon posts | moments 700016190919018939 (Knight skills), 831240433475520038 (tier-8 Duelist leak), 808741946083246280 (Fantomons and sync, 2026-05-27), 703113036122032545 (all classes at tier 4) | B for CN; C for global | read through WebFetch 2026-11-18 | |
| S-96 | 17173 reposts of the fan account "杖剑攻略站" | https://news.17173.com/content/01012026/083707715.shtml (S4 preparation); /01262026/040232575.shtml (Pirate Ship dungeon); /03062026/232909336.shtml (Observatory sets); /05052026/151029904.shtml (new-season pitfalls); /05162026/094330203.shtml (S5 test-server changes); /05292026/095529902.shtml (first anniversary, official text) | C (CN version) | read through WebFetch 2026-11-18 | Genuine player analysis reposted from a WeChat account; same family as S-68 |
| S-97 | Official CN maintenance notices, as reposted | https://www.233leyuan.com/post-detail/2049364966736965632 (2026-04-29: Ignis, tier 7, Season 5); https://www.taptap.cn/moment/834026823116390976 (2026-08-05 patch summary by a player) | official text at second hand: rank with B | read through WebFetch 2026-11-18 | The 04-29 notice is the only place the S4 and S5 season names and the S5 start time were read in official wording |

Earlier tags reused here: S-63 (TapTap strategy hub), S-64 (BWIKI home through WebFetch), S-68 (17173 class-state
article of 2026-05-07), all defined in [provenance](../provenance.md).

How the reading was done: `wiki.biligame.com` with curl (robots.txt read and obeyed: only plain article URLs and
`api.php` listing calls; no `index.php?`, File or Special pages); everything else through the WebFetch reader,
which returns a model's digest of the page, not the page. Digests can garble tables (one read "Lv 5,140" for the
tier-5 level) and cannot read images, where many CN guides keep their builds.

## Source-by-source notes

### BWIKI (S-90)

- Structure: MediaWiki with Semantic MediaWiki. `api.php?action=query&list=allpages` works with curl and lists 33
  main-namespace pages, of which about ten are single relic pages, one a skill page (强袭破甲), one a reposted news
  summary and four community test posts. The navigation links 术师, 战士, 角色一览, 副本, 地图, 活动, 武器图鉴 and the
  per-kingdom pages return 404: they do not exist yet. The relic and skill overview pages are query tables that
  show ten rows and send "more results" to a Special page, which robots.txt forbids.
- So there are **no clean skill or relic tables** to import. `skills-cn.json` was therefore built from TapTap
  guides, not from BWIKI.
- What the home page gives (cached in `raw/bwiki/首页.html`): the seven kingdom tabs (森之国, 山之国, 泽之国, 龙之国,
  羽之国, 哈帕迪, 伊格尼斯), four Legendary relic sets per kingdom with item names and internal ids, a block of
  cross-kingdom sets, and every dungeon per kingdom.
- Relic filter values show the pool names: 龙之国乾坤造化, 龙之国道衍天机, 羽之国曙光秘誓; and five relic elements
  (light, dark, water, wind, fire).
- Relic pages show: 原初宝石 (gem acquisition 10%), 幸运神像 (dungeon rating reward doubling chance 10%), 招财猫神像
  (home Rolla output +10%), 黄金神木 (home wood output +10%), 光明之巅 (mountain, crit damage 7.5%), 丰饶无虞之角
  (forest, damage bonus 2.5%), 玉皇紫金冠 (Loong pool 2, HP 12.5%, set 天道神光), 寰宇乾坤斧 (Loong, DEF 12.5%, set
  天道神光), 天极八阵图 and 灵帝神冢 (Loong pool 1, damage resistance 2.5%).
- The skill page: 强袭破甲, tier 4, class 征服者, type 秘法, cooldown 0: each technique hit ignores part of the
  target's defence (33%+), +10% per own buff up to three. This is the global charm Piercing Assault.
- Stream summary of 2025-10-09 (reposted): big-mine nodes become personal; dungeon pity; a training dummy; a
  catch-up system for returners in about November 2025; tier 6 confirmed finished; new rainbow skills for the
  feather kingdom; overflow relic shards become convertible; penalties for moving gold through gems; "the negative
  feedback of hoarding resources for a season is under review".

### GameKee (S-91)

- Unlock timeline by server day and level: relics Lv 30, Destiny Fruit Lv 31, tier 2 Lv 44, Fantomons Lv 50,
  tier 3 Lv 82, gems Lv 100; S1 days 4 (mountain), 12 (marsh, S1 opens), 24 and 33 (later dungeons), season map
  鲸背岛; S2 day 47, tier 4 Lv 106, Adult Fantomon Lv 108, day 60 two-player gem dungeon 幻天鼎 at Lv 116, day 61
  将军陵 at Lv 130 and second gem socket, day 73 season map 通天塔, day 78 青云观, day 86 Loong relic pool 2, day 92
  古剑城, day 99 仙海云舟 and the Fantomon 竹林仙君; S3 day 114, tier 5 Lv 136, day 127 third gem socket at
  enhancement 160, day 128 永恒花庭 (Lv 160), day 141 season map 星海迅游, day 144 战渊堡垒, day 155 relic pool 2,
  day 159 净化之庭, day 169 Fantomon 虹彩星灵, day 174 秩序神殿, day 183 relic pool 3, day 197 烈阳尖塔, then 君临之巢;
  S4 (days written as 215+, really from day 229): tier 6 Lv 172, Fantomon sync Lv 180, second dungeon Lv 190,
  fourth gem socket at enhancement 190, season map 荒诞乐园, relic pools 2 and 3.
- Threshold table: Seasons 1-4 complete, with the season names 逢魔时至, 渊虹邂羽, 混沌终焉, 怪诞剧场. Copied into
  [future-content](../../systems/future-content.md).
- Relic overview: a stat grid per pool (S1 forest/mountain/marsh; S2 Loong I-II; S3 feather I-III; S4 Hapadi
  I-III; S5 Ignis I-III) counting how many Mythic and Legendary relics give crit rate, crit damage, accuracy,
  block, crit resistance, damage bonus, damage resistance; block damage resistance appears from S4.
- Its forum shows players asking for S5 and tier-8 updates: the wiki lags the game by one to two seasons.

### TapTap CN (S-63, S-92 to S-95)

- The hub (https://www.taptap.cn/app/717836/strategy) groups guides by class collection: Sorcerer
  `entity-collection/277421`, Sage `272820`, Duelist `277420`, Mage class `277424`, Warrior class `277423`,
  Fantomons `351535`, companions `407397`.
- Season mechanics post: season = major version; five things exceed the cap; four ratings (gameplay, cultivation,
  gear, overall); season Primostars = fixed amount + cultivation score at a season-specific ratio; top 10 of a
  server group get a permanent title. No catch-up mechanic as of 2025-12.
- "Detours" master posts (one per season) are the most complete veteran advice; the S1 post has the shard costs,
  cart order, companion milestones and element choices; the S3 post has the affix system.
- Class guides appear within days of each tier reaching the test server, about a month before the live season.

### 17173 fan-account reposts (S-68, S-96)

- Dated articles give calendar anchors: Eternal Flower Court opening 2025-10-03 (S3 day 128 computed from launch:
  the same day), S4 start 2026-01-12, Pirate Ship about 2026-01-26, Observatory 2026-03-08, S5 start 2026-05-07.
- The S4 preparation article is the best checklist for a season change; the S5 pitfalls article covers rank
  timing, Temporal Crystals and affix inheritance.

### Not reached

- `www.taptap.cn`, `gamerch.com`, `news.17173.com`, `gamepedia.jp`, `www.bilibili.com`: curl is refused by our
  network proxy (no robots.txt read), so only WebFetch was used. `www.9game.cn` refused the reader (robots).
- Japanese sites (Gamerch, Gamepedia JP) were not read in this pass: JP launched after CN and covers tiers 1-3.
- Bilibili videos (for example the S3 threshold video BV1rT1CBiEcC) and image-only TapTap posts.
- Official CN site and the in-game notice board. Season 6's name and kingdom were not found anywhere.

## Term dictionary: Chinese to English

"Official" = the English term is the global game's own word as used in our glossary sources ([S-01], [S-02],
[S-03], rules). "Ours" = our translation or transliteration; the global name is unknown. "Inferred" = official
English word, matched to the Chinese word by meaning, order or numbers (not seen side by side).

### Kingdoms, seasons, places

| Chinese | English | Status |
|---|---|---|
| 杖剑传说 | Sword x Staff | Official (same game; CN title) |
| 坎斯汀 | name of the game world (Kanstin) | Ours |
| 森之国 | Verdantglade | Inferred |
| 山之国 | Cinder Ridge | Inferred |
| 泽之国 / 泽国 | Aqualis | Inferred |
| 龙之国 / 龙国 | Loong Haven | Inferred (same thresholds and levels) |
| 羽之国 / 羽国 | Aethyris | Inferred (weaker: by order only) |
| 哈帕迪 / 哈国 | Hapadi | Ours |
| 伊格尼斯 | Ignis | Ours |
| 逢魔时至 (S1) | Witching Hours | Inferred |
| 渊虹邂羽 (S2) | Abyss Rainbow Meets Feather | Ours |
| 混沌终焉 (S3) | Chaos's End | Ours |
| 怪诞剧场 (S4) | Theatre of the Bizarre | Ours |
| 霜焰之歌 (S5) | Song of Frost and Flame | Ours |
| 鲸背岛 | Whaleback Island | Inferred |
| 通天塔 (S2 season map) | probably Acme Nexus ❓ | Inferred, weak |
| 赛季 / 首日服 / 先遣服 | season / first-day servers / early-access test server | Ours |
| 位面 / 界域 | plane (server group) / realm (group of planes) | Ours |
| 位阶 (下位, 中位, 上位) | Kingdom Rank (lower, middle, upper step) | Inferred |

### Dungeons

| Chinese | English | Status |
|---|---|---|
| 世界之树 | Auroradrasil | Inferred |
| 机神山 | Mecha Summit | Inferred |
| 海之宫遗迹 | Ocean Palace Ruins | Inferred |
| 源水大社 | Aquaorigin | Inferred |
| 黄泉阁 | Hellhold | Inferred |
| 封魔峡 | Demonseal Gorge | Inferred |
| 将军陵 | Warlord's Rest | Inferred |
| 青云观 | Cloudcrest Temple | Inferred |
| 古剑城 | Bladeshire | Inferred |
| 仙海云舟 / 云海仙舟 | Celestship | Inferred |
| 幻天鼎 (two-player gem dungeon) | Demonbind Tower | Inferred (same Lv 116) |
| 幻想阶梯 | Fantasia Ascent | Inferred |
| S3-S5 dungeon names | see [future-content](../../systems/future-content.md) | Ours |
| 普通 / 困难 / 噩梦 / 炼狱 / 深渊 | Normal / Hard / Nightmare / Purgatory / Abyss | Official for the first four; Abyss ours |
| 日常副本 | daily dungeon | Official |
| 圣兽试炼 / 圣兽 | Crucible of Hieromon / Hieromon | Inferred |
| 混沌入侵 / 混沌 | Chaos Invasion | Official |
| 双影幻境 / 双影 | two-player dungeon mode (Twin Shadow) | Ours |
| 公会讨伐 | guild boss raid | Ours |
| 竞技场 / 挑战赛 (2v2, 4v4) / 组队赛 | Arena / challenge tournament / team match | Arena official; others ours |
| 推图 / 凹伤 | stage pushing / damage-ranking play | Ours (slang) |

### Currencies and items

| Chinese | English | Status |
|---|---|---|
| 晨星 (players also say 钻石, 钻) | Dawnium | Inferred (premium currency earned in game) |
| 耀星 | Luminium | Inferred (paid currency, converts to Dawnium) |
| 罗拉 (金币) | Rolla | Official (same word) |
| 星之愿 | Stellatie | Inferred (standard skill pull) |
| 星之契 | Covenite | Inferred (premium skill pull) |
| 女神牌 (稀有 / 史诗 / 传说 / 奇迹) | Auroral Badge (Rare / Epic / Legendary / Mythic) | Inferred |
| 元素女神牌 | Auroral Elemental Badge | Inferred |
| 结缘绳 | Bond Trinket | Inferred (Fantomon pull) |
| 结缘水晶 (players: 爱心) | Summon Crystal | Inferred (60 buy one Mythic Fantomon) |
| 粗炼石 (铁矿) | Raw Ore | Inferred |
| 精锻石 | Refined Ore | Inferred |
| 历战精华 | Battle Essence | Inferred |
| 时之沙 (沙子) | Chrono Sand | Inferred |
| 冻干 | Treats | Inferred |
| 石材 / 木材 | Stone / Wood | Official |
| 命运果实 (苹果, 果子) | Destiny Fruit | Inferred |
| 时间水晶 (加速石) | Temporal Crystal | Inferred |
| 神铸石 | Divinecraft Stone | Inferred |
| 洗练石 | refinement stone | Ours |
| 技能兑换券 / 自选券 | Skill Shard Voucher | Inferred |
| 密保碎片 / 秘宝碎片 | Treasure Hunt skill shards | Ours |
| 世界树能量 | Aurodrasil Energy | Inferred |
| 原初之心 / 原初 | Primostar | Inferred |
| 国度币 | kingdom currency | Ours |
| 友情点 / 友情币 | friendship points | Ours |
| 公会币 | Guild Tokens | Inferred |
| 贺卡 | greeting card (home visiting) | Ours |
| 黄金甲虫 | Golden Beetle | Inferred |
| 幻行魔镜 | Shapeshifting Mirror | Inferred |
| 开图工具 / 清障道具: 钻头, 水雷, 钥匙, 积木 | map-opening tools: Magic Drill, Water Mine, Gateway Key, building block | First three inferred; block ours |
| 青草团子 | cheapest supply item (grass dumpling) | Ours |

### Systems

| Chinese | English | Status |
|---|---|---|
| 转职 / N转 | class change / tier N | Official concept |
| 战技 / 秘法 | Technique / Charm | Inferred (active / passive skill) |
| 祈愿 (常驻 / 高阶) | Prayer banner (standard / premium) | Inferred |
| 古遗物 / 遗物 / 圣遗物 | relic | Official |
| 时光扭蛋机 | relic gacha (Aeonic gacha) | Inferred |
| 遗物共鸣 / 遗物等级 | Relic Resonance | Inferred |
| 觉醒 | relic awakening | Official ("Awakened") |
| 幻兽 / 宠物 | Fantomon | Official |
| 幻兽实体化 | Adult Fantomon evolution | Inferred (same Lv 108) |
| 幻兽同调 (输出 / 辅助 / 守护) | Fantomon Sync (Output / Support / Guard) | Ours |
| 幻兽能力 / 天赋页 | Fantomon aptitudes / talent page | Inferred / ours |
| 伙伴 / 好感 | companion / affinity | Official |
| 星神伙伴 | star-god companion | Ours |
| 羁绊冒险 | Bond Adventure | Ours (already in our glossary) |
| 奇景委派 | Wonder Dispatch | Ours |
| 委托 | Commissions | Official |
| 素材秘境 | Material Realm | Official |
| 小推车 | Cart | Official |
| 家园 / 床 / 杂货 / 宝库 | Home / bed / Rolla shop / Dawnium shop | Home official; others descriptive |
| 神秘商人 (黑市商人) | Mysterious Merchant | Official |
| 交易行 / 拍卖行 | trading house / Auction House | Auction House official |
| 料理 / 食谱 | dishes / recipes | Official concept |
| 宝石 (红宝石, 黑曜石, 蓝宝石, 绿宝石) | gems (ruby, obsidian, sapphire, emerald) | Gems official; types ours |
| 强化 / 共鸣 | enhancement / gear resonance | Official concept |
| 洗练 | refinement (affix re-roll) | Inferred |
| 词条继承 | affix inheritance (affix transfer) | Inferred |
| 打底词条 / 四项基本词条 | base affixes / the four basic affixes | Ours |
| 秘宝大作战 | Grand Treasure Hunt | Inferred (same unique relics) |
| 星象合约 | Astral Pact | Inferred |
| 赛季评分 (玩法 / 养成 / 装备 / 总评) | season rating (gameplay / cultivation / gear / overall) | Ours |
| 大矿 | big mine (map mining node, 50 digs a week) | Ours |
| 虚烬重燃 | Embers Rekindled (boss event paying Mythic badges) | Ours |
| 家园拜访 | Home Visiting | Ours |
| 历程回响 | Journey Echo (finish old towers) | Ours |
| 平衡之美 | Beauty of Balance (PvP damping rule) | Ours |
| 战令 / 月卡 | battle pass / monthly card | Ours |

### Classes

| Chinese | English | Status |
|---|---|---|
| 法师 / 战士 | Mage / Warrior | Official |
| 术士 (nickname 鼠鼠) | Sorcerer | Official |
| 贤者 | Sage | Official |
| 斗士 | Duelist | Official (literal "fighter") |
| 骑士 | Knight | Official |
| 魔导师 | Archmage (tier 3 Sorcerer) | Inferred |
| 征服者 | Conqueror (tier 4 Duelist) | Inferred |
| 秘法先知 | Prophet (tier 5 Sage) | Inferred |
| 暗牧 | Shadow Priest (damage Sage) | Official style name |
| 奶妈 | healer Sage | Ours (slang) |
| 召唤流 | summoner build | Ours |
| 果盘 / 四色 | "fruit platter": mixed four-element Sorcerer build | Ours (slang) |
| 光法 / 火法 / 风法 / 水法 | Light / Fire / Wind / Water Sorcerer | Ours |

### Stats and states

| Chinese | English | Status |
|---|---|---|
| 战力 | CP (power) | Official |
| 白值 | flat ("white") value of a skill or stat | Ours |
| 倍率 | multiplier | Ours |
| 会心 / 会心伤害 (会伤) / 双暴 | Crit Rate / Crit Damage / double crit | Official stats |
| 会心抵抗 (会抗) | Crit Resistance | Inferred |
| 格挡 / 格挡伤害抵抗 | Block / block damage resistance (Block Efficiency ❓) | Block official |
| 精准 | Accuracy | Official |
| 效果命中 / 效果抵抗 | effect accuracy / effect resistance | Ours |
| 元素亲和 / 元素精通 | elemental affinity / elemental mastery | Ours |
| 伤害加成 / 伤害抵抗 | damage bonus / damage resistance | Ours |
| 附伤 | added damage (extra hits from passives) | Ours |
| 侵蚀 / 永夜 | Erosion / Eternal Night (tier-8 replacement) | Erosion official; Eternal Night ours |
| 撕裂 / 致盲 / 感电 / 冰冻 / 禁锢 (定身) / 致残 / 潮湿 / 灼烧 / 易伤 / 嘲讽 | Laceration / Blind / Shock / Freeze / Root / Cripple / Wet / Burn / Vulnerability / Taunt | Ours |
| 连携 | Link (tier-7 Sage mechanic) | Ours |
| 魔纹 / 魔印 | sigil (Sorcerer) / magic seal (Duelist) | Ours |
| 稀有 / 史诗 / 传说 / 奇迹 / 神话 | Rare / Epic / Legendary / Mythic / Divine | Inferred |
| 蓝 / 紫 / 橙 / 金 / 红 / 彩 | blue / purple / orange / gold / red / rainbow (skill and gear colour steps) | Ours |
| 零氪 / 微氪 / 中氪 / 氪佬 / 平民 | zero / light / mid / heavy spender / ordinary player | Ours |

### Fantomons and unique relics

| Chinese | English | Status |
|---|---|---|
| 暗夜帝王 (暗夜) | Nyxarchon | Inferred |
| 晨曦天使 (天使) | Aegiswing | Inferred |
| 竹林仙君 / 龙国熊猫 (熊猫) | Pandarial | Inferred |
| 森之妖精 | Sylvaerie | Inferred |
| 重装哈比 (哈比) | Armopi | Inferred, weak |
| 凯尔斯 | Kels | Inferred |
| 药师獭獭 (also 药师懒懒, 药师水獭) | Herbote | Inferred, weak |
| 曼德罗 | Mandragora | Inferred |
| 準 | Falko | Inferred, weak |
| 紫云 | Zeioletus | Inferred, weak |
| 山猪 | Boaro | Inferred, weak |
| 豆之助 | ❓ (Terragon by elimination: guess) | Unknown |
| 虹彩星灵 (星灵) | Iridescent Star Spirit | Ours |
| 幸运神像 | Lucky Statue | Inferred (same effect text) |
| 原初宝石 | Primal Gem | Inferred (same effect) |
| 黄金神木 | Golden Sacred Tree | Ours |
| 招财猫神像 | Lucky Cat Statue | Ours |
| 沙漏 | Hourglass | Ours |
| 远古熔炉 | Primal Forge | Inferred |
| 乾坤造化 / 道衍天机 | Celestial Crafts / Ethereal Oracle (Loong Haven relic pools 1 and 2) | Inferred |
| 曙光秘誓 | Dawn's Secret Oath (feather kingdom pool 1) | Ours |

Skill names: see [skills-cn.json](../../data/skills-cn.json) (each record says whether its English name is a
global name matched by meaning or our translation).

## BWIKI data: Legendary relic sets per kingdom

From the BWIKI home page [S-90]. Four 4-piece sets per kingdom; the id prefix shows the element (615/720 light,
616/722 dark, 617/724 wind, 618/726 water, 728 fire: our reading of the pattern). Set names are left in Chinese;
they are search keys, and no global names are known.

| Kingdom | Light set | Dark set | Wind set | Water set |
|---|---|---|---|---|
| 森之国 | 至高无上 | 永夜安魂曲 | 风之颂歌 | 悠闲的午后 |
| 山之国 | 拥抱太阳 | 魔力统御 | 我就是风暴 | 水中倒影 |
| 泽之国 | 神鸣稻光 | 百鬼夜行 | 三日月之风 | 尘浪翻涌 |
| 龙之国 | 仙道渺渺 | 天煞孤星 | 气象万千 | 四海甘露 |
| 羽之国 | 光辉奇点 | 万物溺于影中 | 悼天穹的风声 | 沧海的礼赞 |
| 哈帕迪 | 云后微光 | 沉溺幽夜 | 启程的飓风 | 海的收藏 |
| 伊格尼斯 | 光阴的刻度 | 愚妄潜行 | 翻飞的流年 | (none listed; a fire set 如烟火初燃 instead) |

Cross-kingdom sets ("其他"): 四国的意志 (one token from each of the first four kingdoms: 圣树勇者之证, 古老石板,
源水御守, 金龙令牌), and three Mythic sets 极乐光域 (light: 零号力源, 启迪之慧果, 丰饶无虞之角, 光明之巅), 亘古黑暗
(dark) and 无界不至之风 (wind). Loong Haven Mythic sets named on relic pages: 天道神光, 光明遍照. A BWIKI community
post on the forest sets says: 至高无上 for short bursts, 永夜安魂曲 for long fights, 风之颂歌 for multi-hit builds,
悠闲的午后 for survival [S-90].

Dungeons per kingdom on the same page: forest 1 (世界之树), mountain 1 (机神山), marsh 3, Loong Haven 5, feather
kingdom 7, Hapadi 7, Ignis 7: the full list is in [future-content](../../systems/future-content.md).

## Pages worth re-reading later

| When | URL | Why |
|---|---|---|
| Before each global season change | https://www.gamekee.com/zjcs/687197.html | Unlock timeline by server day; check whether S4+ days were corrected |
| Before each global season change | https://www.gamekee.com/zjcs/679101.html | Dungeon thresholds; S5 and S6 rows were missing on 2026-11-18 |
| Before each global season change | https://news.17173.com/content/01012026/083707715.shtml and https://news.17173.com/content/05052026/151029904.shtml | Season-change checklists |
| When a new tier nears | https://www.taptap.cn/app/717836/strategy/entity-collection/277421 (Sorcerer), https://www.taptap.cn/app/717836/strategy/entity-collection/272820 (Sage), https://www.taptap.cn/app/717836/strategy/entity-collection/277420 (Duelist) | Newest build guide per tier |
| When a new tier nears | https://www.taptap.cn/moment/695465084507392826 | "Full skill codex, kept updated" (not read: probably images) |
| Monthly | https://www.taptap.cn/app/717836/strategy | Hub: new pinned guides and event posts |
| Monthly | https://www.taptap.cn/moment/713549377435602271 and its successors (the "弯路合集" series) | Veteran advice per season |
| Monthly | https://wiki.biligame.com/zjcswiki/%E9%A6%96%E9%A1%B5 | BWIKI home: watch for the kingdom, skill and dungeon pages being filled; a future Season 6 tab would give the kingdom name |
| Monthly | https://wiki.biligame.com/zjcswiki/api.php?action=query&list=allpages&aplimit=500 | Cheap check of how many BWIKI pages exist (33 on 2026-11-18) |
| On demand | https://wiki.biligame.com/zjcswiki/%E6%8A%80%E8%83%BD%E6%80%BB%E8%A7%88 and https://wiki.biligame.com/zjcswiki/%E9%81%97%E7%89%A9%E6%80%BB%E8%A7%88 | Skill and relic overview tables (10 rows visible today) |
| On demand | https://www.taptap.cn/moment/808741946083246280 | Fantomons and sync |
| On demand | https://www.taptap.cn/moment/869743882454173463 | Tier-9 leak thread: the first sign of CN Season 7 |
| On demand | https://www.233leyuan.com/ (search the game circle for "停服维护公告") | Reposts of official maintenance notices, the only official wording found |

## Open questions

- ❓ Season 6 name and kingdom; unlock levels of tiers 7 and 8; CN titles of class tiers 3-8 for most lines.
- ❓ Whether the JP version (Gamerch) follows the CN calendar with the same day offsets: not read in this pass.
- ❓ The CN-to-global Fantomon and skill name matches marked "Inferred": confirm from icons or in-game text.
- ❓ A string 艾珀希 appears next to "tier-8 Knight" in two post previews; it may be a place name or an author's
  name. Not used.

## Sources

- [S-90] BWIKI zjcswiki, pages cached in `raw/bwiki/` (gitignored)
- [S-91] GameKee zjcs wiki pages 687197, 679101, 689421
- [S-92] to [S-95] TapTap CN posts listed in the register fragment above
- [S-96] 17173 articles listed above; [S-97] reposted official notices
- [S-63], [S-64], [S-68] as defined in [provenance](../provenance.md)
- [S-01], [S-02], [S-03] for the official English terms
