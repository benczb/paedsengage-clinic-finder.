#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_ROOT="$ROOT/paedsengage-clinic-finder"
ROOT_DIST="$ROOT/dist"

if [ ! -f "$APP_ROOT/scripts/build.sh" ]; then
  echo "Nested app build script not found: $APP_ROOT/scripts/build.sh" >&2
  exit 1
fi

bash "$APP_ROOT/scripts/build.sh"
rm -rf "$ROOT_DIST"
mkdir -p "$ROOT_DIST"
cp -a "$APP_ROOT/dist/." "$ROOT_DIST/"

echo "Built PaedsEngage app to $ROOT_DIST"
