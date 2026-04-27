# Cloudflare Pages Deployment

## Recommended settings

- Framework preset: None
- Build command: `bash scripts/build.sh`
- Build output directory: `dist`
- Production branch: `main`

## Environment variable

Add this variable in Cloudflare Pages:

```text
GOOGLE_MAPS_API_KEY=your-restricted-browser-key
```

The key is still visible in the browser after deployment, so it must be restricted in Google Cloud Console.

## Recommended HTTP referrer restrictions

```text
https://childandkid.com/*
https://www.childandkid.com/*
https://*.pages.dev/*
```

## API restrictions

Restrict the key to only the APIs the site needs, typically:

```text
Maps JavaScript API
Geocoding API
```

## Rollback

If deployment fails:

1. Revert the latest commit in GitHub, or
2. Roll back to the previous deployment in Cloudflare Pages, or
3. Remove the custom domain from the Pages project while debugging.
