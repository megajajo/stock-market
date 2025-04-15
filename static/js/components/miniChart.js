

export function drawMiniChart(svgElement, data) {
  // Use the full data if available or choose a subset
  // Here we simply use the entire dataset for this stock.
  const miniData = data; 

  // Dimensions for the mini chart.
  const width = 100;
  const height = 40;
  const margin = { top: 2, right: 2, bottom: 2, left: 2 };

  // Set the SVG attributes.
  const svg = d3.select(svgElement)
    .attr("width", width)
    .attr("height", height);

  // Create scales. You can adjust domain if you want to force a reasonable range.
  const xScale = d3.scaleTime()
    .domain(d3.extent(miniData, d => d.date))
    .range([margin.left, width - margin.right]);

  const yScale = d3.scaleLinear()
    .domain([
      d3.min(miniData, d => d.price),
      d3.max(miniData, d => d.price)
    ])
    .nice()
    .range([height - margin.bottom, margin.top]);

  // Determine the line color based on performance:
  // If the last data point is greater than or equal to the first, color green; otherwise red.
  const firstPrice = miniData[0].price;
  const lastPrice = miniData[miniData.length - 1].price;
  const lineColor = (lastPrice >= firstPrice) ? "#28a745" : "#dc3545";

  // Create the line generator without smoothing.
  const lineGenerator = d3.line()
    .x(d => xScale(d.date))
    .y(d => yScale(d.price));

  // Clear any previous drawing.
  svg.selectAll("*").remove();

  // Draw the mini chart.
  svg.append("path")
    .datum(miniData)
    .attr("fill", "none")
    .attr("stroke", lineColor)
    .attr("stroke-width", 1.5)
    .attr("d", lineGenerator);
}
