// js/main.js
import { userData }           from './data/userData.js';
import { initPortfolioView }  from './components/portfolio.js';
import { initSearchView }     from './components/search.js';
import { populatePortfolio } from './components/portfolio.js';

const GOOGLE_CLIENT_ID = '933623916878-ipovfk31uqvoidtvj5pcknkod3ggdter.apps.googleusercontent.com';
export var loggedIn = false;

function handleCredentialResponse(response) {
  const payload = JSON.parse(atob(response.credential.split('.')[1]));
  console.log('Google user:', payload);

  // Update our central model
  userData.name           = payload.name;
  userData.profilePicUrl  = payload.picture;
  userData.email          = payload.email;  // store email for sign-out

  // Check if a client  with this email address already exists
  // If it does not exist, create it
  addClient()

  // Update loggedIn variable
  loggedIn = true;

  // Connect the WebSocket with the updated email
  connectClientSocket(userData.email);

  // // Update the header if already rendered
  // const nameEl = document.getElementById('user-name');
  // if (nameEl) {
  //   nameEl.textContent = userData.name;
  //   document.getElementById('header-pic').src = userData.profilePicUrl;
  // }

  // Toggle buttons: hide sign-in, show sign-out
  document.getElementById('g_id_signin').style.display    = 'none';
  document.getElementById('google-signout').style.display = 'block';
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
        initSearchView();    searchInitialized = true;
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

  // —————— Google Sign-In ——————
  google.accounts.id.initialize({
    client_id: GOOGLE_CLIENT_ID,
    callback: handleCredentialResponse,
  });
  google.accounts.id.renderButton(
    document.getElementById('g_id_signin'),
    { theme: 'outline', size: 'large' }
  );

  // —————— Google Sign-Out ——————
  const signOutBtn = document.getElementById('google-signout');
  signOutBtn.style.display = 'none';  // ensure hidden initially
  signOutBtn.addEventListener('click', () => {
    // disable auto-select on next load
    google.accounts.id.disableAutoSelect();

    // revoke current session
    google.accounts.id.revoke(userData.email, () => {
      // clear our user model
      userData.name           = '';
      userData.profilePicUrl  = '';
      userData.email          = '';

      // reset UI to defaults
      document.getElementById('user-name').textContent = 'Your Name';
      document.getElementById('header-pic').src       = 'assets/logo.jpg';

      // toggle buttons
      signOutBtn.style.display                    = 'none';
      document.getElementById('g_id_signin').style.display = 'block';

      // update loggedIn variable
      loggedIn = false;
    });
  });

  // Optional: one-tap prompt
  // google.accounts.id.prompt();
});

// —————— addClient function used when signing in ——————
function addClient(){
  const client_data = {
    email: userData.email,
    first_name: userData.name,
    last_name: userData.name
  }

  // API call to add client
  fetch('/api/add_new_client', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(client_data) // Convert the data to JSON format
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log("Server Response Client Object:", data);
    userData.username = data.username;
    alert("Client has been found!");
  })
  .catch(error => {
    console.error("Error:", error);
    alert("Failed to find the client. Please try again.");
  });
}



// —————— WebSocket used to update the client data and the portfolio webpage ——————
// Add WebSocket listeners to get data about the order book


let client_socket; // Declare the WebSocket variable globally

function connectClientSocket(email) {
    // Close the existing WebSocket connection if it exists
    if (client_socket) {
        console.log("Closing existing WebSocket connection...");
        client_socket.close();
    }

    // Create a new WebSocket connection
    client_socket = new WebSocket("ws://localhost:8000/client_info");

    // Handle connection open
    client_socket.addEventListener("open", () => {
        console.log(`Connected to Client Info for client with email: ${email}`);
        // Send the updated email to subscribe to client info
        client_socket.send(email);
    });

    // Handle incoming messages
    client_socket.addEventListener("message", (event) => {
        const data = JSON.parse(event.data);
        console.log(`Client ${email} update:`, data);

        // Update userData with balance
        userData.balance = data.balance;

        // Transform portfolio data into holdings array
        userData.holdings = Object.entries(data.portfolio).map(([stock, amount]) => {
            return {
                stock: stock,       // Stock ticker
                amount: amount,     // Number of shares
                pnl: "N/A"          // Placeholder for PnL (if not provided by the server)
            };
        });

        console.log("Transformed holdings:", userData.holdings);

        // Update the portfolio view
        populatePortfolio();
    });

    // Handle connection close
    client_socket.addEventListener("close", () => {
        console.log("Client Info WebSocket connection closed");
    });

    // Handle errors
    client_socket.addEventListener("error", (error) => {
        console.error("Client Info WebSocket error:", error);
    });
}
