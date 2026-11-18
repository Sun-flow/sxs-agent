# Official site (swordxstaff.boltray.com): post-by-post notes

<!-- index: Every news post on the publisher's site, with the facts it states and the page each belongs in -->

> **Summary:** The publisher's site has a short news list (12 posts with content, ids 186 to 203) and no FAQ or patch notes. The two "Handbook" posts and one "Tips" post are the only tier A statements we have on unlock levels, gear, the Cart, guild donations and Fantomons. Everything here is tagged [S-87].
> **Applies:** launch period, Season 1 (posts dated 2026-04-10 to 2026-06-05)
> **Related:** [eog notes](eog.md), [lootandwaifus notes](lootandwaifus.md), [Source register](../README.md), [Levels and unlocks](../../systems/levels-and-unlocks.md)

## How this source was read

- robots.txt allows everything except `/api/`. We did not request `/api/`. [S-87]
- The site is server-rendered; each post is plain HTML. Posts were found by walking the news list and post ids 185 to 203. Ids with no content were skipped; id 185 is a Chinese carousel stub.
- Tier: A (publisher). Marketing counts ("over 200 skills", "5M players") are claims, not measurements.
- The top-up page was fetched for its layout only. The gift-code page sits on another host (webcp01.boltray.com) and was not fetched.
- Raw copies: `knowledge/sources/raw/official/` (gitignored).

## Post 186 (2026-04-10): pre-registration

- Pre-registration opened on 26 March (UTC-5). [S-87]
- "Over 200 skills" at this date. Kingdoms named: Verdantglade, Cinder Ridge, Aqualis, Loong Haven. [S-87]
- The Traveling Merchant can appear while the player is offline. [S-87]

## Post 190 (2026-05-06): launch date

- Launch set for 19 May 2026. The post claims 5 million players. Pre-registration event ran 27 March to 19 May. [S-87]

## Posts 191, 192, 193, 194, 195, 197: world and characters

- Five kingdoms in the lore, one of them the lost Aethyris. Towns and places named: Drasilgard, Fortburg, Onsengo, Hellhollow. Peoples: Dryason, Merean, Loongborn. [S-87]
- Features named: Portal, Floating Island Home, Puzzle Ruins, Chaos, and the Voyage Obelisk as a passage between Kingdoms. Destiny Fruit comes from the Arborisfatum. [S-87]
- Characters named: Molly, Akane, Reina, Narss (Chief), Hermes, Qin, Killian, the Mysterious Merchant, Naira, Micaela, Karlos, Braulio, Mateo, Mio, Mayoi, Osawa Eiichi, Hanayama Suzu, Juubee. [S-87]
- Hieromons, one per kingdom: Storm Griffin (Verdantglade), Flamoenix (Cinder Ridge), Yamata no Orochi (Aqualis), Primordial Loong (Loong Haven). [S-87]

## Post 196: Handbook Vol. 1 (gear, skills, Cart, Bed, statues)

- Gear starts with 4 slots. The Off-hand slot opens after reaching Class II. Belongs in `systems/gear.md`. [S-87]
- Item level sets base stats; rarity sets multipliers. Primary stats are fixed; secondary and bonus stats are random. [S-87]
- Enhancement belongs to the slot, not the item, so it survives a gear swap. The cap rises with character level. [S-87]
- Every 5 enhancement levels across all slots unlocks a Resonance step (a percent boost to base stats), so upgrade slots evenly. [S-87]
- Dismantle unlocks at Lv 12: the Alchemy Pot at Home turns gear into Refined Ores and Raw Ores. Belongs in `systems/levels-and-unlocks.md`. [S-87]
- A loadout has 4 Techniques and 4 Charms. Battle Essence upgrades skill slots; there is a Quick Upgrade button. [S-87]
- Cart resource level caps depend on Blessing Level. Advice: raise all Cart resources to Lv 10 first, then Wood and Stone. Goddess Statues and the Monthly Pass raise production. [S-87]
- Idle rewards stop growing at 36 hours. [S-87]
- Bed: one free speed-up a day. A Temporal Crystal gives 2 hours of Bed and Cart output. Activate every statue you can before using speed-ups. [S-87]
- Exploring a map sector to 100% activates its Goddess Statue. Main-story statues raise Blessing Level (Cart caps, base Bed EXP). Lost Goddess Statues add resource and EXP boosts. Exploration items are sold in Kingdom Shops. Belongs in `systems/goddess-statues.md`. [S-87]

## Post 198: Handbook Vol. 2 (Vendor Booth, guild, realms)

