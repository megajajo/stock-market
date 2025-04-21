// js/main.js

import { initPortfolioView } from './components/portfolio.js';
import { initSearchView }    from './components/search.js';

// Wait until the DOM is fully loaded.
document.addEventListener('DOMContentLoaded', () => {
  const navButtons = document.querySelectorAll('.nav-btn');
  const views      = document.querySelectorAll('.view');

  // Flags to ensure each view initializes only once
  let portfolioInitialized = false;
  let searchInitialized    = false;

  // ----- Initialize Default View on Load (Portfolio) -----
  if (document.getElementById('portfolio-view').classList.contains('active')) {
    initPortfolioView();
    portfolioInitialized = true;
  }

  // ----- View Switching Logic -----
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update active state on navigation buttons
      navButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Show the clicked view, hide others
      views.forEach(view => view.classList.remove('active'));
      const targetView = btn.dataset.view;
      document.getElementById(targetView).classList.add('active');

      // Lazy‑initialize views
      if (targetView === 'portfolio-view' && !portfolioInitialized) {
        initPortfolioView();
        portfolioInitialized = true;
      } else if (targetView === 'search-view' && !searchInitialized) {
        initSearchView();
        searchInitialized = true;
      }
      // settings view has no init function
    });
  });

  // ----- Dark Mode Toggle -----
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle && themeToggle.checked) {
    document.body.classList.add('dark-mode');
  }
  if (themeToggle) {
    themeToggle.addEventListener('change', () => {
      // Toggle dark mode class based on checkbox state
      document.body.classList.toggle('dark-mode', themeToggle.checked);
    });
  }

  // ----- Logout Functionality Placeholder -----
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      alert('Logging out...');
    });
  }

  // ----- Help Modal Functionality -----
const helpBtn   = document.getElementById('help-btn');
const helpModal = document.getElementById('help-modal');
const helpClose = document.getElementById('help-close');

if (helpBtn && helpModal && helpClose) {
  // Open modal
  helpBtn.addEventListener('click', () => {
    helpModal.style.display = 'flex';
  });
  // Close when × clicked
  helpClose.addEventListener('click', () => {
    helpModal.style.display = 'none';
  });
  // Close when clicking outside content
  helpModal.addEventListener('click', e => {
    if (e.target === helpModal) {
      helpModal.style.display = 'none';
    }
  });
}

});
