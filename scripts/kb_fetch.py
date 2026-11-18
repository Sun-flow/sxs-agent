"""Fetch the public Sword x Staff sites into knowledge/sources/raw/ so research works from local text.

    python3 scripts/kb_fetch.py fandom            # every article of swordxstaff.fandom.com, as wikitext
    python3 scripts/kb_fetch.py sxswiki           # every English page in www.sword-x-staff.wiki's sitemap, as text
    python3 scripts/kb_fetch.py zeroluck          # zeroluck.gg/sword-x-staff/... (section pages)
    python3 scripts/kb_fetch.py eog               # eog.gg/games/sword-x-staff/... (guides and tool pages)
    python3 scripts/kb_fetch.py lootandwaifus     # lootandwaifus.com pages with sword-x-staff in the path
    python3 scripts/kb_fetch.py official          # swordxstaff.boltray.com home and news posts
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
- zeroluck, eog, lootandwaifus, official: "section sites", all driven by the SITES table below. For each one
  the script reads robots.txt first (urllib.robotparser, plus the Content-Signal lines some sites add), takes
  the section's URLs from the sitemaps robots.txt names and from links on the seed pages, and fetches each
  page once with the delay. A page is stored as <slug>.txt (article text) and, when it carries a Next.js
  `__NEXT_DATA__` block, also as <slug>.next.json (the page's own data: the cleanest thing to parse).
  All four folders are gitignored working caches with a manifest.json (pages, skipped URLs and why, the
  robots.txt facts used). Nothing is fetched from a site whose robots.txt forbids our user agent or whose
  Content-Signal says ai-input=no; a URL robots.txt disallows is skipped and listed.
- A site that answers with a bot check (Cloudflare "Just a moment...", sent with HTTP 403 or 503, as
  www.prydwen.gg does) is skipped and reported. This script never tries to get past one.
- A seed that answers 404 is listed under "skipped" in the manifest. On 2026-11-18 zeroluck.gg and
  lootandwaifus.com answered 404 for every Sword x Staff URL from this environment and listed none in their
  sitemaps, so those two manifests hold zero pages until the sites serve the section here.

Standard library only. Needs network access to the hosts (the cloud environment's allowed domains).
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


BOT_MARKS = ("<title>Just a moment...</title>", "cf-browser-verification", "challenge-platform")


def get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        # Cloudflare sends its challenge page with 403 or 503: that is a bot check, not a missing page.
        if e.code in (403, 429, 503):
            body = e.read(4000).decode("utf-8", errors="replace")
            if e.headers.get("cf-mitigated") == "challenge" or any(m in body for m in BOT_MARKS):
                raise BotCheck(url) from None
        raise
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


def sitemap_urls(url: str, seen: set[str] | None = None, delay: float = 0.0) -> list[str]:
    """Every page URL in a sitemap, following sitemap indexes (one request per file, `delay` apart)."""
    seen = seen if seen is not None else set()
    if url in seen:
        return []
    if seen:
        time.sleep(delay)
    seen.add(url)
    locs = [html.unescape(u) for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", get(url))]
    out: list[str] = []
    for u in locs:
        out += sitemap_urls(u, seen, delay) if u.endswith(".xml") else [u]
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


# ---------------------------------------------------------------- section sites (robots + sitemap + links)

# include/exclude are regular expressions matched against the URL path. seeds are fetched first and their
# links are followed (same host, include matches, no query string), so a section missing from the sitemap is
# still found. Add a site by adding a row: it becomes a subcommand with its own folder and manifest.
SITES: dict[str, dict] = {
    "zeroluck": {
        "base": "https://zeroluck.gg", "include": r"^/sword-x-staff(/|$)", "exclude": r"/(profile|my)(/|$)",
        "seeds": ["/sword-x-staff/", "/sword-x-staff/guides/"] + [f"/sword-x-staff/{p}/" for p in (
            "classes", "companions", "bestiary", "gear", "combat-stats", "game-modes", "currencies",
            "life-skills", "reroll", "relics", "battle-pass", "summoning", "codes")],
        "license": "none stated: working cache only, not committed",
    },
    "eog": {
        "base": "https://eog.gg", "include": r"^/games/sword-x-staff(/|$)", "exclude": r"^/api/",
        "seeds": ["/games/sword-x-staff/", "/games/sword-x-staff/tools/"],
        "license": "none stated; robots.txt Content-Signal ai-train=no, use=reference: working cache only",
    },
    "lootandwaifus": {
        "base": "https://lootandwaifus.com", "include": r"sword-x-staff", "exclude": r"^/api/auth/",
        "seeds": ["/sword-x-staff/", "/sword-x-staff-relic-database/", "/sword-x-staff-ingredient-database/",
                  "/sword-x-staff-interactive-map/", "/sword-x-staff-custom-tier-list/",
                  "/guides/sword-x-staff-codes/", "/guides/sword-x-staff-api/"],
        "license": "none stated; robots.txt Content-Signal ai-train=no, use=reference: working cache only",
    },
    "official": {
        "base": "https://swordxstaff.boltray.com", "include": r"^/($|news(/|$))", "exclude": r"^/(api|topup)(/|$)",
        "seeds": ["/", "/news", "/news/news", "/news/lore", "/news/guide"],
        "license": "publisher's copyright: working cache only, not committed",
    },
}
MAX_PAGES = 300
NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
HREF = re.compile(r'href="([^"#]+)')


class RobotsForbid(Exception):
    """robots.txt (or its Content-Signal) does not allow this script to read the site."""


def read_robots(base: str) -> tuple[urllib.robotparser.RobotFileParser, dict]:
    """Parse robots.txt. A missing file (404) allows everything; a bot check or server error stops the site."""
    rp = urllib.robotparser.RobotFileParser()
    info: dict = {"url": base + "/robots.txt", "content_signal": None}
    try:
        text = get(info["url"])
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        text = ""
        info["missing"] = True
    rp.parse(text.splitlines())
    # Content-Signal (contentsignals.org) is not known to robotparser: read the one in the "*" group.
    agents: list[str] = []
    in_rules = False
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, val = (x.strip() for x in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if in_rules:
                agents, in_rules = [], False
            agents.append(val.lower())
        else:
            in_rules = True
            if key == "content-signal" and "*" in agents:
                info["content_signal"] = dict(
                    (k.strip().lower(), v.strip().lower())
                    for k, v in (kv.split("=", 1) for kv in val.split(",") if "=" in kv))
    sig = info["content_signal"] or {}
    # We read pages so an AI agent can look facts up (ai-input / reference use), never for training.
    if sig.get("ai-input") == "no" or sig.get("use") == "no":
        raise RobotsForbid(f"Content-Signal {sig} forbids AI reference use")
    return rp, info


def page_file(path: str) -> str:
    path = path.strip("/")
    return slug(path.replace("/", "--")) if path else "home"


def fetch_site(name: str, delay: float) -> int:
    cfg = SITES[name]
    base = cfg["base"]
    host = urllib.parse.urlparse(base).netloc
    include, exclude = re.compile(cfg["include"]), re.compile(cfg["exclude"])
    out = RAW / name
    robots, robots_info = read_robots(base)
    time.sleep(delay)
    if not robots.can_fetch(UA, base + cfg["seeds"][0]):
        raise RobotsForbid(f"robots.txt disallows {cfg['seeds'][0]} for this user agent")
    out.mkdir(parents=True, exist_ok=True)

    def wanted(u: str) -> str | None:
        """Return the URL in fetchable form if it belongs to the section, else None."""
        p = urllib.parse.urlparse(urllib.parse.urljoin(base + "/", u.strip()))
        if p.scheme not in ("http", "https") or p.netloc != host or p.query:
            return None
        path = p.path or "/"
        if not include.search(path) or exclude.search(path) or re.search(r"\.[a-z0-9]{2,5}$", path):
            return None
        return base + path

    queue: list[str] = []
    known: set[str] = set()

    def add(u: str | None) -> None:
        if u and u.rstrip("/") not in known:
            known.add(u.rstrip("/"))
            queue.append(u)

    sitemaps = robots.site_maps() or [base + "/sitemap.xml"]
    sitemap_note = []
    for sm in sitemaps:
        try:
            found = [w for w in map(wanted, sitemap_urls(sm, delay=delay)) if w]
            sitemap_note.append({"url": sm, "section_urls": len(found)})
        except BotCheck:
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            found = []
            sitemap_note.append({"url": sm, "error": str(e)})
        time.sleep(delay)
        for u in sorted(found):
            add(u)
    for s in cfg["seeds"]:
        add(base + s)
    seeds = {(base + s).rstrip("/") for s in cfg["seeds"]}

    manifest, skipped = [], []
    while queue and len(manifest) < MAX_PAGES:
        u = queue.pop(0)
        if not robots.can_fetch(UA, u):
            skipped.append((u, "robots.txt disallows"))
            continue
        try:
            page = get(u)
        except BotCheck:
            skipped.append((u, "bot check"))
            time.sleep(delay)
            continue
        except urllib.error.HTTPError as e:
            skipped.append((u, f"HTTP {e.code}" + (" (seed)" if u.rstrip("/") in seeds else "")))
            time.sleep(delay)
            continue
        except (urllib.error.URLError, TimeoutError) as e:
            skipped.append((u, str(e)))
            time.sleep(delay)
            continue
        parser = ArticleText()
        parser.feed(page)
        text = parser.text()
        stem = page_file(urllib.parse.urlparse(u).path)
        (out / (stem + ".txt")).write_text(
            f"source: {u}\nfetched: {now()}\ntitle: {parser.title.strip()}\n\n{text}", encoding="utf-8")
        entry = {"url": u, "file": stem + ".txt", "title": parser.title.strip(), "chars": len(text)}
        m = NEXT_DATA.search(page)
        if m:
            try:
                data = json.loads(m.group(1))
                (out / (stem + ".next.json")).write_text(
                    json.dumps(data.get("props", {}).get("pageProps", data), ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")
                entry["next_data"] = stem + ".next.json"
            except json.JSONDecodeError:
                pass
        manifest.append(entry)
        for href in HREF.findall(page):
            add(wanted(html.unescape(href)))
        time.sleep(delay)

    (out / "manifest.json").write_text(json.dumps({
        "source": host, "license": cfg["license"], "fetched": now(), "robots": robots_info,
        "sitemaps": sitemap_note, "pages": manifest, "skipped": skipped,
        "not_fetched_page_cap": queue}, indent=1) + "\n", encoding="utf-8")
    print(f"{name}: {len(manifest)} pages, {len(skipped)} skipped -> {out.relative_to(ROOT)} (gitignored)")
    for u, why in skipped:
        print(f"  skipped {u}: {why}")
    if not manifest:
        print(f"  {name}: no section page was served. Check the seeds in SITES against the live site.")
        return 1
    return 0


def status() -> int:
    for name in ("fandom", "sxswiki", *SITES):
        m = RAW / name / "manifest.json"
        if not m.is_file():
            print(f"{name}: not fetched (python3 scripts/kb_fetch.py {name})")
            continue
        d = json.loads(m.read_text(encoding="utf-8"))
        extra = f", {len(d['skipped'])} skipped" if d.get("skipped") else ""
        print(f"{name}: {len(d['pages'])} pages{extra}, fetched {d['fetched']}, licence: {d['license']}")
    return 0


def main() -> int:
    sources = {"fandom": fetch_fandom, "sxswiki": fetch_sxswiki,
               **{n: (lambda delay, n=n: fetch_site(n, delay)) for n in SITES}}
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("what", choices=[*sources, "all", "status"])
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (default 1.0)")
    a = ap.parse_args()
    if a.what == "status":
        return status()
    rc = 0
    for name, fn in sources.items():
        if a.what in (name, "all"):
            try:
                rc |= fn(a.delay)
            except BotCheck as e:
                print(f"{name}: bot check at {e}; skipped (this script does not bypass bot checks)")
                rc = 1
            except RobotsForbid as e:
                print(f"{name}: not fetched: {e}")
                rc = 1
            except (urllib.error.URLError, TimeoutError) as e:
                print(f"{name}: network error ({e}); is the host in the environment's allowed domains?")
                rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
