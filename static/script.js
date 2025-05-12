//THIS FILE IS ONLY HERE FOR REFEREBCE- IT'S ESSENTIALLY INERT

const stockData = {
    "AAPL": [
        { date: new Date(2024, 0, 1), price: 100 },
        { date: new Date(2024, 0, 2), price: 105 },
        { date: new Date(2024, 0, 3), price: 102 }
    ],
    "Stock B": [
        { date: new Date(2024, 0, 1), price: 200 },
        { date: new Date(2024, 0, 2), price: 195 },
        { date: new Date(2024, 0, 3), price: 198 }
    ],
    "Stock C": [
        { date: new Date(2024, 0, 1), price: 300 },
        { date: new Date(2024, 0, 2), price: 290 },
        { date: new Date(2024, 0, 3), price: 295 }
    ],
    "Stock D": [
        { date: new Date(2024, 0, 1), price: 400 },
        { date: new Date(2024, 0, 2), price: 405 },
        { date: new Date(2024, 0, 3), price: 398 }
    ]
};

const orderBookData = {
  "AAPL": {
      bids: [
      ],
      asks: [
      ]
  },
  "GOOG": {
      bids: [
      ],
      asks: [
      ]
  },
  "TSLA": {
      bids: [
      ],
      asks: [
      ]
  },

};



const container = document.getElementById('stock-container');
Object.keys(stockData).forEach(stockName => {
    const stockBox = document.createElement('div');
    stockBox.classList.add('stock-box');

    stockBox.innerHTML = `
    <div class="stock-title">${stockName}</div>
    <svg class="stock-chart"></svg>
    <input type="text" class="username-input" placeholder="Enter username">
    <input type="number" class="amount-input" placeholder="Enter amount">
    <input type="number" class="price-input" placeholder="Enter limit price">
    <button class="buy-btn">Buy</button>
    <button class="sell-btn">Sell</button>
    <button class="order-book-btn">Show Order Book</button>
    <div class="order-book-container" style="display: none;">
        <div class="order-book-section bids-section">
            <h4>Bids</h4>
            <table class="order-book-table">
                <thead>
                    <tr>
                        <th>Price</th>
                        <th>Volume</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Bids will be inserted here -->
                </tbody>
            </table>
        </div>
        <div class="order-book-section asks-section">
            <h4>Asks</h4>
            <table class="order-book-table">
                <thead>
                    <tr>
                        <th>Price</th>
                        <th>Volume</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Asks will be inserted here -->
                </tbody>
            </table>
        </div>
    </div>
`;



    container.appendChild(stockBox);

    // do the graph first
    drawGraph(stockBox.querySelector('svg'), stockData[stockName]);

    // add the listeners for hte buttons
    stockBox.querySelector('.buy-btn').addEventListener('click', () => handleTrade(stockName, 'buy', stockBox));
    stockBox.querySelector('.sell-btn').addEventListener('click', () => handleTrade(stockName, 'sell', stockBox));

    const orderBookBtn = stockBox.querySelector('.order-book-btn');
const orderBookContainer = stockBox.querySelector('.order-book-container');

orderBookBtn.addEventListener('click', () => {
    if (orderBookContainer.style.display === "none") {
        orderBookContainer.style.display = "block";
        orderBookBtn.textContent = "Hide Order Book";
        populateOrderBook(stockName, orderBookContainer);
    } else {
        orderBookContainer.style.display = "none";
        orderBookBtn.textContent = "Show Order Book";
    }
});
});

