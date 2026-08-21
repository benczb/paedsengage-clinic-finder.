// Prepare-data build step: copies the source-of-truth clinic dataset
// (data/clinics.json at the repo root) into public/data/clinics.json so the
// built site serves it at /data/clinics.json for the client-side search.
// This keeps a single source of truth (the PDF-parser output) and avoids
// committing a duplicated dataset under public/.

import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');

const src = join(root, 'data', 'clinics.json');
const destDir = join(root, 'public', 'data');
const dest = join(destDir, 'clinics.json');

mkdirSync(destDir, { recursive: true });
copyFileSync(src, dest);

console.log(`[prepare-data] copied ${src} -> ${dest}`);