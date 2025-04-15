// js/components/search.js
import { stockData } from '../data/stockData.js';
import { openStockDetail } from './stockDetails.js';

export function initSearchView() {
  const stocksGrid = document.querySelector('.stocks-grid');
  stocksGrid.innerHTML = ''; // Clear previous content

  for (const stockName in stockData) {
    if (stockData.hasOwnProperty(stockName)) {
      const dataPoints = stockData[stockName];
      const latestPoint = dataPoints[dataPoints.length - 1];
      const latestPrice = latestPoint.price;

      const card = document.createElement('div');
      card.classList.add('stock-card');
      card.innerHTML = `
        <h3 class="stock-name">${stockName}</h3>
        <div class="stock-price">Price: $${latestPrice}</div>
      `;

      card.addEventListener('click', () => {
        openStockDetail(stockName);
      });

      stocksGrid.appendChild(card);
    }
  }
}