function drawGraph(svgElement, data) {
    const width = 250, height = 140, margin = 30;

    const svg = d3.select(svgElement)
      .attr("width", width)
      .attr("height", height);

    // Create a clipPath so the graph is not drawn outside the axis area.
    svg.append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("x", margin)
        .attr("y", margin)
        .attr("width", width - margin * 2)
        .attr("height", height - margin * 2);

    // Create initial scales from the data.
    let x = d3.scaleTime()
      .domain(d3.extent(data, d => d.date))
      .range([margin, width - margin]);

    let minPrice = d3.min(data, d => d.price);
    let maxPrice = d3.max(data, d => d.price);
    let y = d3.scaleLinear()
      .domain([minPrice - 5, maxPrice + 5])
      .range([height - margin, margin]);

    // Save the initial domains to enforce limits.
    const xDomainInit = x.domain();
    const yDomainInit = y.domain();

    // Define allowed panning limits.
    const xMinAllowed = new Date(xDomainInit[0].getTime() - 2 * 24 * 60 * 60 * 1000); // 2 days before
    const xMaxAllowed = new Date(xDomainInit[1].getTime() + 2 * 24 * 60 * 60 * 1000); // 2 days after
    const yMinAllowed = yDomainInit[0] - 20;
    const yMaxAllowed = yDomainInit[1] + 20;

    // Group for the graph (line) with clipPath applied.
    const graphGroup = svg.append("g")
      .attr("clip-path", "url(#clip)");

    // Create the line generator.
    const line = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.price));

    // Draw the line.
    const path = graphGroup.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "blue")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Create axes groups (outside the clipPath so they remain visible).
    const xAxisGroup = svg.append("g")
      .attr("transform", `translate(0,${height - margin})`);
    const yAxisGroup = svg.append("g")
      .attr("transform", `translate(${margin},0)`);

    // Function to update the line and axes.
    function updateChart() {
      path.attr("d", line);
      xAxisGroup.call(d3.axisBottom(x)
        .ticks(3)
        .tickFormat(d3.timeFormat("%b %d")));
      yAxisGroup.call(d3.axisLeft(y)
        .ticks(5)
        .tickFormat(d3.format(".0f")));
      // Ensure axes remain on top.
      xAxisGroup.raise();
      yAxisGroup.raise();
    }
    updateChart();

    // Variables to store the start state for dragging.
    let startX, startY, startDomainX, startDomainY;

    // A transparent rectangle to capture drag and wheel events.
    const dragRect = svg.append("rect")
      .attr("width", width - margin * 2)
      .attr("height", height - margin * 2)
      .attr("x", margin)
      .attr("y", margin)
      .attr("fill", "transparent")
      .style("cursor", "move");

    // Drag behavior (click & drag).
    dragRect.call(d3.drag()
      .on("start", function(event) {
        startX = event.x;
        startY = event.y;
        startDomainX = x.domain();
        startDomainY = y.domain();
      })
      .on("drag", function(event) {
        const dx = event.x - startX;
        const dy = event.y - startY;

        // Calculate new x domain based on pixel shift.
        const xDomainSpan = startDomainX[1] - startDomainX[0];
        const xPixelSpan = width - margin * 2;
        const timeOffset = dx / xPixelSpan * xDomainSpan;
        let newXDomain = [
          new Date(startDomainX[0].getTime() - timeOffset),
          new Date(startDomainX[1].getTime() - timeOffset)
        ];

        // Calculate new y domain.
        const yDomainSpan = startDomainY[1] - startDomainY[0];
        const yPixelSpan = height - margin * 2;
        const priceOffset = dy / yPixelSpan * yDomainSpan;
        let newYDomain = [
          startDomainY[0] + priceOffset,
          startDomainY[1] + priceOffset
        ];

        // Enforce horizontal limits.
        if(newXDomain[0] < xMinAllowed) {
          const diff = xMinAllowed - newXDomain[0];
          newXDomain = [
            new Date(newXDomain[0].getTime() + diff),
            new Date(newXDomain[1].getTime() + diff)
          ];
        }
        if(newXDomain[1] > xMaxAllowed) {
          const diff = newXDomain[1] - xMaxAllowed;
          newXDomain = [
            new Date(newXDomain[0].getTime() - diff),
            new Date(newXDomain[1].getTime() - diff)
          ];
        }

        // Enforce vertical limits.
        if(newYDomain[0] < yMinAllowed) {
          const diff = yMinAllowed - newYDomain[0];
          newYDomain = [newYDomain[0] + diff, newYDomain[1] + diff];
        }
        if(newYDomain[1] > yMaxAllowed) {
          const diff = newYDomain[1] - yMaxAllowed;
          newYDomain = [newYDomain[0] - diff, newYDomain[1] - diff];
        }

        x.domain(newXDomain);
        y.domain(newYDomain);
        updateChart();
      })
    );

    // Wheel behavior (two-finger scrolling).
    dragRect.on("wheel", function(event) {
      event.preventDefault(); // Prevent the default page scroll.

      const curXDomain = x.domain();
      const curYDomain = y.domain();

      const xDomainSpan = curXDomain[1] - curXDomain[0];
      const yDomainSpan = curYDomain[1] - curYDomain[0];
      const xPixelSpan = width - margin * 2;
      const yPixelSpan = height - margin * 2;

      // Use wheel delta values as pixel offsets.
      const timeOffset = event.deltaX / xPixelSpan * xDomainSpan;
      const priceOffset = event.deltaY / yPixelSpan * yDomainSpan;

      let newXDomain = [
        new Date(curXDomain[0].getTime() - timeOffset),
        new Date(curXDomain[1].getTime() - timeOffset)
      ];
      let newYDomain = [
        curYDomain[0] + priceOffset,
        curYDomain[1] + priceOffset
      ];

      // Enforce horizontal limits.
      if(newXDomain[0] < xMinAllowed) {
        const diff = xMinAllowed - newXDomain[0];
        newXDomain = [
          new Date(newXDomain[0].getTime() + diff),
          new Date(newXDomain[1].getTime() + diff)
        ];
      }
      if(newXDomain[1] > xMaxAllowed) {
        const diff = newXDomain[1] - xMaxAllowed;
        newXDomain = [
          new Date(newXDomain[0].getTime() - diff),
          new Date(newXDomain[1].getTime() - diff)
        ];
      }

      // Enforce vertical limits.
      if(newYDomain[0] < yMinAllowed) {
        const diff = yMinAllowed - newYDomain[0];
        newYDomain = [newYDomain[0] + diff, newYDomain[1] + diff];
      }
      if(newYDomain[1] > yMaxAllowed) {
        const diff = newYDomain[1] - yMaxAllowed;
        newYDomain = [newYDomain[0] - diff, newYDomain[1] - diff];
      }

      x.domain(newXDomain);
      y.domain(newYDomain);
      updateChart();
    });
  }


