// JSON-LD structured-data builders for the PaedsEngage Clinic Finder.
// Generates schema.org markup that Astro pages inject via <script type="application/ld+json">.

const SITE = 'https://childandkid.com';

function escapeLd(text) {
  return String(text ?? '').replace(/</g, '\\u003c').replace(/>/g, '\\u003e');
}

/**
 * WebSite + Organization schema for the homepage.
 */
function webSiteSchema() {
  return {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebSite',
        '@id': `${SITE}/#website`,
        url: SITE,
        name: 'PaedsEngage Clinic Finder',
        description:
          'Find participating paediatric GP clinics in Singapore from the KKH and NUH PaedsENGAGE programme. Search by area, doctor and opening hours and get directions on Google Maps.',
        publisher: { '@id': `${SITE}/#organization` },
        inLanguage: 'en-SG',
      },
      {
        '@type': 'Organization',
        '@id': `${SITE}/#organization`,
        name: 'PaedsEngage Clinic Finder',
        url: SITE,
        logo: `${SITE}/favicon.svg`,
      },
    ],
  };
}

/**
 * MedicalBusiness / MedicalClinic schema for a single clinic detail page.
 */
function clinicSchema(clinic) {
  const mapsUrl = clinic.google_maps_url || '';

  // Extract the SG 6-digit postal code from the tail of the address
  // (e.g. "... Singapore 560416" -> "560416"), falling back to the last part.
  const postalMatch = (clinic.address || '').match(/\b(\d{6})\b/);
  const postalCode = postalMatch ? postalMatch[1] : '730000';
  const streetAddress = escapeLd(
    (clinic.address || '').replace(/,?\s*Singapore\s*\d{6}\s*$/i, '').trim(),
  );

  const openingHoursSpecification = [];
  const days = clinic.schedule ? clinic.schedule.days : [];
  for (const d of days) {
    const dayFull = {
      Mon: 'Monday',
      Tues: 'Tuesday',
      Wed: 'Wednesday',
      Thurs: 'Thursday',
      Fri: 'Friday',
      Sat: 'Saturday',
      Sun: 'Sunday',
    }[d.day];
    if (!dayFull || !d.time_blocks || d.time_blocks.length === 0) continue;
    for (const block of d.time_blocks) {
      if (block.overnight) {
        // Overnight blocks are rare and don't map cleanly to a single
        // openingHoursSpecification entry; represent as the next-day closure.
        openingHoursSpecification.push({
          '@type': 'OpeningHoursSpecification',
          dayOfWeek: dayFull,
          opens: block.start,
          closes: '23:59',
        });
      } else {
        openingHoursSpecification.push({
          '@type': 'OpeningHoursSpecification',
          dayOfWeek: dayFull,
          opens: block.start,
          closes: block.end,
        });
      }
    }
  }

  const doct = (clinic.doctors || []).map((name) => ({
    '@type': 'Physician',
    name: escapeLd(name),
  }));

  return {
    '@context': 'https://schema.org',
    '@type': ['MedicalClinic', 'LocalBusiness'],
    '@id': `${SITE}/clinic/${clinic.slug}/#clinic`,
    name: escapeLd(clinic.clinic_name),
    description: `PaedsENGAGE participating paediatric GP clinic in ${escapeLd(
      clinic.location,
    )}, Singapore. ${escapeLd(clinic.address)}. Participating in the KKH and NUH PaedsENGAGE programme.`,
    url: `${SITE}/clinic/${clinic.slug}/`,
    image: `${SITE}/favicon.svg`,
    address: {
      '@type': 'PostalAddress',
      streetAddress,
      addressLocality: escapeLd(clinic.location),
      addressRegion: 'Singapore',
      postalCode,
      addressCountry: 'SG',
    },
    telephone: clinic.contact_primary ? `+65${clinic.contact_primary}` : undefined,
    ...(mapsUrl ? { hasMap: mapsUrl } : {}),
    ...(openingHoursSpecification.length
      ? { openingHoursSpecification }
      : {}),
    ...(doct.length ? { medicalSpecialty: 'Pediatric', physician: doct } : {}),
    publisher: { '@id': `${SITE}/#organization` },
    isPartOf: `${SITE}/#website`,
    areaServed: 'Singapore',
    medicalSpecialty: 'Pediatric',
  };
}

/**
 * ItemList schema for a neighbourhood listing page.
 */
function locationListSchema(locationGroup) {
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: `Paediatrics GP clinics in ${locationGroup.location}, Singapore`,
    description: `${locationGroup.count} PaedsENGAGE participating clinics in ${locationGroup.location}.`,
    numberOfItems: locationGroup.count,
    itemListElement: locationGroup.clinics.map((c, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: escapeLd(c.clinic_name),
      url: `${SITE}/clinic/${c.slug}/`,
    })),
  };
}

export { webSiteSchema, clinicSchema, locationListSchema };