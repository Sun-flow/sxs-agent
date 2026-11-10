"""Screen labeling UI: a small local web page for naming screens and marking what matters on them (mae, 2026-11-09).

    python -m sxs labeler [--port 8765] [--no-browser]

Opens http://127.0.0.1:8765 in the browser. The left column lists every screen in docs/screens/ (the unlabelled
bank first). Pick one, drag on it to draw a box, name the box and say what it is (button, text, icon, badge,
region), and, for the UI detector, which detector class it is (resource/detect/classes.json). Boxes the
pre-labeller drew (`python -m sxs prelabel`) show dashed as drafts: fix them and press Confirm (moving or resizing
one confirms it too). Fill in the screen's name, state and notes. Save writes:

- the boxes to docs/screens/labels.json, and a crop of every box ticked "template" to resource/image/labels/
  (sxs/core/labels.py has the format; sxs/vision/labels.py finds them on a frame);
- for a banked screen, its row in docs/screens/unlabeled/README.md (the "File labelled screens" button then runs
  `python -m sxs label`, which moves it into its folder and keeps its boxes);
- for a filed screen, its state and notes in docs/screens/expected.json.

Python standard library plus Pillow; no MaaFramework, no emulator, no model calls. Listens on 127.0.0.1 only.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from ..core import labels, screens
from ..core.paths import SCREENS

PAGE = Path(__file__).with_name("page.html")
LOCK = threading.Lock()


def _known_states() -> list[str]:
    """State ids the detector can report (State.MainMenu -> main_menu), plus any already used in expected.json."""
    import re

    from ..core.paths import RESOURCE

    names = set(screens.load_expected()["states"].values()) | {"unknown", "-"}
    try:
        nodes = json.loads((RESOURCE / "pipeline" / "state.json").read_text(encoding="utf-8"))
        for node in nodes:
            parts = node.split(".")
            if parts[0] == "State" and len(parts) >= 2 and parts[1] not in ("Detect",):
                names.add(re.sub(r"(?<!^)(?=[A-Z])", "_", parts[1]).lower())
    except (OSError, ValueError):
        pass
    return sorted(names)


def _screen_path(key: str) -> Path:
    """docs/screens/<key>, refusing anything outside it."""
    p = (SCREENS / key).resolve()
    if SCREENS.resolve() not in p.parents or p.suffix.lower() != ".png" or not p.exists():
        raise FileNotFoundError(key)
    return p


def _image_size(p: Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(p) as im:
        return im.size


def _items() -> list[dict]:
    from ..detect import items

    return items.load()["items"]


def list_screens() -> list[dict]:
    expected = screens.load_expected()
    rows = {r["file"]: r for r in screens.bank_rows()}
    stored = labels.load()["screens"]
    boxed = {k: len(v.get("boxes", [])) for k, v in stored.items()}
    drafts = {k: sum(1 for b in v.get("boxes", []) if b.get("draft")) for k, v in stored.items()}
    out = []
    for p in sorted(SCREENS.rglob("*.png")):
        key = labels.screen_key(p)
        folder = key.split("/")[0] if "/" in key else ""
        banked = folder == "unlabeled"
        row = rows.get(p.name, {}) if banked else {}
        out.append({"key": key, "folder": folder, "file": p.name, "banked": banked,
                    "state": row.get("state", "") if banked else expected["states"].get(p.stem, ""),
                    "labelled": bool(row.get("state")) if banked else p.stem in expected["states"],
                    "boxes": boxed.get(key, 0), "drafts": drafts.get(key, 0)})
    out.sort(key=lambda s: (not s["banked"], s["folder"], s["file"]))
    return out


def screen_detail(key: str) -> dict:
    p = _screen_path(key)
    banked = key.startswith("unlabeled/")
    expected = screens.load_expected()
    if banked:
        row = next((r for r in screens.bank_rows() if r["file"] == p.name), {})
        fields = {k: row.get(k, "").strip("`") for k in ("name", "folder", "state", "what")}
    else:
        fields = {"name": p.stem, "folder": key.split("/")[0], "state": expected["states"].get(p.stem, ""),
                  "what": expected["notes"].get(p.stem, "")}
    return {"key": key, "banked": banked, "size": list(_image_size(p)), "fields": fields,
            "boxes": labels.boxes_for(key), "suggested_folder": screens.folder_for(fields["name"] or p.stem)}


def save_screen(body: dict) -> dict:
    key = body["key"]
    p = _screen_path(key)
    f = body.get("fields", {})
    problems = labels.set_boxes(key, body.get("boxes", []), _image_size(p))
    if key.startswith("unlabeled/"):
        name = f.get("name", "").strip()
        if name and not screens.NAME.match(name):
            problems.append(f"screen name {name!r} must be lower case letters, digits and _")
            name = ""
        screens.set_row(p.name, name, f.get("folder", ""), f.get("state", ""), f.get("what", ""))
    else:
        expected = screens.load_expected()
        state, what = f.get("state", "").strip(), f.get("what", "").strip()
        if state and state != "-":
            expected["states"][p.stem] = state
        elif state == "-":
            expected["states"].pop(p.stem, None)
        if what:
            expected["notes"][p.stem] = what
        else:
            expected["notes"].pop(p.stem, None)
        screens.save_expected(expected)
    crops = [e["template"] for e in json.loads(labels.MANIFEST.read_text(encoding="utf-8"))["entries"]
             if e["source"] == key] if labels.MANIFEST.exists() else []
    return {"ok": not problems, "problems": problems, "crops": crops}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quiet: one line per save, not per image
        pass

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, code: int = 200) -> None:
        self._send(code, json.dumps(data).encode("utf-8"), "application/json")

    def do_GET(self):
        url = urlparse(self.path)
        try:
            if url.path == "/":
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif url.path == "/api/screens":
                self._json({"screens": list_screens(), "states": _known_states(), "kinds": labels.KINDS,
                            "template_kinds": labels.TEMPLATE_KINDS, "classes": labels.classes(),
                            "items": [{"id": i["id"], "name": i.get("name", "")} for i in _items()]})
            elif url.path == "/api/screen":
                self._json(screen_detail(parse_qs(url.query)["key"][0]))
            elif url.path.startswith("/img/"):
                p = _screen_path(unquote(url.path[5:]))
                self._send(200, p.read_bytes(), mimetypes.guess_type(p.name)[0] or "image/png")
            else:
                self._json({"error": "not found"}, 404)
        except (FileNotFoundError, KeyError) as e:
            self._json({"error": f"not found: {e}"}, 404)

    def do_POST(self):
        url = urlparse(self.path)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            with LOCK:
                if url.path == "/api/save":
                    result = save_screen(body)
                    print(f"saved {body['key']}: {len(body.get('boxes', []))} box(es)"
                          + (f", problems: {result['problems']}" if result["problems"] else ""), flush=True)
                    self._json(result)
                elif url.path == "/api/file":
                    filed, problems = screens.label()
                    for line in filed + problems:
                        print(line, flush=True)
                    self._json({"filed": filed, "problems": problems})
                else:
                    self._json({"error": "not found"}, 404)
        except (FileNotFoundError, KeyError, ValueError) as e:
            self._json({"error": str(e)}, 400)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m sxs labeler", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true", help="don't open the browser")
    args = p.parse_args(argv)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Screen labeler on {url} (Ctrl+C to stop)", flush=True)
    if not args.no_browser:
        threading.Timer(0.5, webbrowser.open, (url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
