#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
rm -rf "$DIST"
mkdir -p "$DIST"
cp -a "$ROOT/site/." "$DIST/"
cat > "$DIST/config.js" <<CONFIG
window.PAEDSENGAGE_CONFIG = {
  googleMapsApiKey: "${GOOGLE_MAPS_API_KEY:-REPLACE_WITH_GOOGLE_MAPS_API_KEY}",
  sourceLabel: "Participating PaedsENGAGE Clinics PDF (accurate as of 13 April 2026)",
  dataUrl: "./data/clinics.json",
};
CONFIG
