import { userData } from '../data/userData.js';
import { openStockDetail } from './stockDetails.js';
import { stockDataPrices } from '../data/stockData.js';
import { drawMiniChart } from './miniChart.js';
import { portfolioPerformanceData } from '../data/portfolioPerformance.js';
import { drawDetailedGraph } from './graph.js';
import { loggedIn } from '../main.js';

// ────────────────────────────────────────────────────────────
// Keep a handle to the live header graph so we can update it
// ────────────────────────────────────────────────────────────
let headerGraph; // will be set once in initPortfolioView()

/**
 * Clears out and re-renders the .holdings-grid
 * @param {HTMLElement} container  the <div class="holdings-grid">
 * @param {Array} holdings         userData.holdings
 */
function populatePositions(container, holdings) {
  // Clear existing cards
  container.innerHTML = '';

  // ── CASH CARD ─────────────────────────────────────────────
  const cashCard = document.createElement('div');
  cashCard.classList.add('holding-card');
  cashCard.innerHTML = `
    <h3 class="holding-stock">Cash</h3>
    <div class="holding-amount">Amount: $${userData.balance.toFixed(2)}</div>
  `;
  cashCard.addEventListener('click', () => {
    /* could open a cash‑detail modal */
  });
  container.appendChild(cashCard);
  // ───────────────────────────────────────────────────────────

  // One card per equity/crypto holding
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
    drawMiniChart(miniChartContainer, stockDataPrices[holding.stock], {
      width: 100,
      height: 40,
      yKey: 'price'
    });
  });
}

export function initPortfolioView() {
  // ── HEADER (profile, name, balance, PnL) ──────────────────
  const img = document.getElementById('header-pic');
  img.src = userData.profilePicUrl || 'assets/logo.jpg';
  img.onerror = () => { img.src = 'assets/logo.jpg'; };

  const titleEl = document.getElementById('portfolio-title');
  titleEl.textContent = loggedIn ? `${userData.name}'s portfolio value:` : 'Your portfolio value:';

  const pnlValue = userData.pnl;
  const isPositive = pnlValue.startsWith('+');
  document.getElementById('balance-header').textContent = `$${userData.portfolioValue.toFixed(2)}`;
  const pnlEl = document.getElementById('pnl-header');
  pnlEl.textContent = pnlValue;
  pnlEl.classList.remove('positive', 'negative');
  pnlEl.classList.add(isPositive ? 'positive' : 'negative');

  // ── MAIN HEADER GRAPH (built once) ────────────────────────
  const graphDiv = document.getElementById('header-graph');
  headerGraph = drawDetailedGraph(graphDiv, portfolioPerformanceData, {
    height: 200,
    yKey: 'value',
    resizeOnWindow: true
  });

  // ── Insert “Your Positions” heading ──────────────────────
  const holdingsGrid = document.querySelector('.holdings-grid');
  const positionsTitle = document.createElement('h2');
  positionsTitle.textContent = 'Your Positions';
  positionsTitle.classList.add('positions-title');
  holdingsGrid.parentNode.insertBefore(positionsTitle, holdingsGrid);

  // ── Initial cards render ─────────────────────────────────
  populatePositions(holdingsGrid, userData.holdings);
}

// Called every time fresh data arrives over the socket
export function populatePortfolio() {
  // Update header numbers
  const pnlValue = userData.pnl;
  const isPositive = pnlValue.startsWith('+');
  document.getElementById('balance-header').textContent = `$${userData.portfolioValue.toFixed(2)}`;
  const pnlEl = document.getElementById('pnl-header');
  pnlEl.textContent = pnlValue;
  pnlEl.classList.remove('positive', 'negative');
  pnlEl.classList.add(isPositive ? 'positive' : 'negative');

  // Push new points into the existing graph (no DOM rebuild)
  if (headerGraph) headerGraph.update(portfolioPerformanceData);

  // Re-render positions grid
  const holdingsGrid = document.querySelector('.holdings-grid');
  const positionsTitle = document.querySelector('.positions-title');
  holdingsGrid.parentNode.insertBefore(positionsTitle, holdingsGrid);
  populatePositions(holdingsGrid, userData.holdings);
}
