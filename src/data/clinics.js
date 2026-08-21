// Data layer for the PaedsEngage Clinic Finder Astro site.
// Loads the clinic dataset from the repo's data/clinics.json and provides
// slug generation, location grouping, and helpers used by the SSG pages.

import rawClinics from '../../data/clinics.json';

// ---------------------------------------------------------------------------
// Slug helpers
// ---------------------------------------------------------------------------

const slugifyCache = new Map();

/**
 * Turn any clinic/location string into a URL-safe ASCII slug.
 * e.g. "Ang Mo Kio" -> "ang-mo-kio", "Appletree Medical" -> "appletree-medical"
 */
function slugify(input) {
  const key = String(input);
  if (slugifyCache.has(key)) return slugifyCache.get(key);
  const slug = key
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    // allow apostrophe removal: "Women's" -> "womens"
    .replace(/['’]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
  slugifyCache.set(key, slug);
  return slug;
}

/**
 * Clinic detail slug: "<location>-<clinic-name>" which is unique for every
 * clinic (verified against the full 535-clinic dataset) and carries both
 * the neighbourhood and the clinic name as URL keywords for local SEO.
 * e.g. "Ang Mo Kio" + "Appletree Medical" -> "ang-mo-kio-appletree-medical"
 */
function clinicSlug(clinic) {
  return `${slugify(clinic.location)}-${slugify(clinic.clinic_name)}`;
}

/**
 * Location page slug: just the neighbourhood, e.g. "bedok".
 */
function locationSlug(location) {
  return slugify(location);
}

// ---------------------------------------------------------------------------
// Derived data
// ---------------------------------------------------------------------------

const clinics = rawClinics.map((c, i) => ({
  ...c,
  slug: clinicSlug(c),
  // stable fallback key not exposed publicly
  _index: i,
}));

/**
 * Group clinics by location, returning an array sorted alphabetically:
 * [{ location, slug, count, clinics }]
 */
const locations = (() => {
  const byLocation = new Map();
  for (const clinic of clinics) {
    const loc = clinic.location;
    if (!byLocation.has(loc)) {
      byLocation.set(loc, {
        location: loc,
        slug: locationSlug(loc),
        clinics: [],
      });
    }
    byLocation.get(loc).clinics.push(clinic);
  }
  const list = [...byLocation.values()].sort((a, b) =>
    a.location.localeCompare(b.location),
  );
  for (const l of list) l.count = l.clinics.length;
  return list;
})();

/** Map slug -> location group for fast lookup in dynamic routes. */
const locationBySlug = new Map(locations.map((l) => [l.slug, l]));

/** Map clinic slug -> clinic for fast lookup in dynamic routes. */
const clinicBySlug = new Map(clinics.map((c) => [c.slug, c]));

// ---------------------------------------------------------------------------
// Human-readable helpers
// ---------------------------------------------------------------------------

const dayShortToFull = {
  Mon: 'Monday',
  Tues: 'Tuesday',
  Wed: 'Wednesday',
  Thurs: 'Thursday',
  Fri: 'Friday',
  Sat: 'Saturday',
  Sun: 'Sunday',
  PH: 'Public holiday',
};

function fullDayName(shortDay) {
  return dayShortToFull[shortDay] || shortDay;
}

/**
 * Build a one-line summary of a clinic's opening schedule for meta descriptions
 * and top-of-page context, e.g. "Mon - Fri 9:00am-12:00pm & 1:00pm-3:00pm; Sat 9:00am-12:00pm".
 */
function scheduleSummary(clinic) {
  const days = clinic.schedule ? clinic.schedule.days : [];
  const parts = [];
  for (const day of days) {
    if (!day.time_blocks || day.time_blocks.length === 0) {
      parts.push(`${fullDayName(day.day)}: closed`);
      continue;
    }
    const times = day.time_blocks.map((b) => b.display).join(' & ');
    parts.push(`${fullDayName(day.day)}: ${times}`);
  }
  return parts.join('; ');
}

export {
  clinics,
  locations,
  locationBySlug,
  clinicBySlug,
  slugify,
  clinicSlug,
  locationSlug,
  fullDayName,
  scheduleSummary,
};