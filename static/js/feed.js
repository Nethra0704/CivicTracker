/**
 * CivicTrack-AI - Public Feed & Live Map Engine
 * OpenStreetMap Live Telemetry, Severity Markers, GPS Tracking & AJAX Comments
 */

const FeedController = {
  currentPriority: 'All',
  currentStatus: 'All',
  searchQuery: '',
  homeMap: null,
  mapMarkersGroup: null,

  init() {
    this.bindFilters();
    this.initHomeMap();
    this.bindLocationButton();
  },

  initHomeMap() {
    const mapEl = document.getElementById('homeLiveMap');
    if (!mapEl) return;

    // Center on Coimbatore, Tamil Nadu (11.0168, 76.9558)
    this.homeMap = MapUtils.initMap('homeLiveMap', 11.0168, 76.9558, 12);
    this.mapMarkersGroup = L.featureGroup().addTo(this.homeMap);
    this.plotMapMarkers();
  },

  bindLocationButton() {
    // "Detect My Location" Button
    const detectBtns = document.querySelectorAll('#detectLocationBtn, [data-detect-location]');
    detectBtns.forEach(btn => {
      btn.addEventListener('click', async () => {
        if (this.homeMap) {
          await MapUtils.detectAndShowUserLocation(this.homeMap, btn);
        } else {
          // Fallback if on another page without main map
          try {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting...';
            const pos = await MapUtils.getCurrentPosition();
            const addr = await MapUtils.reverseGeocode(pos.lat, pos.lon);
            showToast(`Location detected: ${addr}`, 'success');
          } catch (e) {
            showToast('Unable to detect current GPS location.', 'danger');
          } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-location-crosshairs"></i> Detect My Location';
          }
        }
      });
    });
  },

  async plotMapMarkers() {
    if (!this.homeMap) return;
    try {
      const resp = await fetch('/api/reports');
      const data = await resp.json();
      if (data.success && data.reports) {
        this.mapMarkersGroup.clearLayers();
        const bounds = [];

        data.reports.forEach(r => {
          if (!r.latitude || !r.longitude) return;

          // Severity colors: Red (High), Orange (Medium), Yellow (Low), Green (Completed/Resolved)
          const marker = MapUtils.createHazardMarker(
            r.latitude,
            r.longitude,
            r.priority,
            r.status,
            r.category
          );

          // Rich detailed popup (ID, Type, Severity, Description, Location, Status, Image)
          const popupHtml = MapUtils.buildReportPopup(r);
          marker.bindPopup(popupHtml, { maxWidth: 320 });
          this.mapMarkersGroup.addLayer(marker);
          bounds.push([r.latitude, r.longitude]);
        });

        // If there are markers near Coimbatore or overall, fit them or keep centered
        if (bounds.length > 0) {
          // Check if any report is within Coimbatore region; if so, include in view
          this.homeMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
        } else {
          this.homeMap.setView([11.0168, 76.9558], 13);
        }

        setTimeout(() => {
          if (this.homeMap) this.homeMap.invalidateSize();
        }, 250);
      }
    } catch (e) {
      console.warn('Failed to load map markers from API:', e);
    }
  },

  bindFilters() {
    // Priority chips
    document.querySelectorAll('[data-filter-priority]').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('[data-filter-priority]').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        this.currentPriority = chip.dataset.filterPriority;
        this.fetchFilteredReports();
      });
    });

    // Status chips
    document.querySelectorAll('[data-filter-status]').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('[data-filter-status]').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        this.currentStatus = chip.dataset.filterStatus;
        this.fetchFilteredReports();
      });
    });

    // Search input
    const searchInput = document.getElementById('feedSearchInput');
    if (searchInput) {
      let timeout;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          this.searchQuery = e.target.value.trim();
          this.fetchFilteredReports();
        }, 300);
      });
    }
  },

  async fetchFilteredReports() {
    const grid = document.getElementById('reportsFeedGrid');
    if (!grid) return;

    grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--text-muted);"><i class="fas fa-spinner fa-spin" style="font-size: 2rem; color:var(--accent-cyan);"></i><p style="margin-top:10px;">Scanning road issues...</p></div>';

    const params = new URLSearchParams();
    if (this.currentPriority !== 'All') params.append('priority', this.currentPriority);
    if (this.currentStatus !== 'All') params.append('status', this.currentStatus);
    if (this.searchQuery) params.append('search', this.searchQuery);

    try {
      const resp = await fetch(`/api/reports?${params.toString()}`);
      const data = await resp.json();
      if (data.success) {
        this.renderReports(data.reports);
      }
    } catch (e) {
      grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--danger);">Failed to load reports. Please try again.</div>';
    }
  },

  renderReports(reports) {
    const grid = document.getElementById('reportsFeedGrid');
    if (!grid) return;

    if (!reports || reports.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1/-1; text-align:center; padding: 50px 20px; background: var(--bg-card); border-radius: var(--radius-md); border: 1px dashed var(--border-glass);">
          <div style="font-size: 2.5rem; margin-bottom: 12px;">🛡️</div>
          <h3 style="color:#fff; margin-bottom: 6px;">No road issues found matching filters</h3>
          <p style="color:var(--text-muted); font-size:0.9rem;">Try selecting a different priority or clear the search criteria.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = reports.map(r => `
      <div class="issue-card animate-fade-in">
        <div class="issue-thumb-wrap">
          <img src="${r.image_path || '/static/uploads/pothole_crater.svg'}" alt="${r.category}" class="issue-thumb" loading="lazy">
          <div class="issue-badges-overlay">
            <span class="badge badge-priority-${r.priority.toLowerCase()}">
              <span class="badge-dot"></span> ${r.priority} Priority
            </span>
            <span class="badge badge-status-${r.status.toLowerCase().replace(/\s+/g, '')}">
              ${r.status}
            </span>
          </div>
          <div class="ai-score-pill">AI Confidence: ${r.confidence_score}%</div>
        </div>
        <div class="issue-body">
          <div class="issue-category-tag">${r.category} • Severity ${r.severity_score}/100</div>
          <h3 class="issue-location">
            <span>📍</span> ${r.location_name}
          </h3>
          <p class="issue-desc">${r.description}</p>
          <div class="issue-footer">
            <div class="issue-meta-item">
              <span>👤</span> ${r.reporter_name}
            </div>
            <div class="issue-meta-item">
              <span>💬</span> ${r.comment_count} comments
            </div>
            <a href="/report/${r.id}" class="btn btn-outline-cyan btn-sm">Inspect &rarr;</a>
          </div>
        </div>
      </div>
    `).join('');
  }
};

