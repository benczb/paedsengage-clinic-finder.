// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://childandkid.com',
  output: 'static',
  // Trailing slashes for clean, consistent SEO URLs
  trailingSlash: 'always',
  integrations: [
    sitemap({
      // The sitemap plugin auto-generates sitemap-index.xml + sitemap-0.xml
      filter: (page) => !page.includes('/clinic/error') && page !== 'https://childandkid.com/404/',
      // Exclude the client-side-only search page from indexing params issues
    }),
  ],
  build: {
    // Inline smaller assets
    inlineStylesheets: 'auto',
  },
  vite: {
    build: {
      // lightningcss rejects some valid grouped/utility selectors with
      // "Invalid empty selector"; esbuild's CSS minifier is more lenient.
      cssMinify: 'esbuild',
    },
  },
  compressHTML: true,
});