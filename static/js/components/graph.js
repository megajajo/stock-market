export function drawDetailedGraph(containerElement, data, config = {}) {
  const width = config.width || containerElement.clientWidth || 600;
  const height = config.height || 300;
  const margin = config.margin || { top: 20, right: 20, bottom: 40, left: 50 };

  const sortedData = [...data].sort((a, b) => a.date - b.date);

  let currentRange = 'Max';
  let currentXScale, globalYScale, lineGenerator;
  let d3svg, xAxisGroup, yAxisGroup, lineGroup, gridGroup, dragRect;

  // --- Clear previous content ---
  containerElement.innerHTML = '';

  // --- Create timeframe buttons ---
  const togglesDiv = document.createElement('div');
  togglesDiv.classList.add('timeframe-toggles');

  const timeFrames = ['1D', '1W', '1M', '6M', '1Y', 'Max'];
  timeFrames.forEach(tf => {
    const btn = document.createElement('button');
    btn.textContent = tf;
    btn.classList.add('timeframe-btn');
    btn.dataset.range = tf;
    togglesDiv.appendChild(btn);
  });

  // --- Create SVG ---
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.classList.add('portfolio-graph');
  containerElement.appendChild(svg);
  containerElement.appendChild(togglesDiv);

  // --- Graph render function ---
  function render() {
    const xDomain = getXDomain(currentRange, sortedData);

    d3.select(svg).attr('width', width).attr('height', height);
    d3svg = d3.select(svg);

    if (!xAxisGroup) {
      xAxisGroup = d3svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', 'translate(0,' + (height - margin.bottom) + ')');
      yAxisGroup = d3svg.append('g')
        .attr('class', 'y-axis')
        .attr('transform', 'translate(' + margin.left + ',0)');
      // Append grid before line so grid lines are underneath
      gridGroup = d3svg.append('g').attr('class', 'y-grid');
      lineGroup = d3svg.append('g').attr('class', 'line-group');
    } else {
      lineGroup.selectAll('*').remove();
      gridGroup.selectAll('*').remove();
    }

    // Clip path
    let clip = d3svg.select('clipPath#clip');
    if (clip.empty()) {
      d3svg.append('clipPath').attr('id', 'clip')
        .append('rect')
        .attr('x', margin.left)
        .attr('y', margin.top)
        .attr('width', width - margin.left - margin.right)
        .attr('height', height - margin.top - margin.bottom);
    } else {
      clip.select('rect')
        .attr('x', margin.left)
        .attr('y', margin.top)
        .attr('width', width - margin.left - margin.right)
        .attr('height', height - margin.top - margin.bottom);
    }
    lineGroup.attr('clip-path', 'url(#clip)');

    // Drag area
    if (!dragRect) {
      dragRect = d3svg.append('rect')
        .attr('fill', 'transparent')
        .style('cursor', 'move')
        .call(d3.drag().on('start', dragStart).on('drag', dragMove));
    }
    dragRect
      .attr('x', margin.left)
      .attr('y', margin.top)
      .attr('width', width - margin.left - margin.right)
      .attr('height', height - margin.top - margin.bottom);

    currentXScale = d3.scaleTime().domain(xDomain).range([margin.left, width - margin.right]);

    const visible = sortedData.filter(d => d.date >= xDomain[0] && d.date <= xDomain[1]);
    const yData = visible.length ? visible : sortedData;
    const yMin = d3.min(yData, d => d.value || d.price);
    const yMax = d3.max(yData, d => d.value || d.price);
    const yPad = (yMax - yMin) * 0.02;

    globalYScale = d3.scaleLinear()
      .domain([yMin - yPad, yMax + yPad])
      .range([height - margin.bottom, margin.top]);

    const isGain = yData[yData.length - 1][config.yKey || 'value'] >= yData[0][config.yKey || 'value'];

    lineGenerator = d3.line()
      .x(d => currentXScale(d.date))
      .y(d => globalYScale(d[config.yKey || 'value']));

    lineGroup.append('path')
      .datum(sortedData)
      .attr('fill', 'none')
      .attr('stroke', isGain ? '#28a745' : '#dc3545')
      .attr('stroke-width', 3)
      .attr('d', lineGenerator);

    const numTicks = width < 400 ? 3 : 6;
    const formatX = d => {
      const range = currentXScale.domain();
      const diff = range[1] - range[0];
      if (diff < 86400000) return d3.timeFormat('%H:%M')(d);
      if (diff < 2592000000) return d3.timeFormat('%b %d %H:%M')(d);
      return d3.timeFormat('%b %d')(d);
    };

    const xAxis = d3.axisBottom(currentXScale).ticks(numTicks).tickFormat(formatX);
    const yAxis = d3.axisLeft(globalYScale).ticks(6);

    xAxisGroup.call(xAxis);
    yAxisGroup.call(yAxis);
    yAxisGroup.select('.domain').remove();

    // Grid
    const yGrid = d3.axisLeft(globalYScale)
      .ticks(6)
      .tickSize(- (width - margin.left - margin.right))
      .tickFormat('');

    gridGroup.attr('transform', 'translate(' + margin.left + ',0)').call(yGrid);
    gridGroup.selectAll('line').attr('stroke', 'grey').attr('stroke-opacity', 0.2);
    gridGroup.select('path').remove();
  }

  function getXDomain(range, data) {
    const latest = d3.max(data, d => d.date);
    switch (range) {
      case '1D': return [new Date(latest - 86400000), latest];
      case '1W': return [new Date(latest - 7 * 86400000), latest];
      case '1M': return [new Date(latest - 30 * 86400000), latest];
      case '6M': return [new Date(latest - 180 * 86400000), latest];
      case '1Y': return [new Date(latest - 365 * 86400000), latest];
      case 'Max': default: return d3.extent(data, d => d.date);
    }
  }

  function dragStart(event) {
    dragStart.x = event.x;
    dragStart.domain = currentXScale.domain();
  }

  function dragMove(event) {
    const dx = event.x - dragStart.x;
    const span = dragStart.domain[1] - dragStart.domain[0];
    const offset = dx / (width - margin.left - margin.right) * span;
    const newDomain = [
      new Date(dragStart.domain[0].getTime() - offset),
      new Date(dragStart.domain[1].getTime() - offset),
    ];
    currentXScale.domain(newDomain);
    const updatedTicks = width < 400 ? 3 : 6;
    const updatedXAxis = d3.axisBottom(currentXScale)
      .ticks(updatedTicks)
      .tickFormat(d => {
        const range = currentXScale.domain();
        const diff = range[1] - range[0];
        if (diff < 86400000) return d3.timeFormat('%H:%M')(d);
        if (diff < 2592000000) return d3.timeFormat('%b %d %H:%M')(d);
        return d3.timeFormat('%b %d')(d);
      });

    xAxisGroup.call(updatedXAxis);

    updateYAxisAndLine();
  }

  function updateYAxisAndLine() {
    const visible = sortedData.filter(d =>
      d.date >= currentXScale.domain()[0] && d.date <= currentXScale.domain()[1]
    );
    const yData = visible.length ? visible : sortedData;
    const min = d3.min(yData, d => d.value || d.price);
    const max = d3.max(yData, d => d.value || d.price);
    const pad = (max - min) * 0.02;
    globalYScale.domain([min - pad, max + pad]);

    yAxisGroup.call(d3.axisLeft(globalYScale).ticks(6));
    yAxisGroup.select('.domain').remove();

    gridGroup.call(
      d3.axisLeft(globalYScale)
        .ticks(6)
        .tickSize(- (width - margin.left - margin.right))
        .tickFormat('')
    );
    gridGroup.selectAll('line').attr('stroke', 'grey').attr('stroke-opacity', 0.2);
    gridGroup.select('path').remove();

    lineGenerator.y(d => globalYScale(d[config.yKey || 'value']));
    lineGroup.selectAll('path').attr('d', lineGenerator);
  }

  // Activate button logic
  togglesDiv.querySelectorAll('.timeframe-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      currentRange = btn.dataset.range;
      togglesDiv.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      render();
    });
  });

  // Set default active state and render initially
  togglesDiv.querySelector('[data-range=\"Max\"]').classList.add('active');
  render();

  if (config.resizeOnWindow) {
    window.addEventListener('resize', render);
  }
}