/**
 * Handle real-time Comment Posting on Report Detail View
 */
async function submitReportComment(reportId) {
  const input = document.getElementById('commentTextInput');
  if (!input) return;

  const text = input.value.trim();
  if (!text) {
    showToast('Please enter a comment before posting.', 'warning');
    return;
  }

  const postBtn = document.getElementById('postCommentBtn');
  if (postBtn) {
    postBtn.disabled = true;
    postBtn.innerHTML = 'Posting...';
  }

  try {
    const resp = await fetch(`/api/reports/${reportId}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ comment: text })
    });

    const data = await resp.json();
    if (resp.ok && data.success) {
      input.value = '';
      showToast('Comment posted successfully!', 'success');
      renderCommentsList(data.comments);
    } else {
      showToast(data.error || 'Failed to post comment. Ensure you are logged in.', 'danger');
    }
  } catch (e) {
    showToast('Network error while posting comment.', 'danger');
  } finally {
    if (postBtn) {
      postBtn.disabled = false;
      postBtn.innerHTML = 'Post Comment';
    }
  }
}

function renderCommentsList(comments) {
  const container = document.getElementById('commentsContainerList');
  const countBadge = document.getElementById('detailCommentsCount');
  if (countBadge) countBadge.textContent = comments.length;

  if (!container) return;

  if (comments.length === 0) {
    container.innerHTML = '<p style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:20px;">No comments yet. Be the first to share an update!</p>';
    return;
  }

  container.innerHTML = comments.map(c => `
    <div class="comment-item ${c.role === 'Authority' || c.role === 'Admin' ? 'authority-comment' : ''} animate-fade-in">
      <div class="comment-header">
        <div class="comment-author">
          <span>${c.role === 'Authority' ? '🏛️' : '👤'}</span>
          <span>${c.username}</span>
          ${c.role === 'Authority' ? '<span class="badge badge-status-inprogress" style="font-size:0.65rem;">Authority Officer</span>' : ''}
          ${c.role === 'Admin' ? '<span class="badge badge-priority-high" style="font-size:0.65rem;">System Admin</span>' : ''}
        </div>
        <div class="comment-time">${c.created_at}</div>
      </div>
      <div class="comment-body">${c.comment}</div>
    </div>
  `).join('');
}

document.addEventListener('DOMContentLoaded', () => {
  FeedController.init();
});
