// js/components/stockDetails.js

import { stockData } from '../data/stockData.js';
import { drawDetailedGraph } from './graph.js';
import { populateOrderBook } from './orderBook.js';
import { userData }           from '../data/userData.js';

// Function to open the detailed view modal for a given stock.
export function openStockDetail(stockName) {
  // Create the modal container.
  const modal = document.createElement('div');
  modal.classList.add('modal');

  // Set the inner HTML for the modal.
  modal.innerHTML = `
    <div class="modal-content">
      <span class="close-button">&times;</span>
      <h2>${stockName} Details</h2>
      <div class="modal-body">
        <!-- Graph Section -->
        <div class="graph-container">
          <svg class="detailed-chart"></svg>
        </div>
        <!-- Order Form Section -->
        <div class="order-form-section">
          <h3>Place Order</h3>
          <form id="order-form">

            <input type="number" id="order-amount" placeholder="Amount" required />
            <!-- Order Type Toggle (Radio Buttons) -->
            <div class="order-type-toggle">
              <label>
                <input type="radio" name="order-type" value="market" checked> Market
              </label>
              <label>
                <input type="radio" name="order-type" value="limit_buy"> Limit Buy
              </label>
              <label>
                <input type="radio" name="order-type" value="limit_sell"> Limit Sell
              </label>
            </div>
            <!-- Limit Price Field: visible only for limit orders -->
            <input type="number" id="order-limit-price" placeholder="Limit Price" style="display: none;" required />
            <button type="button" id="place-order-btn">Place Order</button>
          </form>
        </div>
        <!-- Order Book Toggle & Section -->
        <button id="toggle-order-book-btn">Show Order Book</button>
        <div class="order-book-section" style="display:none;">
          <div id="order-book-container"></div>
        </div>
      </div>
    </div>
  `;

  // Append the modal to the body.
  document.body.appendChild(modal);

  // Close modal when clicking the close button.
  const closeButton = modal.querySelector('.close-button');
  closeButton.addEventListener('click', () => {
    document.body.removeChild(modal);
  });

  // Optional: close modal if clicking outside the modal content.
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      document.body.removeChild(modal);
    }
  });

  // Draw the detailed graph using the modular graph component.
  const graphContainer = modal.querySelector('.graph-container');
graphContainer.innerHTML = ''; // Clear the placeholder SVG if present
// Wait for the modal to fully render before drawing the graph.
setTimeout(() => {
  drawDetailedGraph(graphContainer, stockData[stockName], {
    height: 200,
    yKey: 'price',
    resizeOnWindow: false,
    margin: { top: 20, right: 20, bottom: 40, left: 35 } // <-- reduce left from default 50
  });

}, 0);


  // Set up the order type toggle: show/hide the limit price input.
  const orderTypeInputs = modal.querySelectorAll('input[name="order-type"]');
  const orderLimitPriceInput = modal.querySelector('#order-limit-price');
  orderTypeInputs.forEach(input => {
    input.addEventListener('change', () => {
      if (input.value === 'limit_buy' || input.value === 'limit_sell') {
        orderLimitPriceInput.style.display = 'block';
      } else {
        orderLimitPriceInput.style.display = 'none';
      }
    });
  });

  // Handle order placement when the "Place Order" button is clicked.
  modal.querySelector('#place-order-btn').addEventListener('click', () => {
    // Get the selected order type.
    const selectedOrderType = modal.querySelector('input[name="order-type"]:checked').value;
    handleOrder(stockName, selectedOrderType, modal);
  });

  // Set up the order book toggle.
  const toggleOrderBookBtn = modal.querySelector('#toggle-order-book-btn');
  const orderBookSection = modal.querySelector('.order-book-section');
  toggleOrderBookBtn.addEventListener('click', () => {
    if (orderBookSection.style.display === 'none') {
      orderBookSection.style.display = 'block';
      toggleOrderBookBtn.textContent = 'Hide Order Book';
      // Populate the order book using the modular order book component.
      const orderBookContainer = modal.querySelector('#order-book-container');
      populateOrderBook(stockName, orderBookContainer);
    } else {
      orderBookSection.style.display = 'none';
      toggleOrderBookBtn.textContent = 'Show Order Book';
    }
  });
}

// Function to handle order submission.
function handleOrder(stock, orderType, modal) {
  const username = userData.name;
  const amountVal = modal.querySelector('#order-amount').value.trim();
  const limitPriceVal = modal.querySelector('#order-limit-price').value.trim();


  if (!amountVal || Number(amountVal) <= 0) {
    alert("Amount must be greater than 0!");
    return;
  }
  if ((orderType === 'limit_buy' || orderType === 'limit_sell') && (!limitPriceVal || Number(limitPriceVal) <= 0)) {
    alert("Please enter a valid limit price!");
    return;
  }

  const tradeData = {
    stock,
    type: orderType,
    username,
    amount: Number(amountVal),
    limitPrice: orderType === 'market' ? null : Number(limitPriceVal),
    timestamp: new Date().toISOString()
  };

  console.log("Sending trade data:", tradeData);

  // Example API call (replace the URL with your endpoint).
  fetch('https://example.com/api/trade', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tradeData)
  })
  .then(response => response.json())
  .then(data => {
    alert("Order placed successfully!");
    console.log("Server response:", data);
  })
  .catch(error => {
    alert("Error placing order!");
    console.error("Order error:", error);
  });
}