// func for the buy and sell buttons
function handleTrade(stock, type, stockBox) {
    const username = stockBox.querySelector('.username-input').value.trim();
    const amountVal = stockBox.querySelector('.amount-input').value.trim();
    const limitPriceVal = stockBox.querySelector('.price-input').value.trim();

    if (!username) {
        alert("Username cannot be empty!");
        return;
    }
    if (!amountVal || Number(amountVal) <= 0) {
        alert("Amount cannot be empty or 0!");
        return;
    }
    if (!limitPriceVal || Number(limitPriceVal) <= 0) {
        alert("Limit price cannot be empty or 0!");
        return;
    }

    // Prepare the data to send to the backend
    const tradeData = {
        ticker: stock, // Stock ticker (e.g., "AAPL")
        side: type, // "buy" or "sell"
        price: parseFloat(limitPriceVal), // Limit price as a float
        volume: parseInt(amountVal, 10), // Volume as an integer
        client_user: username // Replace with the actual client ID (hardcoded for now)
    };
    console.log(username)
    console.log("Sending data to backend:", tradeData);

    // Make the fetch call to the backend
    fetch('/api/place_order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tradeData) // Convert the data to JSON format
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Server Response:", data);
        alert("Order placed successfully!");
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Failed to place the order. Please try again.");
    });
}

function populateOrderBook(stock, container) {
  const bidsTbody = container.querySelector('.bids-section tbody');
  const asksTbody = container.querySelector('.asks-section tbody');

  // Clear any previous rows
  bidsTbody.innerHTML = "";
  asksTbody.innerHTML = "";

  // Make the fetch call to the backend
  // Get bids data
  fetch(`/api/get_all_bids?ticker=${stock}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
  .then(response => {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log("Server Response:", data);

    if(data && data.length > 0) {
        // Populate bids
        data.forEach(order => {
          //console.log(order.volume, order.price);
          const row = document.createElement('tr');
          const amount = order.price * order.volume;
          row.innerHTML = `<td>${order.price}</td><td>${order.volume}</td><td>${amount}</td>`;
          bidsTbody.appendChild(row);
        });
      }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("Failed to get bids from order book. Please try again.");
  });

  // get asks data
  fetch(`/api/get_all_asks?ticker=${stock}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
  .then(response => {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log("Server Response:", data);

    if(data && data.length > 0) {
        // Populate asks
        data.forEach(order => {
          const row = document.createElement('tr');
          const amount = order.price * order.volume;
          row.innerHTML = `<td>${order.price}</td><td>${order.volume}</td><td>${amount}</td>`;
          asksTbody.appendChild(row);
        });
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("Failed to get asks order book content. Please try again.");
  });

}