- Vendor Booth unlocks at Lv 20. Buy Wood, Stone and Quest Scrolls first. The Vault tab sells discounted Stellaties, Iron Hammers, Gold Pickaxes and Worn Knuckles. Belongs in `systems/shops.md` and `systems/levels-and-unlocks.md`. [S-87]
- Guild Donation is available after joining a guild at Lv 15. It gives Guild Tokens plus Steel, Kanstein Cells and Mana Clusters. Up to 5 a day, 1 free. The post recommends paying 70 Dawnium for two more. Belongs in `systems/guild.md`. [S-87]
- The Guild Shop sells discounted items and Fantomon growth materials. [S-87]
- Destiny Exploration can summon Molly or the Mysterious Merchant to Home; the post warns some of their deals are poor. [S-87]
- Material Realm rewards scale with Rank, so save attempts for a higher Rank. Belongs in `systems/material-realms.md`. [S-87]

## Post 199: Tips (relics, statues, Arena, Commercium, Fantomons)

- Destiny Fruits used in exploration also dig up that region's Relics. The Relic Set screen shows missing pieces and where they are. The nearest Goddess Statue lists the region's relics. [S-87]
- Statue of Witch and Statue of the Brave can be used once a day and may give a Stellatie or a lightning bolt. [S-87]
- Tapping Home objects (blossoms, birds, moles) gives small rewards. A mimic chest's attack is dodged by tapping nearby ground. [S-87]
- Grand Arena is in Cinder Ridge and opens at Lv 40 with Rank Advancement. It uses Arena Tickets; save tickets before the weekly reset and use them early in the new season. Belongs in `systems/arena-and-pvp.md`. [S-87]
- Commercium opens at Lv 40, reached by the airship at the western edge of Home. It holds the Trading House and the Auction House; bidding on premium gear needs Luminium. [S-87]
- Fantomons unlock at character Lv 50: summon at the Arborisfatum; Summon Crystals buy Mythics; the Arena Shop sells shards; Treats level them. Only the 4 deployed need levels, and Resonance Level equals the lowest of them. A deployed Fantomon picks up loot automatically. Belongs in `systems/fantomons.md`. [S-87]

## Post 200 (2026-05-19): launch

- "300+ skills" and five kingdoms at launch. [S-87]
- Voice of Kanstein event: 19 May 13:00 UTC to 2 June 13:00 UTC. Official community: r/SwordxStaff_Official. [S-87]

## Post 203 (2026-06-05): KonoSuba 3 collaboration

- Runs 2 to 15 June 2026: daily sign-in, Arcane Wheel, and events named "God's Blessing On This World of Swords and Staffs!", Lost Memories and Monster Conquest. Visages: Otherworldly Adventurer and Crusader. Belongs in `systems/events.md`. [S-87]

## Where gap-filling facts belong

| Gap | Answer | Target page |
|---|---|---|
| Vendor Booth 18 or 20 | 20, per the publisher | `systems/levels-and-unlocks.md` |
| Guild 15 or 20 | 15 | `systems/levels-and-unlocks.md`, `systems/guild.md` |
| Fantomons 50 or 51 | 50 | `systems/levels-and-unlocks.md`, `systems/fantomons.md` |
| When Dismantle opens | Lv 12 | `systems/levels-and-unlocks.md` |
| Arena and Commercium level | Lv 40 | `systems/levels-and-unlocks.md` |
| Off-hand slot | After Class II | `systems/gear.md` |
| Donations per day | Up to 5, 1 free; 70 Dawnium for two more | `systems/guild.md` |
| Idle cap | 36 hours | `systems/cart-and-home.md` |
| Temporal Crystal value | 2 hours of Bed and Cart | `systems/currencies.md` |

## Conflicts

- Skill count: "over 200" in April, "300+" at launch [S-87]. Marketing figures; eog lists 361 [S-85].
- Vendor Booth: 20 here [S-87] against 18 in rule R-011 (our account met it early through a tutorial).
- Fantomons: 50 here [S-87] against 51 in rule R-011.
- Donations: up to 5 with 1 free [S-87] against eog's 3 free [S-85].

## Open questions

- ❓ The exact Dawnium ladder for donations 2 to 5: the post names only "70 for two additional attempts".
- ❓ What Rank Advancement the Grand Arena needs besides Lv 40.
- ❓ Whether newer posts exist after id 203: none were listed on 2026-11-18.
- ❓ Gift codes on the official redeem host: not fetched.

## Sources

- [S-87] swordxstaff.boltray.com news posts 186, 190 to 200 and 203, home and news list, seen 2026-11-18. Not yet in the register; row proposed to the lead.
- [S-85] eog.gg, see [eog.md](eog.md).
