import { userData } from '../data/userData.js';
import { openStockDetail } from './stockDetails.js';
import { stockDataPrices } from '../data/stockData.js';
import { drawMiniChart } from './miniChart.js';
import { portfolioPerformanceData } from '../data/portfolioPerformance.js';
import { drawDetailedGraph } from './graph.js';
import { loggedIn } from '../main.js';


/**
 * Clears out and re-renders the .holdings-grid
 * @param {HTMLElement} container  the <div class="holdings-grid">
 * @param {Array} holdings         userData.holdings
 */
function populatePositions(container, holdings) {
  container.innerHTML = '';


// --- CASH CARD ---
const cashCard = document.createElement('div');
cashCard.classList.add('holding-card');
cashCard.innerHTML = `
  <h3 class="holding-stock">Cash</h3>
  <div class="holding-amount">Amount: $${userData.balance.toFixed(2)}</div>
`;
cashCard.addEventListener('click', () => {
  // you could open a cash-detail modal here if you want
});
container.appendChild(cashCard);
// ------------------

  holdings.forEach(holding => {
    const card = document.createElement('div');
    card.classList.add('holding-card');
    card.innerHTML = `
      <h3 class="holding-stock">${holding.stock}</h3>
      <div class="mini-chart-container"></div>
      <div class="holding-amount">Amount: ${holding.amount}</div>
      <div class="holding-pnl">24h PnL: ${holding.pnl}</div>
    `;
    card.addEventListener('click', () => openStockDetail(holding.stock));
    container.appendChild(card);

    // draw the sparkline
    const miniChartContainer = card.querySelector('.mini-chart-container');
    console.log("data for drawing minichart:", stockDataPrices[holding.stock], holding.stock, stockDataPrices);
    drawMiniChart(miniChartContainer, stockDataPrices[holding.stock], {
      width: 100,
      height: 40,
      yKey: 'price'
    });
  });
}

export function initPortfolioView() {
  // Fill in header: profile pic, name, balance & PnL
  const img = document.getElementById('header-pic');
img.src = userData.profilePicUrl || 'assets/logo.jpg';
img.onerror = () => {
  img.src = 'assets/logo.jpg';
};
  // set dynamic title
const titleEl = document.getElementById('portfolio-title');
if (loggedIn) {
  titleEl.textContent = `${userData.name}'s portfolio value:`;
} else {
  titleEl.textContent = 'Your portfolio value:';
}

  
  const pnlValue = userData.pnl;
  const isPositive = pnlValue.startsWith('+');
  document.getElementById('balance-header').textContent = `$${userData.balance.toFixed(2)}`;
  const pnlEl = document.getElementById('pnl-header');
  pnlEl.textContent = pnlValue;
  pnlEl.classList.add(isPositive ? 'positive' : 'negative');

  // Draw the main portfolio graph inside header
  const graphDiv = document.getElementById('header-graph');
  drawDetailedGraph(graphDiv, portfolioPerformanceData, {
    height: 200,
    yKey: 'value',
    resizeOnWindow: true
  });

  // Insert 'Your Positions' title between graph and holdings grid
  const holdingsGrid = document.querySelector('.holdings-grid');
  const positionsTitle = document.createElement('h2');
  positionsTitle.textContent = 'Your Positions';
  positionsTitle.classList.add('positions-title');
  holdingsGrid.parentNode.insertBefore(positionsTitle, holdingsGrid);

 // Populate via helper
 populatePositions(holdingsGrid, userData.holdings);
}

export function populatePortfolio() {
  // Update header numbers
  const pnlValue = userData.pnl;
  const isPositive = pnlValue.startsWith('+');
  document.getElementById('balance-header').textContent = `$${userData.balance.toFixed(2)}`;
  const pnlEl = document.getElementById('pnl-header');
  pnlEl.textContent = pnlValue;
  pnlEl.classList.add(isPositive ? 'positive' : 'negative');

  // Re-populate positions only (graph was initialized once in initPortfolioView)
  const holdingsGrid = document.querySelector('.holdings-grid');
  const positionsTitle = document.querySelector('.positions-title');
  holdingsGrid.parentNode.insertBefore(positionsTitle, holdingsGrid);


    // Populate the holdings grid
    console.log(userData.holdings);
    populatePositions(holdingsGrid, userData.holdings);
}

