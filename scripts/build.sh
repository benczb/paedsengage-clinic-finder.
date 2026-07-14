#!/bin/bash
set -euo pipefail
mkdir -p dist/data
cp -f data/clinics.json dist/data/clinics.json
if [ -n "${GOOGLE_MAPS_API_KEY:-}" ] && [ "${GOOGLE_MAPS_API_KEY}" != "REPLACE_WITH_GOOGLE_MAPS_API_KEY" ]; then
  sed "s/REPLACE_WITH_GOOGLE_MAPS_API_KEY/${GOOGLE_MAPS_API_KEY}/" config.js > dist/config.js
else
  cp config.js dist/config.js
fi
cp -f index.html dist/
cp -f app.js dist/
cp -f styles.css dist/
echo "Build complete: dist/ ready for Cloudflare Pages"
