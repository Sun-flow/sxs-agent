# Cooking and dishes

<!-- index: Read when cooking in the Alchemy Pot, healing with food, or deciding whether to eat or sell a stat dish -->

> **Summary:** Three kinds of food. Healing dishes are cheap (Rolla plus gathered plants): cook and use them freely. Temporary buff dishes last a number of battles and do not expire: keep them for hard fights. Permanent dishes add stats for good with falling returns (full value for the first 10 of one dish, then 50%, 20%, 5%): conserve them, never eat them without a plan.
> **Applies:** all seasons; Alchemy Pot unlocks with house furniture at Lv 7
> **Related:** [Cart and home](cart-and-home.md), [Auction house](auction-house.md), [Commissions](commissions.md), [Shops](shops.md), rules R-047, R-061, R-138, R-165

## The Alchemy Pot

- House furniture, unlocked at Lv 7 [R-047]. Tabs: Dish / Combine / Dismantle / Goals [R-165].
- Dish tab: pick a recipe, the ingredients show at the top, press Cook [R-047].
- Tapping an ingredient on the cooking screen sends you to the map spot where it is gathered [S-31].
- The Goals tab has Dish and Dismantle milestones, free to claim [R-165].
- Dismantle (gear into ore) is covered in [Cart and home](cart-and-home.md) and rule R-165.

## Three kinds of food

| Kind | Effect | Cost and source | How to use | Source |
|---|---|---|---|---|
| Healing | restores HP, no stats | Rolla and farmable plants; a stronger type with each new region | freely: before fights, at dungeon camps | [R-138][S-31] |
| Temporary buff | a boost for a set number of battles, often tied to a region or fight type | cooked from recipes; recipes also sold in the Kingdom Shop | read the description; hold until a hard fight (they do not expire) | [S-31] |
| Permanent | permanent stats | Auction House (Luminium), Arena shop; recipes from the Auction House, Guild Clash, sometimes commissions or the Mysterious Merchant | conserve; eat with a plan | [R-138][S-31] |

- Healing dishes can be crafted without limit for Rolla; that spending is approved for the bot [R-138].
- Permanent dishes sit in the "Dishes" menu reached from the character portrait; the bot never uses them on its
  own [R-138].
- Going home also restores HP [S-31]; the bot heals to 70% before any fight [R-061].
- Buff food lasts a number of battles, not a time; food has no inventory cap and does not expire; permanent food
  raises HP, ATK, DEF or SPD; recipes come from Commissions and the Auction House [S-85].
- Counts: zeroluck's data has 67 recipes (5 recovery, 62 buff) [S-80]; eog's database has 87 dishes over all
  kingdoms, including later seasons and limited ones [S-85]. Both are tier C and the totals differ, probably
  because eog reads future content from the Chinese server ❓.
- Each dish has a proficiency up to Lv 5, and a buff dish gets stronger the more it is cooked [S-80].

## Permanent dishes: falling returns

The stats from one more dish depend on how many of that same dish you have already eaten [S-31][S-85]:

| Number eaten of one dish | Value of each |
|---|---|
| 1 to 10 | 100% |
| 11 to 30 | 50% |
| 31 to 50 | 20% |
| 51 and up | 5% |

So the first 10 of every different permanent dish are worth the most: spread across dishes before stacking one.
The counter is per recipe, not per stat [S-85]. A second tier C source now gives the same brackets for the live game [S-85].
Recipes from Premium Commissions can be sold instead [S-01]; see [Auction house](auction-house.md).

## Known dishes

| Dish | Kind | Effect | Where seen | Source |
|---|---|---|---|---|
| Green Riceball | healing | restores 8% + 1,000 HP | Alchemy Pot; code ZJ999 gives 50 | [R-047][S-37] |
| Jelly Bean Pals | buff [S-80] | stat not shown ❓ (eog's "Candy Bean Figure", Water 1 + Flour 10, DEF +10%, may be the same dish ❓ [S-85]) | Alchemy Pot's second recipe; code ZJ999 gives 2 | [R-047][S-37][S-80] |
| Honeyed Roast | ❓ | ❓ | code ZJ999 gives 3 | [S-37] |
| Cheerful Greens | buff [S-80] | stat not shown ❓ | recipe in Hermes's Kingdom Shop, 600 leaves | [R-134][S-80] |
| Stewed Meat and Potatoes | ❓ (recipe) | ❓ | recipe in Hermes's Kingdom Shop, 600 leaves | [R-134] |

- Recovery dishes named in the game data [S-80]: Green Rice Ball (our "Green Riceball"), Chargrilled Mushroom,
  Verdant Dew, Shepherd's Purse Pancake (all restore HP) and Starlight Bread (restores Stamina, although the site
  files it under "Restore HP").
- Buff dishes named [S-80]: Stir-Fried Cabbage, Adventurer's Special Platter, Wonder Skewers (ATK); Wonder Hotpot
  (DEF).
- Full list with kingdom, rarity, combat buff, permanent boost and ingredients:
  [recipe-database.json](../data/recipe-database.json) (87 dishes); ingredient list:
  [ingredients.json](../data/ingredients.json) (drop sources unknown). Names there are eog's translations and may
  differ from our client [S-85].

## Ingredients

| Ingredient | Source | Price | Source tag |
|---|---|---|---|
| Water | Vendor Booth General tab | 500 Rolla | [R-120] |
| Flour | Hermes's Kingdom Shop | 50 leaves (limit 50) | [R-134] |
| Potato | Hermes's Kingdom Shop | 50 leaves (limit 50) | [R-134] |
| Plants and other field ingredients | overworld pickups; blue-aura pickups give bonus ingredients | free or 5 stamina | [R-122][S-31] |
| Monster drops (e.g. "Vital Thornballs" in a commission) ❓ | overworld | | [S-01] |

Gems can also be found in the open world "like ingredients" from Season 2 [S-02].

## What to do

1. Keep a stock of the current region's healing dish for exploring and tower runs [R-047][S-31].
2. Buy ingredient staples only for a recipe you cook; kingdom currency goes to kingdom tools first
   ([Shops](shops.md#kingdom-shops)).
3. Hold temporary buff dishes for walls: a dungeon threshold, a boss, an event ranking [S-31].
4. Treat permanent dishes and their recipes as valuables: eat up to 10 of each kind for full value, or sell.

## Open questions
- ❓ Matching eog's translated dish names in [recipe-database.json](../data/recipe-database.json) to our client's names; healing values and battles-applied counts (not in the source).
- ❓ Kind and effect of Honeyed Roast and Stewed Meat and Potatoes; the buffed stat of Jelly Bean Pals and Cheerful Greens.
- ❓ Where each ingredient drops and at what chance.
- ❓ Rolla cost per healing dish.
- ❓ The falling-returns table seen in our own game (two tier C sources agree [S-31][S-85]).
- ❓ What the Combine tab makes.

## Sources
- [S-01] commission screenshot, recipes to sell
- [S-02] Section VI (Gems)
- [S-31] food guide (types, sources, efficiency table)
- [S-37] code rewards
- [S-80] zeroluck life-skills page (recipe counts, recovery and buff dish names, proficiency)
- [S-85] eog food guide and recipe database ([recipe-database.json](../data/recipe-database.json))
- Rules R-047, R-061, R-120, R-122, R-134, R-138, R-165
