// js/main.js

import { initPortfolioView } from './components/portfolio.js';
import { initSearchView } from './components/search.js';

// Wait until the DOM is fully loaded.
document.addEventListener('DOMContentLoaded', () => {
  // ----- View Switching Logic -----
  const navButtons = document.querySelectorAll('.nav-btn');
  const views = document.querySelectorAll('.view');

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update active state on navigation buttons.
      navButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Show the view corresponding to the clicked button.
      const targetView = btn.dataset.view;
      views.forEach(view => {
        view.classList.remove('active'); // Hide all views
      });
      document.getElementById(targetView).classList.add('active');
    });
  });

  // ----- Dark Mode Toggle -----
  const themeToggle = document.getElementById('theme-toggle');

// Set dark mode on load if checkbox is checked
if (themeToggle && themeToggle.checked) {
  document.body.classList.add('dark-mode');
}

if (themeToggle) {
  themeToggle.addEventListener('change', function () {
    if (this.checked) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  });
}

  // ----- Logout Functionality Placeholder -----
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      alert('Logging out...');
    });
  }

  // ----- Initialize the Views -----
  initPortfolioView();
  initSearchView(); // Initialize the search view so the stocks grid is populated.
});
