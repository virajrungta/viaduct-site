#!/usr/bin/env python3
"""Build the Viaduct site: index.html and docs/*.html.

    python3 build.py [path/to/viaduct-plugin-repo]   (default: ../pcb-plugin)

The docs pages are generated from the plugin repo's docs/*.md so the site never
drifts from the repo. Needs the `markdown` package (pip install markdown)."""

import datetime
import html
import json
import os
import re
import shutil
import sys
import urllib.request

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "public")          # the deployed site (see deploy.sh)
ASSETS = ["site.css", "logo.svg", "favicon.svg", "apple-touch-icon.png", "img", "video"]
PLUGIN = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "pcb-plugin"))
if os.path.isdir(os.path.join(PLUGIN, "plugin", ".claude-plugin")):   # V2.12+: the plugin lives in plugin/
    PLUGIN = os.path.join(PLUGIN, "plugin")
REPO = "https://github.com/virajrungta/viaduct"
VERSION = json.load(open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")))["version"]
STAR = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6L2.5 9.4l6.6-.8z"/></svg>'

DOCS = [  # (file, title, group)
    ("getting-started", "Getting started", "Start here"),
    ("how-it-works", "How it works", "Start here"),
    ("cli", "CLI reference", "Reference"),
    ("troubleshooting", "Troubleshooting", "Reference"),
]


def icon(name, cls="icon"):
    svg = open(os.path.join(HERE, "img", "icons", name + ".svg")).read()
    d = re.search(r'<path d="([^"]+)"', svg).group(1)
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true"><path d="%s"/></svg>' % (cls, d)


def head(title, desc, root):
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%s</title>
<meta name="description" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:image" content="https://viaduct-pcb.github.io/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="%sfavicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="%sapple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="%ssite.css">
</head>
<body>
""" % (html.escape(title), html.escape(desc), html.escape(title), html.escape(desc), root, root, root)


def topbar(root, active):
    links = [("Demo", root + "index.html#demo", "demo"),
             ("Docs", root + "docs/getting-started.html", "docs"),
             ("Examples", root + "#examples", "examples"),
             ("Changelog", root + "#changelog", "changelog"),
             ("Usage", root + "usage.html", "usage"),
             ("Releases", REPO + "/releases", "")]
    nav = "".join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if k and k == active else "", t)
                  for t, h, k in links)
    return """<header class="topbar gutter">
  <div class="container">
    <a class="logo" href="%(root)sindex.html"><img src="%(root)slogo.svg" alt="" width="26" height="26">Viaduct</a>
    <nav class="nav" aria-label="Main">%(nav)s</nav>
    <div class="bar-right">
      <a class="gh-link" href="%(repo)s">%(gh)s<span class="label">Star on GitHub</span><span class="count">v%(ver)s</span></a>
      <a class="btn btn-claude btn-sm" href="%(root)sindex.html#install">%(claude)s<span class="long">Install for Claude Code</span><span class="short">Install</span></a>
    </div>
  </div>
</header>
""" % {"root": root, "nav": nav, "repo": REPO, "gh": icon("github"), "ver": VERSION, "claude": icon("claude")}


def footer(root):
    return """<footer class="footer gutter">
  <div class="container">
    <div>
      <a class="logo" href="%(root)sindex.html"><img src="%(root)slogo.svg" alt="" width="26" height="26">Viaduct</a>
      <p class="fine">PCB design for Claude Code. Open source under the MIT license. Viaduct is an independent project, not made by Anthropic or KiCad.</p>
    </div>
    <div><h4>Product</h4><ul>
      <li><a href="%(root)sindex.html#examples">Example boards</a></li>
      <li><a href="%(root)sindex.html#install">Install</a></li>
      <li><a href="%(root)sindex.html#changelog">Changelog</a></li></ul></div>
    <div><h4>Docs</h4><ul>
      <li><a href="%(root)sdocs/getting-started.html">Getting started</a></li>
      <li><a href="%(root)sdocs/how-it-works.html">How it works</a></li>
      <li><a href="%(root)sdocs/cli.html">CLI reference</a></li>
      <li><a href="%(root)sdocs/troubleshooting.html">Troubleshooting</a></li></ul></div>
    <div><h4>Project</h4><ul>
      <li><a href="%(repo)s">GitHub</a></li>
      <li><a href="%(repo)s/releases">Releases</a></li>
      <li><a href="%(repo)s/issues">Report an issue</a></li></ul></div>
  </div>
</footer>
""" % {"root": root, "repo": REPO}


SCRIPT = """<script>
document.querySelectorAll(".copy button").forEach(function (b) {
  b.addEventListener("click", function () {
    var el = document.getElementById(b.dataset.for);
    function done() { b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy"; }, 1400); }
    function sel() { var r = document.createRange(); r.selectNodeContents(el); var s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = "Selected"; }
    try { navigator.clipboard.writeText(el.textContent).then(done, sel); } catch (e) { sel(); }
  });
});
(function () {
  var g = document.getElementById("gallery"); if (!g) return;
  var prev = document.getElementById("g-prev"), next = document.getElementById("g-next");
  function step() { var c = g.querySelector(".card"); return c ? c.getBoundingClientRect().width + 18 : 400; }
  function sync() { prev.disabled = g.scrollLeft < 8; next.disabled = g.scrollLeft + g.clientWidth > g.scrollWidth - 8; }
  prev.addEventListener("click", function () { g.scrollBy({ left: -step() }); });
  next.addEventListener("click", function () { g.scrollBy({ left: step() }); });
  g.addEventListener("scroll", sync, { passive: true }); window.addEventListener("resize", sync); sync();
})();
</script>
</body>
</html>
"""


def releases(n):
    rows = []
    for line in open(os.path.join(PLUGIN, "RELEASES.md")):
        m = re.match(r"\| \[V([\d.]+)\]\(([^)]+)\) \| ([\d-]+) \| (.+?) \|$", line.strip())
        if m:
            rows.append(m.groups())
    out = []
    for ver, url, date, what in rows[:n]:
        what = re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(what, quote=False))
        out.append('<li><span class="ver"><a href="%s" style="text-decoration:none">V%s</a></span>'
                   '<div><p>%s</p><span class="date">%s</span></div></li>' % (url, ver, what, date))
    return "\n".join(out)


def build_index():
    src = open(os.path.join(HERE, "index.src.html")).read()
    page = (head("Viaduct: PCB design for Claude Code",
                 "Describe a circuit board in plain English. Viaduct, a Claude Code plugin, designs it in KiCad and hands you Gerbers, BOM and pick-and-place files ready to order.", "")
            + topbar("", "") + src + footer("") + SCRIPT)
    for k, v in numbers().items():
        page = page.replace(k, v)
    page = (page.replace("{{claude}}", icon("claude")).replace("{{github}}", icon("github"))
            .replace("{{kicad}}", icon("kicad")).replace("{{releases}}", releases(4))
            .replace("{{star}}", STAR).replace("{{repo}}", REPO).replace("{{version}}", VERSION))
    open(os.path.join(OUT, "index.html"), "w").write(page)


def numbers():
    """The homepage's numbers strip. People comes from ~/Developer/viaduct-stats/stats.py
    (it writes stats.json here, locally; only the rounded number is published)."""
    people = "–"
    try:
        mid = json.load(open(os.path.join(HERE, "stats.json")))["estimate"]["mid"]
        people = "%d+" % (mid // 10 * 10) if mid >= 20 else str(mid)
    except (OSError, ValueError, KeyError):
        pass
    try:
        stars = str(json.load(urllib.request.urlopen("https://api.github.com/repos/virajrungta/viaduct", timeout=10))["stargazers_count"])
    except Exception:
        stars = "–"
    nrel = sum(1 for line in open(os.path.join(PLUGIN, "RELEASES.md")) if line.startswith("| [V"))
    nblocks = len([k for k in json.load(open(os.path.join(PLUGIN, "data", "blocks.json"))) if not k.startswith("_")])
    return {"{{people}}": people, "{{stars}}": stars, "{{nreleases}}": str(nrel), "{{nblocks}}": str(nblocks)}


def _gh(path):
    try:
        return json.load(urllib.request.urlopen("https://api.github.com/repos/virajrungta/viaduct" + path, timeout=10))
    except Exception:
        return None


def build_usage():
    """The Usage tab. Numbers are baked in at build time from the local stats.json that
    ~/Developer/viaduct-stats/stats.py writes; only these summaries are published.
    Repo counters and releases come from the public GitHub API."""
    try:
        d = json.load(open(os.path.join(HERE, "stats.json")))
    except (OSError, ValueError):
        return
    floor, share = d["assumptions"]["bot_floor"], d["assumptions"]["repeat"][1]
    days = [[x["date"], int(round(max(0, x["users"] - floor) * share))] for x in d["days"]]
    self_dl = d.get("self_downloads", {})
    engine = sum(max(0, n - self_dl.get(t, 0)) for t, n in d["engine_downloads"].items())
    updated = datetime.datetime.fromisoformat(d["updated"]).astimezone().strftime("%B %-d, %Y")

    repo = _gh("") or {}
    rels = []
    for r in (_gh("/releases?per_page=6") or []):
        when = datetime.datetime.fromisoformat(r["published_at"].replace("Z", "+00:00")).strftime("%b %-d")
        rels.append('<li><span class="gh-tag">%s</span>%s<span class="gh-when">%s</span></li>' % (
            html.escape(r["tag_name"]), ' <span class="gh-latest">Latest</span>' if not rels else "", when))
    vals = dict(numbers())
    vals.update({"{{u_people}}": vals["{{people}}"], "{{u_week}}": str(sum(n for _, n in days[-7:])),
                 "{{u_engine}}": str(engine), "{{u_updated}}": updated, "{{u_days}}": json.dumps(days),
                 "{{u_forks}}": str(repo.get("forks_count", "–")),
                 "{{u_watchers}}": str(repo.get("subscribers_count", "–")),
                 "{{u_releases}}": "\n".join(rels), "{{u_since}}": days[0][0] if days else "",
                 "{{github}}": icon("github"), "{{star}}": STAR, "{{repo}}": REPO, "{{version}}": VERSION})
    src = open(os.path.join(HERE, "usage.src.html")).read()
    for k, v in vals.items():
        src = src.replace(k, v)
    page = (head("Viaduct usage", "How many people use Viaduct, the PCB design plugin for Claude Code.", "")
            + topbar("", "usage") + src + footer(""))
    open(os.path.join(OUT, "usage.html"), "w").write(page)


def _fix_links(text):
    def repl(m):
        label, target = m.group(1), m.group(2)
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            return m.group(0)
        path, _, frag = target.partition("#")
        frag = ("#" + frag) if frag else ""
        base = os.path.basename(path)
        if path.endswith(".md") and base[:-3] in [d[0] for d in DOCS]:
            return "[%s](%s.html%s)" % (label, base[:-3], frag)
        if path.startswith("images/"):
            return "[%s](../img/docs/%s)" % (label, os.path.basename(path))
        clean = os.path.normpath(os.path.join("docs", path)).replace(os.sep, "/")
        kind = "tree" if not os.path.splitext(clean)[1] else "blob"
        return "[%s](%s/%s/main/%s%s)" % (label, REPO, kind, clean, frag)
    return re.sub(r"(?<!\!)\[([^\]]+)\]\(([^)\s]+)\)", repl, text)


def build_docs():
    out_dir = os.path.join(OUT, "docs")
    os.makedirs(out_dir, exist_ok=True)
    img_dir = os.path.join(OUT, "img", "docs")
    os.makedirs(img_dir, exist_ok=True)
    src_imgs = os.path.join(PLUGIN, "docs", "images")
    for f in os.listdir(src_imgs) if os.path.isdir(src_imgs) else []:
        shutil.copy(os.path.join(src_imgs, f), img_dir)
    for i, (name, title, _) in enumerate(DOCS):
        text = open(os.path.join(PLUGIN, "docs", name + ".md")).read()
        text = _fix_links(text)
        text = re.sub(r"!\[([^\]]*)\]\(images/([^)]+)\)", r"![\1](../img/docs/\2)", text)
        text = re.sub(r'src="images/', 'src="../img/docs/', text)
        md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                               extension_configs={"toc": {"toc_depth": "2-3"}})
        body = md.convert(text)
        body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.S)
        toc_items = "".join('<li><a href="#%s">%s</a></li>' % (t["id"], t["name"])
                            for t in (md.toc_tokens[0]["children"] if md.toc_tokens and md.toc_tokens[0]["level"] == 1
                                      else md.toc_tokens) if t["level"] == 2)
        nav, group = [], None
        for n, t, g in DOCS:
            if g != group:
                if group is not None:
                    nav.append("</ul>")
                nav.append("<h4>%s</h4><ul>" % g)
                group = g
            nav.append('<li><a href="%s.html"%s>%s</a></li>' % (n, ' aria-current="page"' if n == name else "", t))
        nav.append("</ul>")
        prev_ = DOCS[i - 1] if i > 0 else None
        next_ = DOCS[i + 1] if i + 1 < len(DOCS) else None
        pager = '<nav class="pager" aria-label="Pages">%s%s</nav>' % (
            ('<a href="%s.html"><small>Previous</small><span>%s</span></a>' % prev_[:2]) if prev_ else "<span></span>",
            ('<a class="next" href="%s.html"><small>Next</small><span>%s</span></a>' % next_[:2]) if next_ else "")
        page = (head("%s · Viaduct docs" % title, "%s: Viaduct, PCB design for Claude Code." % title, "../")
                + topbar("../", "docs")
                + '<main class="gutter"><div class="container docs">'
                + '<aside class="docs-nav" aria-label="Docs">%s</aside>' % "".join(nav)
                + '<article class="prose"><div class="crumb">Docs / %s</div><h1>%s</h1>%s%s</article>' % (
                    html.escape(DOCS[i][2]), html.escape(title), body, pager)
                + ('<aside class="toc"><h4>On this page</h4><ul>%s</ul></aside>' % toc_items if toc_items else "<aside></aside>")
                + "</div></main>" + footer("../") + SCRIPT)
        page = page.replace("/viaduct:", "/viaduct:")
        open(os.path.join(out_dir, name + ".html"), "w").write(page)


def copy_assets():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    for a in ASSETS:
        src = os.path.join(HERE, a)
        (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, os.path.join(OUT, a))
    open(os.path.join(OUT, ".nojekyll"), "w").close()


if __name__ == "__main__":
    copy_assets()
    build_index()
    build_usage()
    build_docs()
    print("built public/ (index + %d docs pages) from %s" % (len(DOCS), PLUGIN))
