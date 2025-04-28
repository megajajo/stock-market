// js/components/orderBook.js

export function populateOrderBook(stock, container, data) {
   //const data = orderBookData[stock];

  console.log("Bids:", data.bids);
  console.log("Asks:", data.asks);

  if (!data) return;

  // Clear existing content.
  container.innerHTML = '';

  // Create bids section.
  const bidsSection = document.createElement('div');
  bidsSection.classList.add('order-book-bids');
  bidsSection.innerHTML = `
    <h4>Bids</h4>
    <table>
      <thead>
        <tr><th>Price</th><th>Volume</th><th>Amount</th></tr>
      </thead>
      <tbody></tbody>
    </table>
  `;

  // Create asks section.
  const asksSection = document.createElement('div');
  asksSection.classList.add('order-book-asks');
  asksSection.innerHTML = `
    <h4>Asks</h4>
    <table>
      <thead>
        <tr><th>Price</th><th>Volume</th><th>Amount</th></tr>
      </thead>
      <tbody></tbody>
    </table>
  `;

  const bidsTbody = bidsSection.querySelector('tbody');
  const asksTbody = asksSection.querySelector('tbody');

  data.bids.forEach(order => {
    const row = document.createElement('tr');
    const amount = order.price * order.volume;
    row.innerHTML = `<td>${order.price}</td><td>${order.volume}</td><td>${amount}</td>`;
    bidsTbody.appendChild(row);
  });

  data.asks.forEach(order => {
    const row = document.createElement('tr');
    const amount = order.price * order.volume;
    row.innerHTML = `<td>${order.price}</td><td>${order.volume}</td><td>${amount}</td>`;
    asksTbody.appendChild(row);
  });

  // Append both sections to the container.
  container.appendChild(bidsSection);
  container.appendChild(asksSection);
}
