// js/main.js
import { userData }           from './data/userData.js';
import { initPortfolioView }  from './components/portfolio.js';
import { initSearchView }     from './components/search.js';

const GOOGLE_CLIENT_ID = '933623916878-ipovfk31uqvoidtvj5pcknkod3ggdter.apps.googleusercontent.com';

function handleCredentialResponse(response) {
  const payload = JSON.parse(atob(response.credential.split('.')[1]));
  console.log('Google user:', payload);

  // Update our central model
  userData.name           = payload.name;
  userData.profilePicUrl  = payload.picture;

  // Update the header if already rendered
  const nameEl = document.getElementById('user-name');
  if (nameEl) {
    nameEl.textContent = userData.name;
    document.getElementById('header-pic').src = userData.profilePicUrl;
  }
  // Hide the sign-in button now that we're signed in
  document.getElementById('g_id_signin').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
  // —————— Navigation + Views ——————
  const navButtons = document.querySelectorAll('.nav-btn');
  const views      = document.querySelectorAll('.view');
  let portfolioInitialized = false;
  let searchInitialized    = false;

  // Default portfolio
  if (document.getElementById('portfolio-view').classList.contains('active')) {
    initPortfolioView();
    portfolioInitialized = true;
  }

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      navButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      views.forEach(v => v.classList.remove('active'));
      const target = btn.dataset.view;
      document.getElementById(target).classList.add('active');

      if (target === 'portfolio-view' && !portfolioInitialized) {
        initPortfolioView(); portfolioInitialized = true;
      } else if (target === 'search-view' && !searchInitialized) {
        initSearchView(); searchInitialized = true;
      }
    });
  });

  // —————— Dark Mode ——————
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    document.body.classList.toggle('dark-mode', themeToggle.checked);
    themeToggle.addEventListener('change', () =>
      document.body.classList.toggle('dark-mode', themeToggle.checked)
    );
  }

  // —————— Help Modal ——————
  const helpBtn   = document.getElementById('help-btn');
  const helpModal = document.getElementById('help-modal');
  const helpClose = document.getElementById('help-close');
  if (helpBtn && helpModal && helpClose) {
    helpBtn.addEventListener('click', () => helpModal.style.display = 'flex');
    helpClose.addEventListener('click', () => helpModal.style.display = 'none');
    helpModal.addEventListener('click', e => {
      if (e.target === helpModal) helpModal.style.display = 'none';
    });
  }

  // —————— Logout Placeholder ——————
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.addEventListener('click', () => alert('Logging out...'));

  // —————— Google Sign-In ——————
  google.accounts.id.initialize({
    client_id: GOOGLE_CLIENT_ID,
    callback: handleCredentialResponse,
  });
  google.accounts.id.renderButton(
    document.getElementById('g_id_signin'),
    { theme: 'outline', size: 'large' }
  );
  // Optional: one-tap prompt
  // google.accounts.id.prompt();
});
