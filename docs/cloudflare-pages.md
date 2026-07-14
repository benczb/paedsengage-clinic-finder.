# PaedsEngage Cloudflare Pages Deployment

## Build Settings
- Build command: `bash scripts/build.sh`
- Build output directory: `dist`

## Environment Variables
- `GOOGLE_MAPS_API_KEY`: Optional. If set, injects the Google Maps API key into dist/config.js during build.

## Deployment
Push to `main` branch triggers Cloudflare Pages deployment.
