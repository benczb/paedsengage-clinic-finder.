# PaedsEngage Clinic Finder

A static clinic-finder website for participating PaedsENGAGE GP clinics in Singapore.

The site lets users search by area, clinic, address, doctor, opening day/time, and view matching results on Google Maps.

## Contents

```text
.
├── site/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   ├── config.js
│   └── data/
│       ├── clinics.json
│       └── clinics.csv
├── scripts/
│   └── build.sh
└── docs/
    └── cloudflare-pages.md
```

## Data source

Clinic data is derived from the official Participating PaedsENGAGE Clinics PDF marked accurate as of 13 April 2026.

Always verify clinic availability, doctor schedules, and opening hours directly with the clinic before visiting.

## Local preview

Because this site fetches JSON, use a local web server instead of opening `index.html` directly:

```bash
cd site
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Google Maps API key

`site/config.js` contains a placeholder key by default:

```js
googleMapsApiKey: "REPLACE_WITH_GOOGLE_MAPS_API_KEY"
```

For deployment, set `GOOGLE_MAPS_API_KEY` in Cloudflare Pages and use the build command below. Restrict the key in Google Cloud Console to your production and preview domains.

Required Google APIs:

- Maps JavaScript API
- Geocoding API, if using browser geocoding fallback

## Cloudflare Pages

Recommended settings:

- Framework preset: None
- Build command: `bash scripts/build.sh`
- Build output directory: `dist`

See `docs/cloudflare-pages.md`.

## Privacy / safety

This public repo should not contain unrestricted API keys, passwords, private notes, source PDFs, or local machine paths.

## License

MIT License. See `LICENSE`.
