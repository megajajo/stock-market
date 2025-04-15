// js/components/portfolio.js

import { userData } from '../data/userData.js';
import { openStockDetail } from './stockDetails.js';
import { stockData } from '../data/stockData.js';
import { drawMiniChart } from './miniChart.js';
// Import the portfolio performance data, if needed by the graph module.
import { portfolioPerformanceData } from '../data/portfolioPerformance.js';
// Import the reusable graph module.
import { drawDetailedGraph } from './graph.js';

export function initPortfolioView() {
  // Update the header with user information.
  document.getElementById('user-name').textContent = userData.name;
  document.querySelector('.balance').textContent = `Balance: $${userData.balance.toFixed(2)}`;
  document.querySelector('.pnl').textContent = `24h PnL: ${userData.pnl}`;

  // Populate the holdings grid.
  const holdingsGrid = document.querySelector('.holdings-grid');
  holdingsGrid.innerHTML = ''; // Clear previous holdings

  userData.holdings.forEach(holding => {
    const card = document.createElement('div');
    card.classList.add('holding-card');
    // Create card HTML with an additional container for the mini chart.
    card.innerHTML = `
      <h3 class="holding-stock">${holding.stock}</h3>
      <div class="mini-chart-container"></div>
      <div class="holding-amount">Amount: ${holding.amount}</div>
      <div class="holding-pnl">24h PnL: ${holding.pnl}</div>
    `;
    
    // Add click event to open stock detailed info.
    card.addEventListener('click', () => {
      openStockDetail(holding.stock);
    });
    
    // Append the card to the holdings grid.
    holdingsGrid.appendChild(card);

    // Now, within the card, create and draw the mini chart.
    const miniChartContainer = card.querySelector('.mini-chart-container');
    // Create an SVG element for the mini chart.
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.classList.add('mini-chart');
    miniChartContainer.appendChild(svg);
    // Check if we have data for this stock.
    if (stockData[holding.stock]) {
      drawMiniChart(svg, stockData[holding.stock]);
    } else {
      // Optionally handle the case where no data is available.
      miniChartContainer.textContent = "No data";
    }
  });

  // Insert the portfolio performance graph.
  const performanceGraphContainer = document.createElement('div');
  performanceGraphContainer.classList.add('portfolio-graph-container');
  performanceGraphContainer.innerHTML = `<h2>Portfolio Performance</h2>`;
  
  // Insert the graph container above the holdings grid.
  const portfolioView = document.getElementById('portfolio-view');
  portfolioView.insertBefore(performanceGraphContainer, holdingsGrid);

  // --- Reusable Graph Integration ---
  // Create an SVG element to be used by the reusable graph module.
  // --- Reusable Graph Integration ---
// Pass the entire container (not an SVG!) to the graph module.
// The module will create the SVG, buttons, and handle everything.
drawDetailedGraph(performanceGraphContainer, portfolioPerformanceData, {
  height: 300,
  yKey: 'value', // or 'price' depending on your dataset
  resizeOnWindow: true
});

}
