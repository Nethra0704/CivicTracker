/**
 * CivicTrack-AI - Authority Control Dashboard Controller
 * Status progression management, notes logging, and district filtering.
 */

const AuthorityController = {
  currentReportId: null,

  init() {
    this.bindUpdateButtons();
  },

  bindUpdateButtons() {
    // Open Status Update Modal
    document.querySelectorAll('[data-open-status-modal]').forEach(btn => {
      btn.addEventListener('click', () => {
        const reportId = btn.dataset.reportId;
        const currentStatus = btn.dataset.currentStatus;
        const locationName = btn.dataset.locationName;

        this.openStatusModal(reportId, currentStatus, locationName);
      });
    });

    // Save Status Update Form
    const saveBtn = document.getElementById('saveStatusUpdateBtn');
    if (saveBtn) {
      saveBtn.addEventListener('click', () => this.submitStatusUpdate());
    }
  },

  openStatusModal(reportId, currentStatus, locationName) {
    this.currentReportId = reportId;

    const modal = document.getElementById('authorityUpdateModal');
    const locSpan = document.getElementById('modalReportLocation');
    const statusSelect = document.getElementById('modalStatusSelect');
    const notesInput = document.getElementById('modalResponseNotes');

    if (locSpan) locSpan.textContent = locationName;
    if (statusSelect) statusSelect.value = currentStatus;
    if (notesInput) notesInput.value = '';

    if (modal) modal.classList.add('open');
  },

  async submitStatusUpdate() {
    if (!this.currentReportId) return;

    const statusSelect = document.getElementById('modalStatusSelect');
    const notesInput = document.getElementById('modalResponseNotes');
    const saveBtn = document.getElementById('saveStatusUpdateBtn');

    const newStatus = statusSelect ? statusSelect.value : 'In Progress';
    const notes = notesInput ? notesInput.value.trim() : '';

    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.innerHTML = 'Updating...';
    }

    try {
      const resp = await fetch(`/api/reports/${this.currentReportId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          notes: notes
        })
      });

      const data = await resp.json();
      if (resp.ok && data.success) {
        showToast(`Report #${this.currentReportId} status successfully set to: ${newStatus}`, 'success');
        
        // Update DOM status badge in row
        const rowBadge = document.getElementById(`statusBadge_${this.currentReportId}`);
        if (rowBadge) {
          rowBadge.className = `badge badge-status-${newStatus.toLowerCase().replace(/\s+/g, '')}`;
          rowBadge.textContent = newStatus;
        }

        const modal = document.getElementById('authorityUpdateModal');
        if (modal) modal.classList.remove('open');

        // Optional short delay reload for refreshed metrics
        setTimeout(() => window.location.reload(), 1000);
      } else {
        showToast(data.error || 'Failed to update status', 'danger');
      }
    } catch (e) {
      showToast('Network error while saving authority update.', 'danger');
    } finally {
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = 'Commit Status Update';
      }
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  AuthorityController.init();
});
