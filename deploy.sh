#!/usr/bin/env bash
# Build the site and publish public/ to the main branch of viaduct-pcb/viaduct-pcb.github.io,
# served at https://viaduct-pcb.github.io/
set -euo pipefail
cd "$(dirname "$0")"
python3 build.py "${1:-../pcb-plugin}"
tmp="$(mktemp -d)"
cp -R public/. "$tmp/"
cd "$tmp"
git init -q -b main
git add -A
git commit -q -m "Site $(date +%Y-%m-%d)"
git push -q -f https://github.com/viaduct-pcb/viaduct-pcb.github.io.git main
cd - >/dev/null && rm -rf "$tmp"
echo "deployed to https://viaduct-pcb.github.io/"
