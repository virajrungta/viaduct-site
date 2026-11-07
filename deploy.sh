#!/usr/bin/env bash
# Build the site and publish public/ to the gh-pages branch of virajrungta/viaduct,
# served at https://virajrungta.github.io/viaduct/
set -euo pipefail
cd "$(dirname "$0")"
python3 build.py "${1:-../pcb-plugin}"
tmp="$(mktemp -d)"
cp -R public/. "$tmp/"
cd "$tmp"
git init -q -b gh-pages
git add -A
git commit -q -m "Site $(date +%Y-%m-%d)"
git push -q -f https://github.com/virajrungta/viaduct.git gh-pages
cd - >/dev/null && rm -rf "$tmp"
echo "deployed to https://virajrungta.github.io/viaduct/"
