/**
 * CivicTrack-AI - Safe Journey Planner Frontend Engine
 * Computes safety-conscious routes, visualizes hazard corridors,
 * displays toll estimates, traffic levels, and safe alternative recommendations.
 */

const JourneyPlanner = {
  map: null,
  routePolyline: null,
  corridorLayerGroup: null,
  markersLayerGroup: null,

  init() {
    this.initMap();
    this.bindForm();
    this.bindQuickPresets();
  },

  initMap() {
    const mapEl = document.getElementById('plannerMap');
    if (!mapEl) return;

    // Centered on Coimbatore, Tamil Nadu
    this.map = MapUtils.initMap('plannerMap', 11.0168, 76.9558, 12);
    this.corridorLayerGroup = L.featureGroup().addTo(this.map);
    this.markersLayerGroup = L.featureGroup().addTo(this.map);
  },

  bindForm() {
    const form = document.getElementById('journeyPlannerForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const startLoc = document.getElementById('plannerStartInput').value.trim();
      const destLoc = document.getElementById('plannerDestInput').value.trim();

      if (!startLoc || !destLoc) {
        showToast('Please enter both origin and destination.', 'warning');
        return;
      }

      await this.calculateRoute(startLoc, destLoc);
    });
  },

  bindQuickPresets() {
    document.querySelectorAll('[data-route-preset]').forEach(btn => {
      btn.addEventListener('click', () => {
        const start = btn.dataset.start;
        const dest = btn.dataset.dest;

        document.getElementById('plannerStartInput').value = start;
        document.getElementById('plannerDestInput').value = dest;

        this.calculateRoute(start, dest);
      });
    });
  },

  async calculateRoute(startLoc, destLoc) {
    const calcBtn = document.getElementById('planJourneySubmitBtn');
    const loadingCard = document.getElementById('plannerLoadingState');
    const resultsPanel = document.getElementById('plannerResultsPanel');

    if (calcBtn) {
      calcBtn.disabled = true;
      calcBtn.innerHTML = '<i class="fas fa-satellite-dish fa-spin"></i> Analyzing Route & Hazards...';
    }

    if (loadingCard) loadingCard.style.display = 'block';
    if (resultsPanel) resultsPanel.style.display = 'none';

    try {
      const resp = await fetch('/api/journey/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_location: startLoc,
          destination: destLoc
        })
      });

      const data = await resp.json();
      if (resp.ok && data.success) {
        this.renderRoutePlan(data.plan);
        showToast(`Route computed! Safety level: ${data.plan.safety_level}`, 'info');
      } else {
        showToast(data.error || 'Failed to compute route.', 'danger');
      }
    } catch (e) {
      showToast('Error connecting to route engine.', 'danger');
    } finally {
      if (calcBtn) {
        calcBtn.disabled = false;
        calcBtn.innerHTML = '<span>⚡</span> Analyze Safe Route';
      }
      if (loadingCard) loadingCard.style.display = 'none';
    }
  },

  renderRoutePlan(plan) {
    const resultsPanel = document.getElementById('plannerResultsPanel');
    if (!resultsPanel || !this.map) return;

    // 1. Clear previous layers
    this.corridorLayerGroup.clearLayers();
    this.markersLayerGroup.clearLayers();

    // 2. Draw Start & End Markers
    const startIcon = L.divIcon({
      className: 'custom-pin-marker',
      html: `<div class="pin-icon" style="background:#10b981; border-color:#fff;"><span>🟢</span></div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });
    const destIcon = L.divIcon({
      className: 'custom-pin-marker',
      html: `<div class="pin-icon" style="background:#3b82f6; border-color:#fff;"><span>🏁</span></div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });

    const startMarker = L.marker(plan.start_coords, { icon: startIcon }).bindPopup(`<b>Origin:</b> ${plan.start_location}`);
    const destMarker = L.marker(plan.end_coords, { icon: destIcon }).bindPopup(`<b>Destination:</b> ${plan.destination}`);
    
    this.markersLayerGroup.addLayer(startMarker);
    this.markersLayerGroup.addLayer(destMarker);

    // 3. Draw Route Polyline
    this.routePolyline = L.polyline(plan.waypoints, {
      color: plan.risk_color,
      weight: 6,
      opacity: 0.9,
      lineCap: 'round',
      lineJoin: 'round'
    });
    this.corridorLayerGroup.addLayer(this.routePolyline);

    // Draw Route Glow corridor
    const glowLine = L.polyline(plan.waypoints, {
      color: plan.risk_color,
      weight: 14,
      opacity: 0.22,
      lineCap: 'round'
    });
    this.corridorLayerGroup.addLayer(glowLine);

    // 4. Draw Hazards along the corridor
    plan.hazards.forEach(h => {
      const hMarker = MapUtils.createHazardMarker(
        h.latitude,
        h.longitude,
        h.priority,
        h.status || 'Pending',
        h.category
      );

      const popupHtml = MapUtils.buildReportPopup(h);
      hMarker.bindPopup(popupHtml, { maxWidth: 320 });
      this.markersLayerGroup.addLayer(hMarker);
    });

    // Fit map bounds to encompass the entire route
    const allLayers = [this.routePolyline, startMarker, destMarker];
    const group = L.featureGroup(allLayers);
    this.map.fitBounds(group.getBounds(), { padding: [50, 50] });

    // 5. Update DOM UI Cards
    this.updateResultsDOM(plan);
    resultsPanel.style.display = 'flex';
  },

  updateResultsDOM(plan) {
    // Risk Card
    const riskCard = document.getElementById('routeRiskCard');
    const riskBadge = document.getElementById('routeRiskBadge');
    const riskDesc = document.getElementById('routeRiskDesc');

    let cardClass = 'risk-card-safe';
    if (plan.safety_level === 'High Risk') cardClass = 'risk-card-danger';
    else if (plan.safety_level === 'Moderate Risk') cardClass = 'risk-card-moderate';

    if (riskCard) riskCard.className = `risk-summary-card ${cardClass}`;
    if (riskBadge) {
      riskBadge.className = `badge ${plan.safety_badge_class}`;
      riskBadge.innerHTML = `<span class="badge-dot"></span> ${plan.safety_level}`;
    }
    if (riskDesc) riskDesc.textContent = plan.safety_summary;

    // Metrics
    const distEl = document.getElementById('routeDistanceMetric');
    const timeEl = document.getElementById('routeTimeMetric');
    const trafficEl = document.getElementById('routeTrafficMetric');
    const tollEl = document.getElementById('routeTollMetric');

    if (distEl) distEl.textContent = `${plan.distance_km} km`;
    if (timeEl) timeEl.textContent = plan.travel_time;
    if (trafficEl) {
      trafficEl.textContent = plan.traffic_level;
      trafficEl.style.color = plan.traffic_color;
    }
    if (tollEl) {
      tollEl.textContent = plan.toll_count > 0 ? `${plan.toll_count} Plaza(s) (~₹${plan.estimated_toll_cost})` : 'Free (No Tolls)';
    }

    // Alternative Route Recommendation
    const altBox = document.getElementById('routeAltRecommendationBox');
    const altTitle = document.getElementById('routeAltTitle');
    const altDesc = document.getElementById('routeAltDesc');

    if (altBox && plan.alternative_route) {
      if (plan.alternative_route.has_alternative) {
        altBox.style.display = 'block';
        if (altTitle) altTitle.innerHTML = `<span>🛡️</span> ${plan.alternative_route.title}`;
        if (altDesc) altDesc.textContent = plan.alternative_route.details;
      } else {
        altBox.style.display = 'none';
      }
    }

    // Hazards list
    const listEl = document.getElementById('routeHazardsList');
    if (listEl) {
      if (plan.hazards.length === 0) {
        listEl.innerHTML = '<div style="color:var(--success); font-size:0.85rem; padding:8px 0;">🎉 Zero reported road hazards on this route!</div>';
      } else {
        listEl.innerHTML = plan.hazards.map(h => `
          <div class="hazard-mini-item">
            <div>
              <span class="badge badge-priority-${h.priority.toLowerCase()}" style="font-size:0.65rem;">${h.priority}</span>
              <b style="color:#fff; margin-left:6px;">${h.category}</b>
              <div style="color:var(--text-muted); font-size:0.75rem;">${h.location_name} (~${h.distance_from_route_m}m off path)</div>
            </div>
            <a href="/report/${h.id}" class="btn btn-outline-cyan btn-sm" style="font-size:0.7rem; padding:3px 8px;">View</a>
          </div>
        `).join('');
      }
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  JourneyPlanner.init();
});
