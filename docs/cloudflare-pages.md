# Cloudflare Pages Deployment

The site is a static **Astro** build deployed to Cloudflare Pages via the
GitHub Git integration.

## Recommended Cloudflare Pages settings

In the Cloudflare Pages project (Workers & Pages > childandkid project >
Settings > Build & deployments):

| Setting | Value |
|---|---|
| Production branch | `main` |
| Framework preset | `Astro` |
| Build command | `bash scripts/build.sh` |
| Build output directory | `dist` |
| Node version | **22+** (Astro 7 requires Node `>=22.12.0`) |

If the Framework preset list has no "Astro", set it to **None** and use the
build command + output above.

The build command runs `npm ci`, then `npm run build` (which first copies
`data/clinics.json` into `public/data/` via the `prebuild` step).

> Note: the legacy site used build output `/` or `.` (repository root). With
> Astro the output is now **`dist`** — this must be changed in the Pages
> settings or the deploy will serve stale files.

## Required / optional environment variable

```text
PUBLIC_GOOGLE_MAPS_API_KEY=<your-restricted-browser-key>
```

This is an **Astro build-time public variable** (must be prefixed `PUBLIC_`).
If it is not set, the clinic search and results still load; only the interactive
map panel is disabled (same behaviour as the legacy site).

> The legacy build used `GOOGLE_MAPS_API_KEY` (no `PUBLIC_` prefix). That name
> will NOT be picked up by Astro. Rename it to `PUBLIC_GOOGLE_MAPS_API_KEY`.

## Custom domain and redirects

- Apex `childandkid.com` should be attached to this Pages project.
- `www.childandkid.com` is redirected to the apex via `public/_redirects`
  (copied into `dist/_redirects` by Astro).
- `public/_redirects` also canonicalises trailing slashes for `/clinic/...` and
  `/clinics/...` so Google does not see duplicate URLs.

## Verifying a deployment

After a successful build, check:

1. `https://childandkid.com/` returns 200 with the new homepage.
2. `https://childandkid.com/sitemap-index.xml` exists (sitemap).
3. A sample clinic page, e.g. `https://childandkid.com/clinic/ang-mo-kio-appletree-medical/`, returns 200 and contains JSON-LD.
4. `https://childandkid.com/robots.txt` points at the sitemap.
5. `https://childandkid.com/data/clinics.json` serves the dataset for the client search.