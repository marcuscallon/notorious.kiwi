#!/usr/bin/env bash
# Stage the static site into dist/ for Cloudflare (Workers static assets / Pages).
#
# Mirrors what scripts/deploy.sh publishes to S3:
#   - src/ contents at the web root (assets, variants, profile.html ...)
#   - profile.html served as index.html
#   - Marcus-Callon-Executive-Profile.pdf at the web root (Download PDF button href)
#
# If --build is passed, the site is rebuilt from content/ first. The committed
# src/ artifacts are normally fresh (pre-commit hook), so plain staging is fine;
# use --build inside the Cloudflare build machine for belt-and-braces.
#
# Usage:
#   bash scripts/prepare-cloudflare.sh          # stage committed artifacts
#   bash scripts/prepare-cloudflare.sh --build  # rebuild content -> src/ first

set -euo pipefail
cd "$(dirname "$0")/.."

if [ "${1:-}" = "--build" ]; then
  echo "==> Building site from content/ ..."
  python3 scripts/build.py --variants
fi

if [ ! -f src/profile.html ]; then
  echo "error: src/profile.html missing - run 'just site' first" >&2
  exit 1
fi
if [ ! -f Marcus-Callon-Executive-Profile.pdf ]; then
  echo "error: Marcus-Callon-Executive-Profile.pdf missing - run 'just pdf' first" >&2
  exit 1
fi

echo "==> Staging dist/ ..."
rm -rf dist
mkdir -p dist
cp -RL src/. dist/   # -L dereferences symlinks (src/assets -> ../assets);
                     # Pages rejects output dirs containing links outside it
cp src/profile.html dist/index.html
cp Marcus-Callon-Executive-Profile.pdf dist/

echo "==> dist/ ready ($(find dist -type f | wc -l | tr -d ' ') files)"
