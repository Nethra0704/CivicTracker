/**
 * CivicTrack-AI - Global Frontend Controller
 * Handles alerts, mobile navigation, modals, and demo credential helpers.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Auto-dismiss flash toasts after 5 seconds
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(t => {
    setTimeout(() => {
      t.style.opacity = '0';
      t.style.transform = 'translateX(100%)';
      t.style.transition = 'all 0.4s ease';
      setTimeout(() => t.remove(), 400);
    }, 5000);
  });

  // 2. Mobile nav toggle
  const mobileToggle = document.querySelector('.mobile-nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('mobile-open');
    });
  }

  // 3. Modal close bindings
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-backdrop');
      if (modal) modal.classList.remove('open');
    });
  });

  // Close modal when clicking on backdrop
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('open');
      }
    });
  });
});

/**
 * Global Toast Trigger Helper
 */
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 4500);
}

/**
 * Demo Login Auto-fill Helper for Quick Testing
 */
function fillDemoCredentials(username, password) {
  const userInput = document.getElementById('loginUsername');
  const passInput = document.getElementById('loginPassword');
  if (userInput && passInput) {
    userInput.value = username;
    passInput.value = password;
    showToast(`Autofilled demo credentials for: ${username}`, 'info');
  }
}
