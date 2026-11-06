# Viaduct site

The website for [Viaduct](https://github.com/virajrungta/viaduct), PCB design for Claude Code: https://virajrungta.github.io/viaduct-site/

Plain HTML and CSS, served by GitHub Pages from `main`. The docs pages are generated from the plugin repo's `docs/`:

```bash
pip install markdown
python3 build.py ../pcb-plugin   # path to the viaduct plugin checkout
```

Edit `index.src.html` (home page content), `site.css` and `build.py` (header, footer, docs layout), then rebuild.
