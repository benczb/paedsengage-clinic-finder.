// PaedsENGAGE Clinic Finder Configuration
// Google Maps API key - use Cloudflare Pages env var GOOGLE_MAPS_API_KEY in production
const GOOGLE_MAPS_API_KEY = 'REPLACE_WITH_GOOGLE_MAPS_API_KEY';

// Site metadata
const SITE = {
  title: 'PaedsENGAGE Clinic Finder',
  subtitle: 'Find participating paediatric clinics in Singapore',
  accurateAsOf: 'Accurate as of 06 Jul 2026',
  source: 'KKH PaedsENGAGE participating clinics list',
  sourceUrl: 'https://www.kkh.com.sg/content/dam/singhealth-web/kkh/imported-assets/assets/documents/PaedsENGAGE-Clinics.pdf'
};

if (typeof module !== 'undefined') {
  module.exports = { SITE, GOOGLE_MAPS_API_KEY };
}
