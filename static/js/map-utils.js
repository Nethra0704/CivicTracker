/**
 * CivicTrack-AI - Map Utilities & Leaflet OpenStreetMap Engine
 * Official OpenStreetMap Tiles, Dynamic Severity Markers & GPS Tracking
 */

const MapUtils = {
  // Official OpenStreetMap tile URL (No paid API keys, zero Google dependencies)
  TILE_URL: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  TILE_ATTRIB: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',

  // Default coordinate: Coimbatore, Tamil Nadu (11.0168, 76.9558)
  DEFAULT_CENTER: [11.0168, 76.9558],
  DEFAULT_ZOOM: 13,

  /**
   * Initialize a responsive Leaflet map instance with OpenStreetMap tiles
   */
  initMap(elementId, centerLat = 11.0168, centerLon = 76.9558, zoom = 13) {
    const el = document.getElementById(elementId);
    if (!el) return null;

    // If map already initialized on this element, remove it first
    if (el._leaflet_id && el._leaflet_map) {
      try { el._leaflet_map.remove(); } catch (e) {}
    }

    const map = L.map(elementId, {
      center: [centerLat, centerLon],
      zoom: zoom,
      zoomControl: true,
      scrollWheelZoom: true,
      dragging: true,
      touchZoom: true
    });

    el._leaflet_map = map;

    // Add standard OpenStreetMap Tile Layer
    L.tileLayer(this.TILE_URL, {
      attribution: this.TILE_ATTRIB,
      maxZoom: 19,
      minZoom: 3,
      crossOrigin: true
    }).addTo(map);

    // Invalidate size on load & resize to ensure full rendering without gray areas
    setTimeout(() => {
      map.invalidateSize();
    }, 200);

    window.addEventListener('resize', () => {
      if (map) map.invalidateSize();
    });

    return map;
  },

  /**
   * Create custom styled marker using severity-based colors:
   * - Green: Resolved reports (Completed)
   * - Red: High severity
   * - Orange: Medium severity
   * - Yellow: Low severity
   */
  createHazardMarker(lat, lon, priority = 'Medium', status = 'Pending', category = 'Pothole') {
    let pinColorClass = 'pin-medium'; // default orange

    if (status === 'Completed' || status === 'Resolved') {
      pinColorClass = 'pin-resolved'; // Green
    } else {
      const p = (priority || '').toLowerCase();
      if (p === 'high') {
        pinColorClass = 'pin-high';   // Red
      } else if (p === 'medium') {
        pinColorClass = 'pin-medium'; // Orange
      } else if (p === 'low') {
        pinColorClass = 'pin-low';    // Yellow
      }
    }

    let iconChar = '⚠️';
    const catLower = (category || '').toLowerCase();
    if (status === 'Completed' || status === 'Resolved') {
      iconChar = '✓';
    } else if (catLower.includes('water')) {
      iconChar = '🌊';
    } else if (catLower.includes('manhole')) {
      iconChar = '⭕';
    } else if (catLower.includes('guardrail') || catLower.includes('barrier')) {
      iconChar = '🚧';
    } else if (catLower.includes('light')) {
      iconChar = '💡';
    } else if (catLower.includes('crack')) {
      iconChar = '⚡';
    }

    const customIcon = L.divIcon({
      className: 'custom-pin-marker',
      html: `<div class="pin-icon ${pinColorClass}"><span>${iconChar}</span></div>`,
      iconSize: [34, 34],
      iconAnchor: [17, 17],
      popupAnchor: [0, -20]
    });

    return L.marker([lat, lon], { icon: customIcon });
  },

  /**
   * Build complete informative popup for road issues as required:
   * - Report ID
   * - Road issue type
   * - Severity
   * - Description
   * - Location
   * - Report status
   * - Uploaded image, if available
   */
  buildReportPopup(r) {
    const hasImage = r.image_path && r.image_path.trim() !== '';
    const imgHtml = hasImage 
      ? `<div class="popup-thumb-wrap">
           <img src="${r.image_path}" alt="${r.category || 'Road Issue'}" class="popup-thumb" onerror="this.style.display='none'">
         </div>`
      : '';

    let statusBadgeClass = 'badge-status-pending';
    if (r.status === 'Completed') statusBadgeClass = 'badge-status-completed';
    else if (r.status === 'In Progress') statusBadgeClass = 'badge-status-inprogress';

    let priorityBadgeClass = 'badge-priority-medium';
    if (r.priority === 'High') priorityBadgeClass = 'badge-priority-high';
    else if (r.priority === 'Low') priorityBadgeClass = 'badge-priority-low';

    return `
      <div class="report-marker-popup">
        ${imgHtml}
        <div class="popup-content-inner">
          <div class="popup-header-row">
            <span class="popup-report-id">Report ID: #${r.id}</span>
            <span class="badge ${statusBadgeClass}">${r.status}</span>
          </div>

          <div class="popup-issue-type">
            <span>⚠️</span> ${r.category || 'Road Issue'}
          </div>

          <div class="popup-meta-row">
            <span class="badge ${priorityBadgeClass}">Severity: ${r.priority} (${r.severity_score || 50}/100)</span>
          </div>

          <div class="popup-location-row">
            <span>📍</span> <b>Location:</b> ${r.location_name || 'Unspecified'}
          </div>

          <div class="popup-desc-row">
            <b>Description:</b> ${r.description || 'No description provided'}
          </div>

          <div class="popup-footer-row">
            <a href="/report/${r.id}" class="btn btn-outline-cyan btn-sm" style="width:100%; text-align:center; display:block;">
              Inspect Full Report &rarr;
            </a>
          </div>
        </div>
      </div>
    `;
  },

  /**
   * Reverse Geocode Lat/Lon to readable street / locality name using Nominatim
   */
  async reverseGeocode(lat, lon) {
    try {
      const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&addressdetails=1`;
      const resp = await fetch(url, {
        headers: { 'Accept-Language': 'en' }
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.display_name) {
          const addr = data.address || {};
          const parts = [
            addr.road || addr.suburb || addr.neighbourhood,
            addr.city_district || addr.city || addr.town || addr.county,
            addr.state
          ].filter(Boolean);

          return parts.length > 0 ? parts.join(', ') : data.display_name.split(',').slice(0, 3).join(', ');
        }
      }
    } catch (e) {
      console.warn('Reverse geocoding warning:', e);
    }
    return `Location (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
  },

  /**
   * Geocode a place name to lat/lon using Nominatim
   */
  async geocode(query) {
    try {
      const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1&countrycodes=in`;
      const resp = await fetch(url);
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.length > 0) {
          return {
            lat: parseFloat(data[0].lat),
            lon: parseFloat(data[0].lon),
            display_name: data[0].display_name
          };
        }
      }
    } catch (e) {
      console.warn('Geocoding warning:', e);
    }
    return null;
  },

  /**
   * Get Current GPS Position of the device
   */
  getCurrentPosition() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by your browser.'));
      } else {
        navigator.geolocation.getCurrentPosition(
          (pos) => resolve({
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            accuracy: pos.coords.accuracy
          }),
          (err) => reject(err),
          { timeout: 12000, enableHighAccuracy: true, maximumAge: 0 }
        );
      }
    });
  },

  /**
   * Trigger GPS Location Detection, update map & add pulsing user marker
   */
  async detectAndShowUserLocation(map, buttonElement = null) {
    if (!map) return;

    if (buttonElement) {
      buttonElement.disabled = true;
      buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting Location...';
    }

    try {
      const pos = await this.getCurrentPosition();
      const userLat = pos.lat;
      const userLon = pos.lon;

      // Create glowing user location pin
      const userIcon = L.divIcon({
        className: 'custom-pin-marker',
        html: `<div class="pin-icon pin-user-location"><span>📍</span></div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
        popupAnchor: [0, -20]
      });

      // Remove existing user marker if any
      if (map._userLocationMarker) {
        map.removeLayer(map._userLocationMarker);
      }

      const userMarker = L.marker([userLat, userLon], { icon: userIcon }).addTo(map);
      map._userLocationMarker = userMarker;

      const address = await this.reverseGeocode(userLat, userLon);
      userMarker.bindPopup(`
        <div style="padding:10px; min-width:180px;">
          <div style="font-weight:700; color:#38bdf8; margin-bottom:4px;">📍 Your Current Location</div>
          <div style="font-size:0.85rem; color:#fff;">${address}</div>
          <div style="font-size:0.75rem; color:#94a3b8; margin-top:4px;">GPS: ${userLat.toFixed(5)}, ${userLon.toFixed(5)}</div>
        </div>
      `).openPopup();

      map.setView([userLat, userLon], 15, { animate: true });
      map.invalidateSize();

      if (typeof showToast === 'function') {
        showToast(`Location detected: ${address.substring(0, 40)}...`, 'success');
      }
      return { lat: userLat, lon: userLon, address };
    } catch (err) {
      let errorMsg = 'Could not detect your location.';
      if (err.code === 1) {
        errorMsg = 'Location access denied. Please enable location permissions in your browser.';
      } else if (err.code === 2) {
        errorMsg = 'Location unavailable. Please check your network/GPS connection.';
      } else if (err.code === 3) {
        errorMsg = 'Location request timed out. Please try again.';
      }

      if (typeof showToast === 'function') {
        showToast(errorMsg, 'danger');
      } else {
        alert(errorMsg);
      }
      return null;
    } finally {
      if (buttonElement) {
        buttonElement.disabled = false;
        buttonElement.innerHTML = '<i class="fas fa-location-crosshairs"></i> Detect My Location';
      }
    }
  }
};
