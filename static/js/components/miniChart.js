

// js/components/miniChart.js


export function drawMiniChart(containerElement, data, config = {}) {
  //console.log("MINI CHART", data);
  // — Configurable dimensions & margins —
  const width  = config.width  || 100;
  const height = config.height || 40;
  const margin = config.margin || { top:2, right:2, bottom:2, left:2 };
  const yKey   = config.yKey   || 'price';  // matches your stockData

  // — Clear out any old content —
  containerElement.innerHTML = '';

  // — Create the SVG —
  const svg = document.createElementNS("http://www.w3.org/2000/svg","svg");
  svg.setAttribute("width",  width);
  svg.setAttribute("height", height);
  containerElement.appendChild(svg);
  const d3svg = d3.select(svg);

  // — Sort & prepare data —
  const miniData = [...data].sort((a,b)=>a.date - b.date);

  // — Scales —
  const xScale = d3.scaleTime()
    .domain(d3.extent(miniData, d=>d.date))
    .range([margin.left, width - margin.right]);

  const yScale = d3.scaleLinear()
    .domain([
      d3.min(miniData, d=>d[yKey]),
      d3.max(miniData, d=>d[yKey])
    ]).nice()
    .range([height - margin.bottom, margin.top]);

  // — Line color by performance —
  const first = miniData[0][yKey], last = miniData[miniData.length-1][yKey];
  const lineColor = last >= first ? "#28a745" : "#dc3545";

  // — Line generator —
  const lineGen = d3.line()
    .x(d=>xScale(d.date))
    .y(d=>yScale(d[yKey]));

  // — Clear & draw —
  d3svg.selectAll("*").remove();
  d3svg.append("path")
    .datum(miniData)
    .attr("fill","none")
    .attr("stroke", lineColor)
    .attr("stroke-width",1.5)
    .attr("d", lineGen);
}
