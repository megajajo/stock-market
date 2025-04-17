import { userData } from '../data/userData.js';
import { openStockDetail } from './stockDetails.js';
import { stockData } from '../data/stockData.js';
import { drawMiniChart } from './miniChart.js';
import { portfolioPerformanceData } from '../data/portfolioPerformance.js';
import { drawDetailedGraph } from './graph.js';

export function initPortfolioView() {
  // Populate the holdings grid
  const holdingsGrid = document.querySelector('.holdings-grid');
  holdingsGrid.innerHTML = '';

  userData.holdings.forEach(holding => {
    const card = document.createElement('div');
    card.classList.add('holding-card');
    card.innerHTML = `
      <h3 class="holding-stock">${holding.stock}</h3>
      <div class="mini-chart-container"></div>
      <div class="holding-amount">Amount: ${holding.amount}</div>
      <div class="holding-pnl">24h PnL: ${holding.pnl}</div>
    `;
    card.addEventListener('click', () => openStockDetail(holding.stock));
    holdingsGrid.appendChild(card);

    // Draw mini-chart
    const miniChartContainer = card.querySelector('.mini-chart-container');
    drawMiniChart(miniChartContainer, stockData[holding.stock], {
      width: 100,
      height: 40,
      yKey: 'price'
    });
  });

  // Fill in header: profile pic, name, balance & PnL
  document.getElementById('header-pic').src = userData.profilePicUrl || 'assets/profile_picture.jpg';
  document.getElementById('user-name').textContent = userData.name;

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
}