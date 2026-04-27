# PaedsEngage Clinic Finder

A static clinic-finder website for participating PaedsENGAGE GP clinics in Singapore.

The site lets users search by area, clinic name, address, doctor, opening day/time, and view matching results on Google Maps.

## What this site does

The clinic finder provides:

- Search by clinic, location, address, or doctor name
- Location filtering
- Day and time filtering
- "Open now" filtering based on Singapore time
- Paginated clinic results
- Google Maps display for visible results
- Direct Google Maps links for each clinic

## Repository contents

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   └── cloudflare-pages.md
├── scripts/
│   └── build.sh
└── site/
    ├── index.html
    ├── app.js
    ├── styles.css
    ├── config.js
    └── data/
        ├── clinics.json
        └── clinics.csv
```

## Data source

Clinic data is derived from the official Participating PaedsENGAGE Clinics PDF marked accurate as of 13 April 2026.

Always verify clinic availability, doctor schedules, and opening hours directly with the clinic before visiting.

## Local preview

Because the site fetches JSON data, use a local web server instead of opening `index.html` directly.

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

For deployment, set the real key as an environment variable in Cloudflare Pages:

```text
GOOGLE_MAPS_API_KEY=your-restricted-browser-key
```

The Google Maps key is visible in the browser after deployment, so it must be restricted in Google Cloud Console.

Recommended APIs:

- Maps JavaScript API
- Geocoding API, if using browser geocoding fallback

Recommended HTTP referrer restrictions:

```text
https://childandkid.com/*
https://www.childandkid.com/*
https://*.pages.dev/*
```

## Cloudflare Pages deployment

Recommended Cloudflare Pages settings:

```text
Framework preset: None
Build command: bash scripts/build.sh
Build output directory: dist
Production branch: main
```

The build script copies the `site/` folder into `dist/` and injects the `GOOGLE_MAPS_API_KEY` environment variable into `dist/config.js`.

See also:

```text
docs/cloudflare-pages.md
```

## Manual GitHub upload

If uploading manually:

1. Create a new GitHub repository, for example `paedsengage-clinic-finder`.
2. Extract the ZIP file locally.
3. Upload the extracted contents to GitHub, not the ZIP file itself.
4. Commit directly to `main`.
5. Connect the GitHub repo to Cloudflare Pages.
6. Add the `GOOGLE_MAPS_API_KEY` environment variable in Cloudflare Pages.
7. Deploy using the Cloudflare Pages settings above.

## Privacy and safety notes

This public repo should not contain:

- Unrestricted API keys
- Passwords or secrets
- Private notes
- Source PDFs unless redistribution is allowed
- Local machine paths
- Raw parser work products

The included `site/config.js` should keep the placeholder API key only. The live key should be injected during deployment.

## Important limitations

- Clinic data is extracted from a PDF and should be spot-checked before publication.
- Google Maps URLs are search links and may not confirm exact Google Place IDs.
- Opening hours and doctor availability may change. Users should confirm with clinics directly.
- Browser-side Google Maps keys are public by nature, so API and domain restrictions are essential.

## Rollback plan

If deployment fails:

1. Roll back to the previous Cloudflare Pages deployment, or
2. Revert the latest GitHub commit, or
3. Temporarily remove the custom domain from the Pages project while debugging.

If the uploaded GitHub repository is wrong, delete the repository or replace the files with a corrected upload.

## License

MIT License.
