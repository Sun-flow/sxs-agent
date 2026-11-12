"""Sequence Capture: record approach sequences of world collectibles for detector training data. No model calls.

    python -m sxs seqcap --job NAME [--steps "hunt:ore,statue:Troll Lair,pickups:Grotto Peninsula"] [--minutes 40]
    python -m sxs seqcap --job NAME --resume        # carry on a stopped job where it left off

Plan: docs/collectibles-capture-plan.md (mae, 2026-11-11: collectibles in the world with the frames leading up to
collection, for the Roboflow detector).

How it works:
- A **pre-roll buffer** (`Recorder`) keeps every frame the bot takes plus one every SAMPLE_S from a sampler thread,
  for the last PRE_S seconds. When a leg collects something (a pickup's reward popup, an object cleared, a card
  acted on, a wheel), the buffer from PRE_S before to POST_S after is saved as one sequence:
  captures/sequences/<job>/seq_<kind>_<zone>_<nn>/fNN.png with frames.json. Nobody has to start a burst by hand.
- A job is a list of steps (mae's answers, 2026-11-11), run in order:
  - `hunt:MATERIAL` (ore, sand, rolla, essence): stamina-costing exemplars through the Resource Hunt route, a few
    pickups each (`--per-material`), only above `--keep` stamina (150). Essence comes from monster fights.
  - `statue:ZONE`: walk to the statue icon nearest us in the zone; the walk is the sequence (statue not tapped).
  - `pickups:ZONE`: Clear Zone (`sxs/loops/clear.py`) with legs to free pickups only (minimap item dots and known
    collectible crops). Legs to item and monster dots (minimap, then big map; mae 19:44: monsters saved like interactables); no quest-ring, guard or frontier legs; the statue is blessed at 100% (allowed).
    Clear Zone refuses explored zones, where pickups cost stamina (R-065).
- **Stamina drops on free legs** are not a stop (mae): the pre-roll of the cause is saved as a stamina_drop sequence
  and listed in job.json under stamina_drops for the report.
- **Pausable**: the job file captures/sequences/<job>/job.json is written after every saved sequence and step, and a
  sequence folder appears only when complete (written as .part, then renamed). Stop any time (Ctrl+C, close the
  laptop, the emulator dropping); `--resume` carries on from the first unfinished step.
- `--pick N` (default 5) copies N frames of each sequence (first sight, middle, near, the collect moment, the
  reward) as 256-colour PNGs into docs/screens/sequences/<seq>/ for committing and boxing in the labeler.

Account name: never in file or folder names (zone names only). The dataset export blacks out the name on frames.
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
from collections import deque
from pathlib import Path
from typing import Optional

import cv2

from ..core.loop import Loop, banner, progress
from ..core.paths import CAPTURES, SCREENS
from ..vision import collectibles, minimap
from ..vision.hud import read_stamina
from ..vision.player import player_on_screen
from . import clear

log = logging.getLogger("sxs.loops.seqcap")

PRE_S = 10.0  # seconds of frames kept before the collect moment
POST_S = 3.0  # seconds after it (the reward popup)
SAMPLE_S = 0.5  # sampler thread: one frame this often, on top of the frames the walk takes itself
MAX_FRAMES = 24  # frames kept per sequence (evenly thinned when the buffer holds more)
MERGE_S = 4.0  # events this close together are one sequence (a leg's "pickup" then "cleared")
COLLECT_EVENTS = {"pickup": "pickup", "cleared": "pickup", "acted": "object", "wheel": "wheel", "fight": "monster"}
ROOT = CAPTURES / "sequences"
PICKS = SCREENS / "sequences"
STAMINA_DROP_READS = 2  # readings in a row below the last good one before a drop counts (OCR slips)


def slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (t or "unknown").lower()).strip("_")[:30] or "unknown"


# ---------------------------------------------------------------- the job file
class Job:
    def __init__(self, name: str):
        self.name = name
        self.dir = ROOT / name
        self.file = self.dir / "job.json"
        self.data = {"job": name, "target": 30, "steps": [], "sequences": [], "stamina_drops": [], "runs": []}
        self.lock = threading.Lock()

    @classmethod
    def open(cls, name: str, resume: bool, target: int, steps: list[dict]) -> "Job":
        job = cls(name)
        if job.file.exists():
            if not resume:
                raise FileExistsError(f"job {name!r} exists ({job.file}); pass --resume to carry it on")
            job.data = json.loads(job.file.read_text(encoding="utf-8"))
        else:
            job.data.update(target=target, steps=steps)
        for p in job.dir.glob("*.part"):  # a sequence cut off by a stop: never half kept
            for f in p.iterdir():
                f.unlink()
            p.rmdir()
        job.data["runs"].append({"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "status": "running"})
        job.save()
        return job

    def save(self) -> None:
        with self.lock:
            self.dir.mkdir(parents=True, exist_ok=True)
            tmp = self.file.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, indent=1) + "\n", encoding="utf-8")
            tmp.replace(self.file)

    @property
    def count(self) -> int:
        return len(self.data["sequences"])

    @property
    def done(self) -> bool:
        return self.count >= self.data["target"]

    def next_name(self, kind: str, zone: str) -> str:
        return f"seq_{slug(kind)}_{slug(zone)}_{self.count + 1:02d}"

    def end_run(self, status: str) -> None:
        self.data["runs"][-1].update(ended=time.strftime("%Y-%m-%dT%H:%M:%S"), status=status)
        self.save()


# ---------------------------------------------------------------- the pre-roll buffer
class Recorder:
    """Wraps dev.screenshot so every frame the bot takes is kept, plus a sampler thread, for the last PRE_S s."""

    def __init__(self, dev, job: Job, picks: int = 5):
        self.dev, self.job, self.picks = dev, job, picks
        self.buf: deque = deque()
        self.lock = threading.Lock()
        self.pending: list[dict] = []  # {"t", "kind", "zone", "what"}
        self.stop_ev = threading.Event()
        self.orig = dev.screenshot
        self.thread = threading.Thread(target=self._sample, name="seqcap-sampler", daemon=True)
        self.errors = 0

    def shot(self):
        with self.lock:
            frame = self.orig().copy()
            now = time.time()
            self.buf.append((now, frame))
            while self.buf and self.buf[0][0] < now - PRE_S - POST_S - 2:
                self.buf.popleft()
        return frame

    def start(self) -> None:
        self.dev.screenshot = self.shot  # every caller (the detector included) now records
        self.thread.start()

    def stop(self, flush: bool = True) -> None:
        if flush:
            deadline = time.time() + POST_S + 1
            while self.pending and time.time() < deadline:
                time.sleep(0.2)
        self.stop_ev.set()
        self.thread.join(timeout=5)
        self.dev.screenshot = self.orig
        if self.pending:
            self._write_due(force=True)

    def mark(self, kind: str, zone: str, what: str, force: bool = False) -> None:
        now = time.time()
        if not force and self.pending and now - self.pending[-1]["t"] < MERGE_S:
            return  # the same collect (a reward popup, then the dot gone from the minimap)
        self.pending.append({"t": now, "kind": kind, "zone": zone, "what": what})
        log.info("collect seen (%s, %s): saving the last %.0f s and the next %.0f s", kind, what, PRE_S, POST_S)

    def _sample(self) -> None:
        while not self.stop_ev.wait(SAMPLE_S):
            try:
                self.shot()
                self.errors = 0
            except Exception as e:  # the emulator went away (laptop closed): the main thread stops too
                self.errors += 1
                if self.errors in (1, 10):
                    log.warning("sampler: screenshot failed (%s)", e)
            self._write_due()

    def _write_due(self, force: bool = False) -> None:
        now = time.time()
        while self.pending and (force or now >= self.pending[0]["t"] + POST_S):
            ev = self.pending.pop(0)
            with self.lock:
                frames = [(t, f) for t, f in self.buf if ev["t"] - PRE_S <= t <= ev["t"] + POST_S]
            try:
                self._write(ev, frames)
            except Exception as e:
                log.warning("sequence not saved: %s", e)

    def _write(self, ev: dict, frames: list) -> None:
        if len(frames) < 4:
            log.info("only %d frames round the collect: sequence skipped", len(frames))
            return
        if len(frames) > MAX_FRAMES:
            step = (len(frames) - 1) / (MAX_FRAMES - 1)
            frames = [frames[round(i * step)] for i in range(MAX_FRAMES)]
        name = self.job.next_name(ev["kind"], ev["zone"])
        part = self.job.dir / f"{name}.part"
        part.mkdir(parents=True, exist_ok=True)
        rows = []
        for i, (t, f) in enumerate(frames, 1):
            fn = f"{name}_f{i:02d}.png"
            cv2.imwrite(str(part / fn), f)
            rows.append({"file": fn, "t": round(t - ev["t"], 2)})
        meta = {"name": name, "kind": ev["kind"], "zone": ev["zone"], "what": ev["what"],
                "at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ev["t"])), "frames": rows}
        (part / "frames.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
        final = self.job.dir / name
        part.replace(final)
        picked = pick(final, meta, self.picks) if self.picks else []
        self.job.data["sequences"].append({k: meta[k] for k in ("name", "kind", "zone", "what", "at")}
                                          | {"frames": len(rows), "picked": len(picked)})
        self.job.save()
        log.info("[sequence %d/%d] %s: %d frames, %d picked", self.job.count, self.job.data["target"], name,
                 len(rows), len(picked))
        progress(("sequence", self.job.count))


def pick(folder: Path, meta: dict, n: int) -> list[Path]:
    """Copy n frames of a sequence into docs/screens/sequences/<name>/: evenly spread over the approach, always
    including the first, the last before the collect, and the last (the reward)."""
    from PIL import Image

    rows = meta["frames"]
    before = [i for i, r in enumerate(rows) if r["t"] <= 0] or [0]
    idx = {0, before[-1], len(rows) - 1}
    k = max(0, n - len(idx))
    span = before[-1]
    idx |= {round(span * (j + 1) / (k + 1)) for j in range(k)}
    out = PICKS / meta["name"]
    out.mkdir(parents=True, exist_ok=True)
    saved = []
    for i in sorted(idx)[:n + 1]:
        src = folder / rows[i]["file"]
        rgb = Image.open(src).convert("RGB")
        dst = out / rows[i]["file"]
        rgb.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(dst, optimize=True)
        saved.append(dst)
    (out / "frames.json").write_text(json.dumps(
        {k: meta[k] for k in ("name", "kind", "zone", "what", "at")}
        | {"picked": [rows[i] for i in sorted(idx)[:n + 1]]}, indent=1) + "\n", encoding="utf-8")
    return saved


# ---------------------------------------------------------------- Clear Zone, pickups only
class CaptureClearer(clear.Clearer):
    """Clear Zone with legs to pickups only (mae, 2026-11-11: no quest-ring legs to start; blessing a statue at 100%
    is fine, it opens new areas)."""
    MINIMAP_GOALS = ("item", "monster")  # mae (19:44): monsters are fine targets, saved like interactables
    BIG_MAP_GOALS = ("item", "monster")  # live 2026-11-11: minimap-only legs found nothing in Grotto Peninsula or XIII

    def __init__(self, dev, det, area, rec: "Recorder", job: Job):
        super().__init__(dev, det, area)
        self.frontier_used = clear.FRONTIER_LEGS  # no fog legs: capture walks to pickups only
        self.rec, self.job = rec, job
        self.stamina: Optional[int] = None
        self.low_reads = 0

    def here(self) -> str:
        """The zone we actually stand in, for the sequence name (live 2026-11-11: a Grotto Peninsula monster was
        filed under Hurricane Heights, the zone the step was aiming for)."""
        from ..actions import goto
        try:
            return goto.area_name_here(self.det) or self.home or "unknown"
        except Exception:
            return self.home or "unknown"

    def event(self, name: str) -> None:
        super().event(name)
        kind = COLLECT_EVENTS.get(name)
        if kind:
            what = self.leg.what if self.leg else name
            if name == "acted" and self.last_card:
                kind = slug(self.last_card)
            self.rec.mark(kind, self.here(), what)

    def guard_stamina(self) -> None:
        """mae (2026-11-11): a stamina drop on a free-pickup leg is not a stop. Save the pre-roll of what caused it
        as a stamina_drop sequence, note it in the job file for the report, and carry on."""
        s = read_stamina(self.det)
        if s is None:
            return
        if self.stamina is None or s >= self.stamina:
            self.stamina, self.low_reads = s, 0
            return
        self.low_reads += 1
        if self.low_reads >= STAMINA_DROP_READS:
            last = self.legs[-1] if self.legs else None
            what = f"after leg {last.n}: {last.what} ({last.result})" if last else "before the first leg"
            log.warning("stamina dropped %d -> %d %s: saving the pre-roll as stamina_drop", self.stamina, s, what)
            self.job.data["stamina_drops"].append({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "zone": self.home,
                                                   "from": self.stamina, "to": s, "what": what})
            self.job.save()
            self.rec.mark("stamina_drop", self.home or "unknown", what, force=True)
            self.stamina, self.low_reads = s, 0

    def finish_object(self, leg, spot, goal: str) -> None:
        """Clear Zone records an object gone from the minimap straight into the leg, not through event() (live
        2026-11-11: a Hurricane Heights monster "taken" this way saved no sequence)."""
        super().finish_object(leg, spot, goal)
        if "cleared" in leg.events:
            self.rec.mark("monster" if goal == "monster" else "pickup", self.here(), leg.what)

    def try_known(self, frame, xy, me):
        for name, kind, point, score in collectibles.find(frame, explored=False, area=self.home or "",
                                                          kinds=("collectible",)):
            spot = clear.mapnav.to_world(xy, me, point)
            if self.failed_spot(spot):
                continue
            leg = self.start_leg("known", f"{kind} {name!r} ({score:.2f})", spot)
            self.tapped = (frame, point, kind)
            self.leg_tap(point)
            return leg
        return None

    def plan(self):
        self.guard_stamina()
        frame = self.dev.screenshot()
        xy, me = clear._xy(self.det), player_on_screen(self.det, frame)
        return self.try_known(frame, xy, me) or self.try_minimap(frame, xy, me) or self.try_big_map()


# ---------------------------------------------------------------- stamina nodes (Resource Hunt)
def hunt(dev, det, rec: "Recorder", material: str, pickups: int, keep: int) -> str:
    """Stamina-costing exemplars (mae, 2026-11-11): ore, sand, Rolla, and essence (monster fights in a blessed area)
    through the Resource Hunt route, a few pickups each, only above `keep` stamina. Each stamina drop is one
    collect: the pre-roll before it is saved as seq_<material>_stamina_resource_hunt_NN."""
    from .gather import TARGETS, Gatherer

    class Hunter(Gatherer):
        last = None

        def progress(self, target):
            now = super().progress(target)
            if now is not None and self.last is not None and now < self.last:
                rec.mark(f"{material}_stamina", "resource_hunt", f"{material} pickup, stamina {self.last} -> {now}")
            if now is not None:
                self.last = now
            return now

    g = Hunter(dev, det)
    stamina = g.open_hunt(material)
    if stamina is None:
        return "unknown_screen"
    budget = min(pickups, max(0, (stamina - keep) // TARGETS[material].cost))
    log.info("%s: stamina %d, keep %d: %d pickups", material, stamina, keep, budget)
    if budget == 0:
        g.nav.go_home()
        return "no_spare_stamina"
    if not g.enter():
        g.nav.go_home()
        return "unknown_screen"
    out = g.collect(TARGETS[material], budget=budget, keep=keep, minutes=4)
    log.info("%s: %s", material, out)
    g.nav.go_home()
    return out.get("end", "done")


# ---------------------------------------------------------------- statue approaches
def statue(dev, det, rec: "Recorder", zone: str) -> str:
    """Approach frames of a statue (mae, 2026-11-11: Goddess and Lost Goddess Statues must be in the model). Walk
    into the zone, then to the statue icon nearest us on the area map; the pre-roll of that walk is the sequence.
    The statue is not tapped (a blessed statue's card has nothing to do)."""
    from ..actions import goto
    from ..vision import area_map
    from .roam import statue_badges, statue_points

    def nearest(frame):
        me = [p for k, p in area_map.objects(frame) if k == "player"]
        cx, cy = me[0] if me else goto.SCREEN_CENTRE
        pts = statue_points(frame) + statue_badges(frame)
        return min(pts, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2) if pts else None

    if det.detect().state != "world_map":
        # A hunt step ends at home (live 2026-11-11: the statue step after it read not_on_map at once).
        from .roam import Roamer
        if not Roamer(dev, det)._to_world():
            return "not_on_map"
    if goto.go_to(dev, det, zone) == "not_on_map":
        return "not_on_map"
    why = goto.go_to(dev, det, nearest)
    log.info("statue walk in %s: %s", zone, why)
    if why != "arrived":
        return why
    time.sleep(1.5)
    rec.mark("statue", zone, f"walk to the statue icon nearest us in {zone}", force=True)
    time.sleep(POST_S + 1)
    return "done"


# ---------------------------------------------------------------- the job
DEFAULT_STEPS = (
    [{"do": "hunt", "arg": m} for m in ("ore", "sand", "rolla", "essence")]
    + [{"do": "statue", "arg": z} for z in ("Auroradrasil", "Jungle Camp", "Troll Lair")]
    + [{"do": "pickups", "arg": z} for z in ("Grotto Peninsula", "Verdantglade XIII", "Hurricane Heights")]
)
STEP_OK = clear.OK | {"done", "no_spare_stamina", "budget_spent", "stamina_reserve", "stuck_progress", "guarded",
                      "arrived", "no_move", "no_label", "no_target"}


def parse_steps(text: str) -> list[dict]:
    """"hunt:ore,statue:Troll Lair,pickups:Grotto Peninsula" -> steps."""
    out = []
    for part in [p.strip() for p in text.split(",") if p.strip()]:
        do, _, arg = part.partition(":")
        if do not in ("hunt", "statue", "pickups") or not arg:
            raise ValueError(f"bad step {part!r}: use hunt:MATERIAL, statue:ZONE or pickups:ZONE")
        out.append({"do": do, "arg": arg.strip()})
    return out


def run(dev, det, job: str, steps: list[dict], target: int, minutes: float, resume: bool, picks: int,
        keep: int, per_material: int) -> dict:
    try:
        j = Job.open(job, resume, target, steps)
    except FileExistsError as e:
        return {"status": "refused: " + str(e)}
    todo = [s for s in j.data["steps"] if not s.get("status") or s["status"] in ("timeout", "paused", "running", "not_on_map")
            or s["status"].startswith("error")]
    banner(log, "Sequence Capture", f"save {j.data['target']} approach sequences of world collectibles (job {job}, "
           f"{j.count} saved so far): " + ", ".join(f"{s['do']} {s['arg']}" for s in todo),
           f"{j.data['target']} sequences, {minutes:g} minutes, every step done, or an unfamiliar screen; stamina "
           f"is spent only on hunt steps and only above {keep}")
    rec = Recorder(dev, j, picks)
    rec.start()
    deadline = time.monotonic() + minutes * 60
    status = "steps_done"
    try:
        for step in todo:
            left = (deadline - time.monotonic()) / 60
            if j.done:
                status = "target"
                break
            if left < 1:
                status = "timeout"
                break
            step["status"] = "running"
            j.save()
            log.info("[step] %s %s: %d of %d sequences so far, %.0f minutes left", step["do"], step["arg"], j.count,
                     j.data["target"], left)
            progress(("step", step["do"], step["arg"]))
            if step["do"] == "hunt":
                res = hunt(dev, det, rec, step["arg"], per_material, keep)
            elif step["do"] == "statue":
                res = statue(dev, det, rec, step["arg"])
            else:
                res = CaptureClearer(dev, det, step["arg"], rec, j).run(left, walk_there=True)
            res = res.split()[0] if isinstance(res, str) else str(res)
            step["status"] = res
            j.save()
            log.info("[step] %s %s: %s", step["do"], step["arg"], res)
            if res not in STEP_OK:
                status = res
                break
        if j.done:
            status = "target"
    except KeyboardInterrupt:
        status = "paused"
    except Exception as e:  # a step's navigation gave up (live 2026-11-11: go_home timed out on a game restart)
        log.exception("step failed: %s", e)
        rec.mark("error", "nav", f"{type(e).__name__}: {e}"[:200], force=True)  # the frames that led up to it
        status = f"error: {type(e).__name__}"
    finally:
        rec.stop()
        j.end_run(status)
    log.info("job %s: %d/%d sequences, %d stamina drops on free legs; resume with: python -m sxs seqcap --job %s "
             "--resume", job, j.count, j.data["target"], len(j.data["stamina_drops"]), job)
    return {"status": status, "sequences": j.count, "target": j.data["target"],
            "kinds": sorted({s["kind"] for s in j.data["sequences"]}), "stamina_drops": len(j.data["stamina_drops"])}


def _args(p) -> None:
    p.add_argument("--job", required=True, help="job name (lower case, digits, _): captures/sequences/<job>/")
    p.add_argument("--steps", default="", help="hunt:MATERIAL, statue:ZONE, pickups:ZONE, comma separated "
                   "(default: ore, sand, rolla, essence; statues in Auroradrasil, Jungle Camp, Troll Lair; pickups in "
                   "Grotto Peninsula, Verdantglade XIII, Hurricane Heights)")
    p.add_argument("--target", type=int, default=30, help="sequences to save (default 30)")
    p.add_argument("--minutes", type=float, default=40, help="upper limit for this sitting")
    p.add_argument("--resume", action="store_true", help="carry on an existing job from its job file")
    p.add_argument("--pick", type=int, default=5, help="frames per sequence copied to docs/screens/sequences/")
    p.add_argument("--keep", type=int, default=150, help="hunt steps never take stamina below this (default 150)")
    p.add_argument("--per-material", type=int, default=4, help="pickups per hunt step (default 4)")


def _run(ctx, opts):
    if not re.match(r"^[a-z][a-z0-9_]*$", opts.job):
        return {"status": "refused: job name must be lower case letters, digits and _"}
    try:
        steps = parse_steps(opts.steps) if opts.steps else [dict(s) for s in DEFAULT_STEPS]
    except ValueError as e:
        return {"status": f"refused: {e}"}
    return run(ctx.dev, ctx.det, opts.job, steps, opts.target, opts.minutes, opts.resume, opts.pick, opts.keep,
               opts.per_material)


OK = {"target", "steps_done", "timeout", "paused"}
LOOP = Loop("seqcap", "Sequence Capture", "record approach sequences of world collectibles and stamina nodes "
            "(pre-roll buffer, resumable)", _run, _args, ok=OK, budget=300)
