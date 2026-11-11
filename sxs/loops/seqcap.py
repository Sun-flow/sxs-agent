"""Sequence Capture: record approach sequences of world collectibles for detector training data. No model calls.

    python -m sxs seqcap --job NAME [--areas "Zone A,Zone B"] [--target 20] [--minutes 40]
    python -m sxs seqcap --job NAME --resume        # carry on a stopped job where it left off

Plan: docs/collectibles-capture-plan.md (mae, 2026-11-11: collectibles in the world with the frames leading up to
collection, for the Roboflow detector).

How it works:
- A **pre-roll buffer** (`Recorder`) keeps every frame the bot takes plus one every SAMPLE_S from a sampler thread,
  for the last PRE_S seconds. When a leg collects something (a pickup's reward popup, an object cleared, a card
  acted on, a wheel), the buffer from PRE_S before to POST_S after is saved as one sequence:
  captures/sequences/<job>/seq_<kind>_<zone>_<nn>/fNN.png with frames.json. Nobody has to start a burst by hand.
- The walk is Clear Zone's (`sxs/loops/clear.py`) cut down to **capture only**: legs go to pickups only (minimap item
  dots and known collectible crops on screen). No quest ring, no guard fights, no big-map or frontier legs, no
  blessing at 100%. Clear Zone already refuses explored zones, where pickups cost stamina (R-065).
- **Stamina guard**: stamina is read before every leg; any drop ends the job at once ("stamina_spent"). The job
  never spends stamina or any currency (mae, 2026-11-11).
- **Pausable**: the job file captures/sequences/<job>/job.json is written after every saved sequence, and a sequence
  folder appears only when complete (written as .part, then renamed). Stop any time (Ctrl+C, close the laptop, the
  emulator dropping); `--resume` continues the count and the zone list from the job file.
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
COLLECT_EVENTS = {"pickup": "pickup", "cleared": "pickup", "acted": "object", "wheel": "wheel"}
ROOT = CAPTURES / "sequences"
PICKS = SCREENS / "sequences"
STAMINA_DROP_READS = 2  # readings in a row below the last good one before the guard stops the job (OCR slips)


def slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (t or "unknown").lower()).strip("_")[:30] or "unknown"


class StaminaSpent(Exception):
    pass


# ---------------------------------------------------------------- the job file
class Job:
    def __init__(self, name: str):
        self.name = name
        self.dir = ROOT / name
        self.file = self.dir / "job.json"
        self.data = {"job": name, "target": 20, "areas": [], "sequences": [], "zones": {}, "runs": []}
        self.lock = threading.Lock()

    @classmethod
    def open(cls, name: str, resume: bool, target: int, areas: list[str]) -> "Job":
        job = cls(name)
        if job.file.exists():
            if not resume:
                raise FileExistsError(f"job {name!r} exists ({job.file}); pass --resume to carry it on")
            job.data = json.loads(job.file.read_text(encoding="utf-8"))
            if areas:
                job.data["areas"] = areas
        else:
            job.data.update(target=target, areas=areas)
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

    def mark(self, kind: str, zone: str, what: str) -> None:
        now = time.time()
        if self.pending and now - self.pending[-1]["t"] < MERGE_S:
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


# ---------------------------------------------------------------- Clear Zone, capture only
class CaptureClearer(clear.Clearer):
    MINIMAP_GOALS = ("item",)

    def __init__(self, dev, det, area, rec: Recorder):
        super().__init__(dev, det, area)
        self.rec = rec
        self.stamina: Optional[int] = None
        self.low_reads = 0

    def event(self, name: str) -> None:
        super().event(name)
        kind = COLLECT_EVENTS.get(name)
        if kind:
            what = self.leg.what if self.leg else name
            if name == "acted" and self.last_card:
                kind = slug(self.last_card)
            self.rec.mark(kind, self.home or "unknown", what)

    def guard_stamina(self) -> None:
        s = read_stamina(self.det)
        if s is None:
            return
        if self.stamina is None or s >= self.stamina:
            self.stamina, self.low_reads = s, 0
            return
        self.low_reads += 1
        if self.low_reads >= STAMINA_DROP_READS:
            raise StaminaSpent(f"stamina {self.stamina} -> {s}")

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
        return self.try_known(frame, xy, me) or self.try_minimap(frame, xy, me)

    def map_pct(self) -> None:
        return  # area-map % reads only steer exploration; capture doesn't need them

    def finish_zone(self) -> str:
        log.info("%s reads 100%%: no pickups left here (statue not blessed: capture only)", self.home)
        return "zone_done"


# ---------------------------------------------------------------- the loop
def run(dev, det, job: str, areas: list[str], target: int, minutes: float, resume: bool, picks: int) -> dict:
    try:
        j = Job.open(job, resume, target, areas)
    except FileExistsError as e:
        return {"status": "refused: " + str(e)}
    zones = j.data["areas"]
    banner(log, "Sequence Capture", f"save {j.data['target']} approach sequences of world collectibles "
           f"(job {job}, {j.count} saved so far) from pickups in {', '.join(zones) or 'the zone we stand in'}",
           f"{j.data['target']} sequences, {minutes:g} minutes, every zone out of pickups, any stamina spent, "
           "or an unfamiliar screen")
    rec = Recorder(dev, j, picks)
    rec.start()
    deadline = time.monotonic() + minutes * 60
    status = "timeout"
    try:
        todo = [z for z in zones if j.data["zones"].get(z) not in clear.OK - {"timeout"}] or ([None] if not zones else [])
        for zone in todo:
            if j.done:
                break
            left = (deadline - time.monotonic()) / 60
            if left < 1:
                break
            c = CaptureClearer(dev, det, zone, rec)
            log.info("zone %s: %d of %d sequences so far, %.0f minutes left", zone or "(here)", j.count,
                     j.data["target"], left)
            res = c.run(left, walk_there=zone is not None)
            zstat = res.split()[0] if isinstance(res, str) else str(res)
            j.data["zones"][zone or c.home or "here"] = zstat
            j.save()
            if zstat not in clear.OK:
                status = zstat
                break
        else:
            status = "target" if j.done else "zones_done"
        if j.done:
            status = "target"
    except StaminaSpent as e:
        log.warning("STOP: %s. The job never spends stamina; check what took it", e)
        status = "stamina_spent"
    except KeyboardInterrupt:
        status = "paused"
    finally:
        rec.stop()
        j.end_run(status)
    log.info("job %s: %d/%d sequences; resume with: python -m sxs seqcap --job %s --resume", job, j.count,
             j.data["target"], job)
    return {"status": status, "sequences": j.count, "target": j.data["target"],
            "kinds": sorted({s["kind"] for s in j.data["sequences"]})}


def _args(p) -> None:
    p.add_argument("--job", required=True, help="job name (lower case, digits, _): captures/sequences/<job>/")
    p.add_argument("--areas", default="", help="zones to take pickups in, comma separated (default: where we stand)")
    p.add_argument("--target", type=int, default=20, help="sequences to save (default 20)")
    p.add_argument("--minutes", type=float, default=40, help="upper limit for this sitting")
    p.add_argument("--resume", action="store_true", help="carry on an existing job")
    p.add_argument("--pick", type=int, default=5, help="frames per sequence copied to docs/screens/sequences/")


def _run(ctx, opts):
    if not re.match(r"^[a-z][a-z0-9_]*$", opts.job):
        return {"status": "refused: job name must be lower case letters, digits and _"}
    areas = [a.strip() for a in opts.areas.split(",") if a.strip()]
    return run(ctx.dev, ctx.det, opts.job, areas, opts.target, opts.minutes, opts.resume, opts.pick)


OK = {"target", "zones_done", "timeout", "paused"} | clear.OK
LOOP = Loop("seqcap", "Sequence Capture", "record approach sequences of world collectibles (pickups only, "
            "resumable, never spends stamina)", _run, _args, ok=OK, budget=300)
