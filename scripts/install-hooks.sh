#!/usr/bin/env bash
# Install local git hooks. Run once per clone.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$ROOT/.git/hooks"
SOURCE_DIR="$ROOT/scripts/hooks"

mkdir -p "$HOOKS_DIR"

for hook in "$SOURCE_DIR"/*; do
  name="$(basename "$hook")"
  target="$HOOKS_DIR/$name"

  # Remove any existing hook before linking
  rm -f "$target"
  ln -s "$hook" "$target"
  chmod +x "$target"
  echo "installed $name hook"
done

echo "Done. Git hooks are active for this clone."
