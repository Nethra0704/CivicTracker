/**
 * CivicTrack-AI - Report Issue Controller
 * Manages media uploads, sample hazards picker, interactive GPS/map pin drop,
 * coordinate-to-address reverse geocoding, and real-time AI severity preview.
 */

const ReportController = {
  pickerMap: null,
  activeMarker: null,
  selectedSampleImage: 'pothole_crater.svg',

  init() {
    this.initMapPicker();
    this.bindDropzone();
    this.bindSamplePicker();
    this.bindGeoActions();
    this.bindAIPreview();
  },

  initMapPicker() {
    const mapEl = document.getElementById('reportPickerMap');
    if (!mapEl) return;

    // Default to Coimbatore, Tamil Nadu (11.0168, 76.9558)
    this.pickerMap = MapUtils.initMap('reportPickerMap', 11.0168, 76.9558, 13);

    // Initial pin in Coimbatore
    this.setPin(11.0168, 76.9558, "Avinashi Road, Coimbatore, Tamil Nadu");

    // Click on map to drop / move pin
    this.pickerMap.on('click', async (e) => {
      const { lat, lng } = e.latlng;
      this.setPin(lat, lng, 'Resolving address...');
      const address = await MapUtils.reverseGeocode(lat, lng);
      this.updateAddressFields(lat, lng, address);
    });

    setTimeout(() => {
      if (this.pickerMap) this.pickerMap.invalidateSize();
    }, 250);
  },

  setPin(lat, lon, title = '') {
    if (!this.pickerMap) return;

    if (this.activeMarker) {
      this.pickerMap.removeLayer(this.activeMarker);
    }

    this.activeMarker = MapUtils.createHazardMarker(lat, lon, 'High', 'Pending', 'Pothole');
    this.activeMarker.addTo(this.pickerMap);
    this.pickerMap.panTo([lat, lon]);

    if (title) {
      this.activeMarker.bindPopup(`<b>Selected Hazard Location</b><br>${title}`).openPopup();
    }
  },

  updateAddressFields(lat, lon, address) {
    const latInput = document.getElementById('reportLat');
    const lonInput = document.getElementById('reportLon');
    const locNameInput = document.getElementById('reportLocationName');
    const readableBadge = document.getElementById('readableLocationBadge');

    if (latInput) latInput.value = lat.toFixed(6);
    if (lonInput) lonInput.value = lon.toFixed(6);
    if (locNameInput) locNameInput.value = address;
    if (readableBadge) {
      readableBadge.innerHTML = `<span>📍</span> <b>Resolved:</b> ${address}`;
      readableBadge.style.display = 'inline-flex';
    }
  },

  bindDropzone() {
    const dropzone = document.getElementById('mediaDropzone');
    const fileInput = document.getElementById('mediaFileInput');
    const previewImg = document.getElementById('mediaPreviewImg');

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        fileInput.files = e.dataTransfer.files;
        this.handleFileSelected(fileInput.files[0], previewImg);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files[0]) {
        this.handleFileSelected(fileInput.files[0], previewImg);
      }
    });
  },

  handleFileSelected(file, previewImg) {
    if (!file) return;

    // Deselect sample buttons
    document.querySelectorAll('.sample-img-card').forEach(c => c.classList.remove('selected'));
    const sampleInput = document.getElementById('sampleImageChoice');
    if (sampleInput) sampleInput.value = '';

    const reader = new FileReader();
    reader.onload = (e) => {
      if (previewImg) {
        previewImg.src = e.target.result;
        previewImg.style.display = 'block';
      }
      this.triggerAIPreview();
    };
    reader.readAsDataURL(file);
  },

  bindSamplePicker() {
    const sampleCards = document.querySelectorAll('.sample-img-card');
    const sampleInput = document.getElementById('sampleImageChoice');
    const previewImg = document.getElementById('mediaPreviewImg');
    const fileInput = document.getElementById('mediaFileInput');

    sampleCards.forEach(card => {
      card.addEventListener('click', () => {
        sampleCards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        
        const filename = card.dataset.sampleFile;
        this.selectedSampleImage = filename;
        if (sampleInput) sampleInput.value = filename;
        if (fileInput) fileInput.value = ''; // clear file upload
        
        if (previewImg) {
          previewImg.src = `/static/uploads/${filename}`;
          previewImg.style.display = 'block';
        }

        // Auto-select category matching sample
        const categorySelect = document.getElementById('reportCategory');
        if (categorySelect && card.dataset.category) {
          categorySelect.value = card.dataset.category;
        }

        this.triggerAIPreview();
      });
    });
  },

  bindGeoActions() {
    // 1. Current GPS Location Button ("Detect My Location")
    const gpsBtns = document.querySelectorAll('#useCurrentGpsBtn, #detectLocationBtn, [data-detect-location]');
    gpsBtns.forEach(gpsBtn => {
      gpsBtn.addEventListener('click', async () => {
        gpsBtn.disabled = true;
        gpsBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting Location...';
        try {
          const pos = await MapUtils.getCurrentPosition();
          this.setPin(pos.lat, pos.lon, 'Your Current Location');
          const address = await MapUtils.reverseGeocode(pos.lat, pos.lon);
          this.updateAddressFields(pos.lat, pos.lon, address);
          showToast('GPS position accurately detected!', 'success');
        } catch (err) {
          let msg = 'Could not fetch GPS. Ensure location access is permitted in your browser.';
          if (err && err.code === 1) msg = 'Location access denied by user. Please allow permission.';
          showToast(msg, 'danger');
        } finally {
          gpsBtn.disabled = false;
          gpsBtn.innerHTML = '<i class="fas fa-location-crosshairs"></i> Detect My Location';
        }
      });
    });

    // 2. Search Address By Name
    const searchBtn = document.getElementById('searchAddressBtn');
    const searchInput = document.getElementById('searchAddressInput');
    if (searchBtn && searchInput) {
      const doSearch = async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        searchBtn.disabled = true;
        searchBtn.innerHTML = 'Searching...';
        const result = await MapUtils.geocode(query);
        if (result) {
          this.setPin(result.lat, result.lon, result.display_name);
          this.updateAddressFields(result.lat, result.lon, result.display_name);
          showToast(`Found: ${result.display_name.substring(0, 45)}...`, 'success');
        } else {
          showToast('Location not found. Try entering landmark or city.', 'warning');
        }
        searchBtn.disabled = false;
        searchBtn.innerHTML = 'Find';
      };

      searchBtn.addEventListener('click', doSearch);
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          doSearch();
        }
      });
    }
  },

  bindAIPreview() {
    const descInput = document.getElementById('reportDescription');
    const categorySelect = document.getElementById('reportCategory');

    let debounce;
    const trigger = () => {
      clearTimeout(debounce);
      debounce = setTimeout(() => this.triggerAIPreview(), 400);
    };

    if (descInput) descInput.addEventListener('input', trigger);
    if (categorySelect) categorySelect.addEventListener('change', trigger);
  },

  async triggerAIPreview() {
    const descInput = document.getElementById('reportDescription');
    const categorySelect = document.getElementById('reportCategory');
    const previewContainer = document.getElementById('aiPreviewContainer');
    if (!previewContainer) return;

    const desc = descInput ? descInput.value : '';
    const category = categorySelect ? categorySelect.value : 'Pothole';
    const sample = this.selectedSampleImage;

    try {
      const resp = await fetch('/api/ai/analyze-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: desc,
          category: category,
          sample_image: sample
        })
      });

      const data = await resp.json();
      if (data.success && data.analysis) {
        const a = data.analysis;
        previewContainer.style.display = 'block';

        const priorityBadge = document.getElementById('aiPreviewPriorityBadge');
        const scoreSpan = document.getElementById('aiPreviewScore');
        const confidenceSpan = document.getElementById('aiPreviewConfidence');
        const fillBar = document.getElementById('aiPreviewConfidenceFill');
        const hazardsList = document.getElementById('aiPreviewHazardsList');
        const actionSpan = document.getElementById('aiPreviewAction');

        if (priorityBadge) {
          priorityBadge.className = `badge badge-priority-${a.priority.toLowerCase()}`;
          priorityBadge.innerHTML = `<span class="badge-dot"></span> AI: ${a.priority} Priority`;
        }
        if (scoreSpan) scoreSpan.textContent = `${a.severity_score}/100`;
        if (confidenceSpan) confidenceSpan.textContent = `${a.confidence_score}%`;
        if (fillBar) fillBar.style.width = `${a.confidence_score}%`;
        if (actionSpan) actionSpan.textContent = a.recommended_action;

        if (hazardsList) {
          hazardsList.innerHTML = a.detected_hazards.map(h => `<li>${h}</li>`).join('');
        }
      }
    } catch (e) {
      console.warn('AI preview error:', e);
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  ReportController.init();
});
