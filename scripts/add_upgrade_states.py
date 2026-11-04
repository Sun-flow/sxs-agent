"""One-off: add the upgrade-system screens to resource/pipeline/state.json (kept for the record; safe to re-run)."""

import json
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "resource" / "pipeline" / "state.json"
TITLE = [0, 20, 440, 70]

NEW = {
    "State.SkillPage": ("Skill page (Character > Skill): techniques left, charms right, Quick Upgrade beside the "
                        "lower-right charm, Loadout switcher, Technique/Charm/Shard tabs (R-080, R-104).",
                        r"^Loadout \d", [200, 670, 320, 60]),
    "State.TechniqueUpgrade": ("A technique's Upgrade (Battle Essence) or Ascension (its own shards) tab.",
                               r"^(Upgrade|Ascension)$", TITLE),
    "State.UpgradeGoals": ("Goals tab of an upgrade screen (Skill, Quality, Enhancement, Level, Power, Total Class "
                           "Level goals): free Claim buttons.",
                           r"(Skill|Quality|Enhancement|Level|Power) Goals$|^Total Class Level$", TITLE),
    "State.ClassPage": ("Class screen (Change Class, Class Hierarchy, Goals tabs) and a class's Info/Upgrade page. "
                        "Change Class is mae's decision: never tapped.",
                        r"^Class$|Class ?Level|^Total Level$", [0, 0, 720, 420]),
    "State.RankAdvancement": ("Rank Advancement (the Apprentice badge on Character): raises the level cap; costs "
                              "ore, Bellflowers and Rolla.", r"Rank Advancement", TITLE),
    "State.GearResonance": ("Gear Resonance (Enhance Gear > Resonance): free stat bonuses when all 4 pieces reach "
                            "+5, +10, ...; Activate claims one.", r"^Gear Resonance$", TITLE),
    "State.MapExploration": ("Journal > Map Exploration: Resource Hunt card with stamina, 4 material choices "
                             "(Rolla, ore, sand, Battle Essence) and Go (R-108).", r"^Map Exploration$", TITLE),
}
# Insert before these (title OCR screens go after the full-screen overlays and before State.Unknown).
AFTER = "State.EnhanceGear"

data = json.loads(PATH.read_text(encoding="utf-8"))
order = data["State.Detect"]["custom_action_param"]["order"]
for name, (doc, expected, roi) in NEW.items():
    data[name] = {"doc": doc, "recognition": "OCR", "expected": expected, "roi": roi, "pre_delay": 0,
                  "post_delay": 0}
    if name not in order:
        order.insert(order.index(AFTER) + 1, name)
PATH.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok", len(order))
