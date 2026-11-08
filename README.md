# Viaduct site

The website for [Viaduct](https://github.com/virajrungta/viaduct), PCB design for Claude Code: https://viaduct-pcb.github.io/

Plain HTML and CSS, built into `public/` and deployed with `./deploy.sh` to the `gh-pages` branch of virajrungta/viaduct. This repo's own Pages only redirects the old /viaduct-site address. The docs pages are generated from the plugin repo's `docs/`:

```bash
pip install markdown
./deploy.sh ../pcb-plugin   # build + publish; path to the viaduct plugin checkout
```

Edit `index.src.html` (home page content), `site.css` and `build.py` (header, footer, docs layout), then rebuild.
