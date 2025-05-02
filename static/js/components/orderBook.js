export function populateOrderBook(container, data) {
  if (!data) return;

  // Clear existing content.
  container.innerHTML = '';

  // Create bids section
  const bidsSection = document.createElement('div');
  bidsSection.classList.add('order-book-bids');
  bidsSection.innerHTML = `
    <h4>Bids</h4>
    <table>
      <thead>
        <tr><th>Price</th><th>Volume</th></tr>
      </thead>
      <tbody></tbody>
    </table>
  `;
  const bidsTbody = bidsSection.querySelector('tbody');
  data.all_bids.forEach(order => {
    const row = document.createElement('tr');
    row.innerHTML = `<td>${order.price}</td><td>${order.volume}</td>`;
    bidsTbody.appendChild(row);
  });

  // Create asks section
  const asksSection = document.createElement('div');
  asksSection.classList.add('order-book-asks');
  asksSection.innerHTML = `
    <h4>Asks</h4>
    <table>
      <thead>
        <tr><th>Price</th><th>Volume</th></tr>
      </thead>
      <tbody></tbody>
    </table>
  `;
  const asksTbody = asksSection.querySelector('tbody');
  data.all_asks.forEach(order => {
    const row = document.createElement('tr');
    row.innerHTML = `<td>${order.price}</td><td>${order.volume}</td>`;
    asksTbody.appendChild(row);
  });

  // Append both sections
  container.appendChild(bidsSection);
  container.appendChild(asksSection);
}
