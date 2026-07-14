// PaedsENGAGE Clinic Finder - Main Application
(function() {
  'use strict';

  let clinics = [];
  let map = null;
  let markers = [];

  async function loadClinics() {
    try {
      const resp = await fetch('data/clinics.json');
      if (!resp.ok) throw new Error('Failed to load clinics.json');
      clinics = await resp.json();
      populateLocationFilter();
      updateSummary();
      renderClinics(clinics);
    } catch(e) {
      console.error('Error loading clinics:', e);
      document.getElementById('clinicList').innerHTML = '<p class="no-results">Failed to load clinic data.</p>';
    }
  }

  function populateLocationFilter() {
    const locations = [...new Set(clinics.map(c => c.location))].sort();
    const sel = document.getElementById('locationFilter');
    locations.forEach(loc => {
      const opt = document.createElement('option');
      opt.value = loc;
      opt.textContent = loc;
      sel.appendChild(opt);
    });
  }

  function updateSummary() {
    const locs = new Set(clinics.map(c => c.location)).size;
    document.getElementById('summary').innerHTML = 
      '<p>Showing ' + clinics.length + ' clinics across ' + locs + ' locations</p>';
  }

  function matchesDay(clinic, day) {
    if (!clinic.schedule || !clinic.schedule.days) return true;
    return clinic.schedule.days.some(d => d.day === day);
  }

  function renderClinics(data) {
    const list = document.getElementById('clinicList');
    if (data.length === 0) {
      list.innerHTML = '<p class="no-results">No clinics match your search.</p>';
      return;
    }
    list.innerHTML = data.map(c => {
      const doctors = c.doctors && c.doctors.length ? c.doctors.join(', ') : '';
      const phone = c.contact_primary ? '<a href="tel:+65' + c.contact_primary + '">📞 ' + c.contact_primary + '</a>' : '';
      const hours = c.operating_hours_text && c.operating_hours_text.length ? 
        c.operating_hours_text.slice(0, 3).join('; ') : '';
      const mapsUrl = c.google_maps_url || '';
      return '<div class="clinic-card">' +
        '<h3>' + (c.clinic_name || 'Unknown') + '</h3>' +
        '<div class="location">' + (c.location || '') + '</div>' +
        '<div class="address">' + (c.address || '') + '</div>' +
        '<div class="phone">' + phone + '</div>' +
        (doctors ? '<div class="doctors">👨‍⚕️ ' + doctors + '</div>' : '') +
        (hours ? '<div class="hours">🕐 ' + hours + '</div>' : '') +
        (mapsUrl ? '<div class="maps-link"><a href="' + mapsUrl + '" target="_blank">🗺️ View on Google Maps</a></div>' : '') +
      '</div>';
    }).join('');
  }

  function filterClinics() {
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    const loc = document.getElementById('locationFilter').value;
    const day = document.getElementById('dayFilter').value;

    let filtered = clinics;
    if (loc) filtered = filtered.filter(c => c.location === loc);
    if (day) filtered = filtered.filter(c => matchesDay(c, day));
    if (query) {
      filtered = filtered.filter(c => {
        const haystack = [c.clinic_name, c.location, c.address, c.contact_primary].join(' ').toLowerCase();
        const docs = (c.doctors || []).join(' ').toLowerCase();
        return haystack.includes(query) || docs.includes(query);
      });
    }
    renderClinics(filtered);
    updateSummary();
    updateMapMarkers(filtered);
  }

  function updateMapMarkers(data) {
    if (!map || typeof google === 'undefined') return;
    markers.forEach(m => m.setMap(null));
    markers = [];
    const center = data.length > 0 ? 
      new google.maps.LatLng(1.3521, 103.8198) : 
      new google.maps.LatLng(1.3521, 103.8198);
    map.setCenter(center);
    const bounds = new google.maps.LatLngBounds();
    data.forEach(c => {
      // Use Google Maps search URL - simplified marker approach
      if (c.address) {
        // We rely on the search links since we don't have coordinates
      }
    });
  }

  function initMap() {
    if (typeof google === 'undefined') {
      document.getElementById('map-container').innerHTML = '<p class="no-results">Map requires Google Maps API key configuration.</p>';
      return;
    }
    map = new google.maps.Map(document.getElementById('map-container'), {
      center: { lat: 1.3521, lng: 103.8198 },
      zoom: 11,
      disableDefaultUI: true
    });
  }

  // Event listeners
  document.addEventListener('DOMContentLoaded', function() {
    loadClinics();
    document.getElementById('searchInput').addEventListener('input', filterClinics);
    document.getElementById('locationFilter').addEventListener('change', filterClinics);
    document.getElementById('dayFilter').addEventListener('change', filterClinics);
    if (typeof GOOGLE_MAPS_API_KEY !== 'undefined' && GOOGLE_MAPS_API_KEY && GOOGLE_MAPS_API_KEY !== 'REPLACE_WITH_GOOGLE_MAPS_API_KEY') {
      const script = document.createElement('script');
      script.src = 'https://maps.googleapis.com/maps/api/js?key=' + GOOGLE_MAPS_API_KEY + '&libraries=places';
      script.onload = initMap;
      document.head.appendChild(script);
    }
  });
})();
