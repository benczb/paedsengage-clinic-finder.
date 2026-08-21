#!/usr/bin/env bash
# Build wrapper for the Astro-powered PaedsEngage Clinic Finder.
# Cloudflare Pages runs this as the build command, with the output at `dist`.
#
# Required env: none.
# Optional env: PUBLIC_GOOGLE_MAPS_API_KEY (Astro build-time public var) -
#   injects the Google Maps browser key into the client bundle. Without it the
#   clinic search and results still load; only the interactive map panel is
#   disabled (same behaviour as the legacy site).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[build] Installing dependencies (npm ci)"
npm ci

echo "[build] Running Astro build (prebuild copies data/clinics.json -> public/data)"
npm run build

echo "[build] Build complete. Output: $ROOT/dist"

# Copy the canonical www->apex redirect (already emitted into dist by Astro
# from public/_redirects) - no action needed; just report.
echo "[build] dist/_redirects present: $(test -f dist/_redirects && echo yes || echo no)"