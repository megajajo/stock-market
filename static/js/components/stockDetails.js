// js/components/stockDetails.js

import { stockDataPrices } from '../data/stockData.js';       // historic price data
import { drawDetailedGraph } from './graph.js';              // to draw the stock chart
import { populateOrderBook } from './orderBook.js';          // to render order book
import { loggedIn } from '../main.js';                       // login flag
import { userData } from '../data/userData.js';              // current user info

// Opens a modal showing detailed info & order form for a given stock
export function openStockDetail(stockName) {
  // Create the modal container
  const modal = document.createElement('div');
  modal.classList.add('modal');
  modal.innerHTML = `
    <div class="modal-content">
      <span class="close-button">&times;</span>
      <h2>${stockName} Details</h2>
      <div class="modal-body">
        <!-- Graph -->
        <div class="graph-container"></div>

        <!-- Order Form -->
        <div class="order-form-section">
          <h3>Place Order</h3>
          <form id="order-form">
            <input type="number" id="order-amount" placeholder="Amount" required />

            <div class="order-type-toggle">
              <label>
                <input type="radio" name="order-type" value="market_buy" checked>
                Market Buy
              </label>
              <label>
                <input type="radio" name="order-type" value="market_sell">
                Market Sell
              </label>
              <label>
                <input type="radio" name="order-type" value="limit_buy">
                Limit Buy
              </label>
              <label>
                <input type="radio" name="order-type" value="limit_sell">
                Limit Sell
              </label>
            </div>

            <input
              type="number"
              id="order-limit-price"
              placeholder="Limit Price"
              style="display: none;"
              required
            />

            <button type="button" id="place-order-btn">Place Order</button>
          </form>
        </div>

        <!-- Order Book -->
        <button id="toggle-order-book-btn">Show Order Book</button>
        <div class="order-book-section" style="display: none;">
          <div id="order-book-container"></div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Close handlers
  modal.querySelector('.close-button').addEventListener('click', () => {
    document.body.removeChild(modal);
  });
  modal.addEventListener('click', e => {
    if (e.target === modal)
      document.body.removeChild(modal);
  });

  // Draw the chart once modal is in DOM
  const graphContainer = modal.querySelector('.graph-container');
  setTimeout(() => {
    drawDetailedGraph(
      graphContainer,
      stockDataPrices[stockName],
      {
        height: 200,
        yKey: 'price',
        resizeOnWindow: false,
        margin: { top: 20, right: 20, bottom: 40, left: 35 }
      }
    );
  }, 0);

  // Show/hide limit price input on order-type change
  const orderTypeInputs = modal.querySelectorAll('input[name="order-type"]');
  const limitPriceInput  = modal.querySelector('#order-limit-price');
  orderTypeInputs.forEach(input => {
    input.addEventListener('change', () => {
      limitPriceInput.style.display = input.value.startsWith('limit')
        ? 'block'
        : 'none';
    });
  });

  // Place order button
  modal.querySelector('#place-order-btn').addEventListener('click', () => {
    const selected = modal.querySelector('input[name="order-type"]:checked').value;
    handleOrder(stockName, selected, modal);
  });

  // Toggle order book section
  const toggleBtn        = modal.querySelector('#toggle-order-book-btn');
  const orderBookSection = modal.querySelector('.order-book-section');
  const bookContainer    = modal.querySelector('#order-book-container');

  toggleBtn.addEventListener('click', () => {
    const showing = orderBookSection.style.display === 'block';
    orderBookSection.style.display = showing ? 'none' : 'block';
    toggleBtn.textContent = showing ? 'Show Order Book' : 'Hide Order Book';

    if (!showing) {
      // populate with the latest dynamic data
      populateOrderBook(bookContainer, stockDataDynamic[stockName]);
    }
  });
}

// Handles sending the order to the backend API
function handleOrder(stockName, orderType, modal) {
  if (!loggedIn) {
    alert("You must be signed in before placing any order!");
    return;
  }

  const username     = userData.username;
  const amountVal    = modal.querySelector('#order-amount').value.trim();
  const limitVal     = modal.querySelector('#order-limit-price').value.trim();

  if (!amountVal || Number(amountVal) <= 0) {
    alert("Amount must be greater than 0!");
    return;
  }
  if (orderType.startsWith('limit') && (!limitVal || Number(limitVal) <= 0)) {
    alert("Please enter a valid limit price!");
    return;
  }

  const isBuy = orderType.endsWith('_buy');
  const price = orderType.startsWith('limit') ? Number(limitVal) : null;

  const tradeData = {
    ticker:      stockName,
    side:        isBuy ? 'buy' : 'sell',
    client_user: username,
    volume:      Number(amountVal),
    price:       price
  };

  console.log("Sending trade data:", tradeData);

  fetch('/api/place_order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tradeData)
  })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(data => {
      console.log("Server Response:", data);
      alert("Order placed successfully!");
    })
    .catch(err => {
      console.error(err);
      alert("Failed to place the order. Please try again.");
    });
}

// WebSocket for live order book updates
const socket = new WebSocket("ws://localhost:8000/ws");
const stockDataDynamic = {};
let ticker = "AAPL";

socket.addEventListener("open", () => {
  console.log(`Connected to OrderBook WebSocket for ticker: ${ticker}`);
  socket.send(ticker);
});

socket.addEventListener("message", event => {
  const data = JSON.parse(event.data);
  stockDataDynamic[ticker] = data;

  // Append to historic prices if timestamp is new
  const lastDate  = new Date(data.last_timestamp);
  const history   = stockDataPrices[ticker];
  const lastEntry = history[history.length - 1];

  if (Date.parse(lastEntry.date) !== lastDate.getTime()) {
    history.push({ date: lastDate, price: data.last_price });
  }

  // If order book is visible, refresh it
  const bookContainer = document.getElementById("order-book-container");
  if (bookContainer) {
    populateOrderBook(bookContainer, stockDataDynamic[ticker]);
  }
});

socket.addEventListener("close", () => {
  console.log("OrderBook WebSocket connection closed");
});
socket.addEventListener("error", err => {
  console.error("OrderBook WebSocket error:", err);
});
