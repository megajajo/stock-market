// js/components/search.js

import { drawMiniChart } from './miniChart.js';
import { stockData }       from '../data/stockData.js';
import { openStockDetail } from './stockDetails.js';


export function initSearchView() {
  const stocksGrid = document.querySelector('.stocks-grid');
  stocksGrid.innerHTML = '';

  for (const stockName in stockData) {
    if (!stockData.hasOwnProperty(stockName)) continue;
    const dataPoints = stockData[stockName];
    const latestPrice = dataPoints[dataPoints.length-1].price;

    const card = document.createElement('div');
    card.classList.add('stock-card');
    card.innerHTML = `
      <h3 class="stock-name">${stockName}</h3>
      <div class="stock-price">Price: $${latestPrice}</div>
      <div class="mini-chart-container"></div>
    `;
    card.addEventListener('click', () => openStockDetail(stockName));
    stocksGrid.appendChild(card);

    // **Draw the mini chart** inside that container div:
    const chartContainer = card.querySelector('.mini-chart-container');
    drawMiniChart(chartContainer, dataPoints, {
      width: 100,
      height: 40,
      yKey: 'price'
    });
  }
}
