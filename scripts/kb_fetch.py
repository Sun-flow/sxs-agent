"""Fetch the public Sword x Staff wikis into knowledge/sources/raw/ so research works from local text.

    python3 scripts/kb_fetch.py fandom            # every article of swordxstaff.fandom.com, as wikitext
    python3 scripts/kb_fetch.py sxswiki           # every English page in www.sword-x-staff.wiki's sitemap, as text
    python3 scripts/kb_fetch.py all [--delay 1.0]
    python3 scripts/kb_fetch.py status            # what is cached, and how old

How each source is read (details: knowledge/sources/README.md):
- fandom: the MediaWiki API (api.php), the interface the site offers for programs. One request per 50 pages.
  Text is CC BY-SA 3.0, so the wikitext is committed under knowledge/sources/raw/fandom/ with a manifest that
  credits each page (title, URL, revision id, time).
- sxswiki: robots.txt allows everything and names sitemap.xml. Pages are fetched one at a time with a delay and
  reduced to their article text. The site states no content licence, so that text goes to the gitignored
  knowledge/sources/raw/sxswiki/ cache: a working copy to read, never committed. Facts taken from it are cited
  by URL in the knowledge files.
- A site that answers with a bot check (Cloudflare "Just a moment...", as www.prydwen.gg does) is skipped and
  reported. This script never tries to get past one.

Standard library only. Needs network access to the two hosts (the cloud environment's allowed domains).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "knowledge" / "sources" / "raw"
UA = "Mozilla/5.0 (X11; Linux x86_64) sxs-knowledge-fetch/1.0"
FANDOM_API = "https://swordxstaff.fandom.com/api.php"
FANDOM_PAGE = "https://swordxstaff.fandom.com/wiki/"
SXSWIKI = "https://www.sword-x-staff.wiki"
# Two-letter first path segments are translations of the English pages.
LANG_SEGMENT = re.compile(r"^/[a-z]{2}(?:-[a-zA-Z]{2})?(?:/|$)")


class BotCheck(Exception):
    """The site answered with a bot-check page instead of content."""


def get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        text = r.read().decode("utf-8", errors="replace")
    if "<title>Just a moment...</title>" in text[:600]:
        raise BotCheck(url)
    return text


def slug(title: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-").lower()
    return s or "page"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- fandom

def fetch_fandom(delay: float) -> int:
    out = RAW / "fandom"
    out.mkdir(parents=True, exist_ok=True)
    pages: dict[int, dict] = {}
    params = {
        "action": "query", "format": "json", "formatversion": "2",
        "generator": "allpages", "gaplimit": "50", "gapfilterredir": "nonredirects",
        "prop": "revisions|categories", "rvprop": "content|timestamp|ids", "rvslots": "main", "cllimit": "500",
    }
    cont: dict[str, str] = {}
    while True:
        data = json.loads(get(FANDOM_API + "?" + urllib.parse.urlencode({**params, **cont})))
        for p in data.get("query", {}).get("pages", []):
            # A page can arrive in pieces across continuation batches: merge them.
            cur = pages.setdefault(p["pageid"], {"title": p["title"], "categories": []})
            if p.get("revisions"):
                cur["revision"] = p["revisions"][0]
            cur["categories"] += [c["title"].split(":", 1)[-1] for c in p.get("categories", [])]
        if "continue" not in data:
            break
        cont = data["continue"]
        time.sleep(delay)

    manifest = []
    for pid, p in sorted(pages.items(), key=lambda kv: kv[1]["title"].lower()):
        rev = p.get("revision")
        if not rev:
            continue
        text = rev["slots"]["main"]["content"]
        name = slug(p["title"]) + ".wiki"
        (out / name).write_text(text.rstrip() + "\n", encoding="utf-8")
        manifest.append({
            "title": p["title"], "file": name, "pageid": pid, "revid": rev["revid"], "edited": rev["timestamp"],
            "url": FANDOM_PAGE + urllib.parse.quote(p["title"].replace(" ", "_")),
            "chars": len(text), "categories": sorted(set(p["categories"])),
        })
    keep = {m["file"] for m in manifest}
    for old in out.glob("*.wiki"):
        if old.name not in keep:
            old.unlink()
    (out / "manifest.json").write_text(json.dumps({
        "source": "swordxstaff.fandom.com", "license": "CC BY-SA 3.0 (Fandom community content)",
        "fetched": now(), "pages": manifest}, indent=1) + "\n", encoding="utf-8")
    print(f"fandom: {len(manifest)} pages, {sum(m['chars'] for m in manifest)} chars -> {out.relative_to(ROOT)}")
    return 0


# ---------------------------------------------------------------- sxswiki

class ArticleText(HTMLParser):
    """Reduce a page to readable text: headings as #, list items as -, table rows as | a | b |."""

    SKIP = {"script", "style", "nav", "footer", "header", "svg", "noscript", "form", "button", "aside"}
    BLOCK = {"p", "div", "section", "article", "br", "ul", "ol", "table", "blockquote"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0
        self.title = ""
        self._in_title = False
        self.cell: list[str] | None = None
        self.row: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        if self.skip:
            return
        if tag == "title":
            self._in_title = True
        elif re.fullmatch(r"h[1-6]", tag):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell = []
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag == "title":
            self._in_title = False
        elif tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.out.append("\n| " + " | ".join(self.row) + " |")
            self.row = None
        elif re.fullmatch(r"h[1-6]", tag) or tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self.skip:
            return
        if self.cell is not None:
            self.cell.append(data)
        else:
            self.out.append(data)

    def text(self) -> str:
        t = "".join(self.out)
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        t = re.sub(r" ?\n ?", "\n", t)
        return re.sub(r"\n{3,}", "\n\n", t).strip() + "\n"


def sitemap_urls(url: str, seen: set[str] | None = None) -> list[str]:
    seen = seen if seen is not None else set()
    if url in seen:
        return []
    seen.add(url)
    locs = [html.unescape(u) for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", get(url))]
    out: list[str] = []
    for u in locs:
        out += sitemap_urls(u, seen) if u.endswith(".xml") else [u]
    return out


def fetch_sxswiki(delay: float) -> int:
    out = RAW / "sxswiki"
    out.mkdir(parents=True, exist_ok=True)
    robots = urllib.robotparser.RobotFileParser()
    robots.parse(get(SXSWIKI + "/robots.txt").splitlines())
    sitemaps = robots.site_maps() or [SXSWIKI + "/sitemap.xml"]
    urls = sorted({u.rstrip("/") for sm in sitemaps for u in sitemap_urls(sm)})
    urls = [u for u in urls if not LANG_SEGMENT.match(urllib.parse.urlparse(u).path or "/")]
    manifest, skipped = [], []
    for u in urls:
        if not robots.can_fetch(UA, u):
            skipped.append((u, "robots.txt disallows"))
            continue
        path = urllib.parse.urlparse(u).path.strip("/")
        name = (slug(path.replace("/", "--")) if path else "home") + ".txt"
        try:
            page = get(u)
        except BotCheck:
            skipped.append((u, "bot check"))
            continue
        except (urllib.error.URLError, TimeoutError) as e:
            skipped.append((u, str(e)))
            continue
        parser = ArticleText()
        parser.feed(page)
        text = parser.text()
        (out / name).write_text(f"source: {u}\nfetched: {now()}\ntitle: {parser.title.strip()}\n\n{text}", encoding="utf-8")
        manifest.append({"url": u, "file": name, "title": parser.title.strip(), "chars": len(text)})
        time.sleep(delay)
    (out / "manifest.json").write_text(json.dumps({
        "source": "www.sword-x-staff.wiki", "license": "none stated: working cache only, not committed",
        "fetched": now(), "pages": manifest, "skipped": skipped}, indent=1) + "\n", encoding="utf-8")
    print(f"sxswiki: {len(manifest)} pages, {len(skipped)} skipped -> {out.relative_to(ROOT)} (gitignored)")
    for u, why in skipped:
        print(f"  skipped {u}: {why}")
    return 0


def status() -> int:
    for name in ("fandom", "sxswiki"):
        m = RAW / name / "manifest.json"
        if not m.is_file():
            print(f"{name}: not fetched (python3 scripts/kb_fetch.py {name})")
            continue
        d = json.loads(m.read_text(encoding="utf-8"))
        print(f"{name}: {len(d['pages'])} pages, fetched {d['fetched']}, licence: {d['license']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("what", choices=["fandom", "sxswiki", "all", "status"])
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (default 1.0)")
    a = ap.parse_args()
    if a.what == "status":
        return status()
    rc = 0
    for name, fn in (("fandom", fetch_fandom), ("sxswiki", fetch_sxswiki)):
        if a.what in (name, "all"):
            try:
                rc |= fn(a.delay)
            except BotCheck as e:
                print(f"{name}: bot check at {e}; skipped (this script does not bypass bot checks)")
                rc = 1
            except urllib.error.URLError as e:
                print(f"{name}: network error ({e}); is the host in the environment's allowed domains?")
                rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
