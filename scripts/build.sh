#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
rm -rf "$DIST"
mkdir -p "$DIST/data"
cp "$ROOT/index.html" "$ROOT/app.js" "$ROOT/styles.css" "$DIST/"
cp "$ROOT/data/clinics.json" "$DIST/data/clinics.json"
cat > "$DIST/_redirects" <<'REDIRECTS'
# Canonical hostname
# Keep the working apex domain as the only public host.
https://www.childandkid.com/* https://childandkid.com/:splat 301!
http://www.childandkid.com/* https://childandkid.com/:splat 301!
REDIRECTS
cat > "$DIST/config.js" <<CONFIG
window.PAEDSENGAGE_CONFIG = {
  googleMapsApiKey: "${GOOGLE_MAPS_API_KEY:-REPLACE_WITH_GOOGLE_MAPS_API_KEY}",
  sourceLabel: "Participating PaedsENGAGE Clinics PDF (accurate as of 22 Jun 2026)",
  dataUrl: "./data/clinics.json",
};
CONFIG
