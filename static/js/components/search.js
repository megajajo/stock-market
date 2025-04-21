// js/components/search.js
import { drawMiniChart } from './miniChart.js';
import { stockData }       from '../data/stockData.js';
import { openStockDetail } from './stockDetails.js';

export function initSearchView() {
  const stocksGrid = document.querySelector('.stocks-grid');
  const searchInput = document.getElementById('stock-search-input');

  // Render initial full list
  renderStocks('');

  // When the user types, re-render matching stocks
  searchInput.addEventListener('input', () => {
    const query = searchInput.value.trim().toLowerCase();
    renderStocks(query);
  });

  function renderStocks(filter) {
    stocksGrid.innerHTML = '';

    // Get all stock names, filter by substring, case‑neutral
    const names = Object.keys(stockData)
      .filter(name => name.toLowerCase().includes(filter));

    if (names.length === 0) {
      stocksGrid.innerHTML = `<div class="no-results">No stocks match “${filter}”</div>`;
      return;
    }

    for (const stockName of names) {
      const dataPoints = stockData[stockName];
      const latestPrice = dataPoints[dataPoints.length - 1].price;

      const card = document.createElement('div');
      card.classList.add('stock-card');
      card.innerHTML = `
        <h3 class="stock-name">${stockName}</h3>
        <div class="stock-price">Price: $${latestPrice}</div>
        <div class="mini-chart-container"></div>
      `;
      card.addEventListener('click', () => openStockDetail(stockName));
      stocksGrid.appendChild(card);

      // Draw the mini chart
      const chartContainer = card.querySelector('.mini-chart-container');
      drawMiniChart(chartContainer, dataPoints, {
        width: 100,
        height: 40,
        yKey: 'price'
      });
    }
  }
}
