export function drawDetailedGraph(containerElement, data, config = {}) {
  const margin = config.margin || { top: 20, right: 20, bottom: 40, left: 50 };

  // Keep mutable values in closure so the updater can mutate them in-place
  let width = config.width || containerElement.clientWidth || 600;
  let height = config.height || 300;
  let sortedData = [...data].sort((a, b) => a.date - b.date);

  // UI state
  let currentRange = 'Max';

  // D3 handles
  let d3svg, xAxisGroup, yAxisGroup, lineGroup, gridGroup, dragRect;
  let currentXScale, globalYScale, lineGenerator;
  let togglesDiv;

  // We build the DOM once and afterwards only update the bits that need it
  let firstBuild = true;
  let formatX;

  function render() {
    width = config.width || containerElement.clientWidth || 600;
    height = config.height || 300;

    const xDomain = getXDomain(currentRange, sortedData);

    // ────────────────────── one-time DOM build ──────────────────────
    if (firstBuild) {
      containerElement.innerHTML = '';

      // Time-frame buttons
      togglesDiv = document.createElement('div');
      togglesDiv.classList.add('timeframe-toggles');
      const timeFrames = ['1D', '1W', '1M', '6M', '1Y', 'Max'];
      timeFrames.forEach(tf => {
        const btn = document.createElement('button');
        btn.textContent = tf;
        btn.classList.add('timeframe-btn');
        btn.dataset.range = tf;
        togglesDiv.appendChild(btn);
      });

      const svgEl = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svgEl.classList.add('portfolio-graph');
      containerElement.appendChild(svgEl);
      containerElement.appendChild(togglesDiv);

      d3svg = d3.select(svgEl).attr('width', width).attr('height', height);

      // Axes & groups
      xAxisGroup = d3svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height - margin.bottom})`);

      yAxisGroup = d3svg.append('g')
        .attr('class', 'y-axis')
        .attr('transform', `translate(${margin.left},0)`);

      gridGroup = d3svg.append('g').attr('class', 'y-grid');
      lineGroup = d3svg.append('g').attr('class', 'line-group');

      // Clip path
      d3svg.append('clipPath').attr('id', 'clip')
        .append('rect')
        .attr('x', margin.left)
        .attr('y', margin.top)
        .attr('width', width - margin.left - margin.right)
        .attr('height', height - margin.top - margin.bottom);

      lineGroup.attr('clip-path', 'url(#clip)');

      // Drag rectangle for panning
      dragRect = d3svg.append('rect')
        .attr('fill', 'transparent')
        .style('cursor', 'move')
        .call(d3.drag().on('start', dragStart).on('drag', dragMove));

      // Button wiring
      togglesDiv.querySelectorAll('.timeframe-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          currentRange = btn.dataset.range;
          togglesDiv.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          render();
        });
      });
      togglesDiv.querySelector('[data-range="Max"]').classList.add('active');

      // Live resize support
      if (config.resizeOnWindow) {
        window.addEventListener('resize', render);
      }

      firstBuild = false;
    } else {
      // Update dimensions & transforms
      d3svg.attr('width', width).attr('height', height);
      xAxisGroup.attr('transform', `translate(0,${height - margin.bottom})`);
      yAxisGroup.attr('transform', `translate(${margin.left},0)`);
      d3svg.select('clipPath#clip rect')
        .attr('width', width - margin.left - margin.right)
        .attr('height', height - margin.top - margin.bottom);
    }

    // Drag rectangle always needs fresh size
    dragRect
      .attr('x', margin.left)
      .attr('y', margin.top)
      .attr('width', width - margin.left - margin.right)
      .attr('height', height - margin.top - margin.bottom);

    // ────────────────────── scales ──────────────────────
    currentXScale = d3.scaleTime().domain(xDomain).range([margin.left, width - margin.right]);

    const visible = sortedData.filter(d => d.date >= xDomain[0] && d.date <= xDomain[1]);
    const yData = visible.length ? visible : sortedData;
    const yMin = d3.min(yData, d => d[config.yKey || 'value'] || d.price);
    const yMax = d3.max(yData, d => d[config.yKey || 'value'] || d.price);
    const yPad = (yMax - yMin) * 0.02;

    globalYScale = d3.scaleLinear()
      .domain([yMin - yPad, yMax + yPad])
      .range([height - margin.bottom, margin.top]);

    const isGain = yData[yData.length - 1][config.yKey || 'value'] >= yData[0][config.yKey || 'value'];

    lineGenerator = d3.line()
      .x(d => currentXScale(d.date))
      .y(d => globalYScale(d[config.yKey || 'value']));

    // ────────────────────── draw / update line ──────────────────────
    lineGroup.selectAll('path')
      .data([sortedData]) // one line → single datum wrapped in array
      .join('path')      // enter/update
        .attr('fill', 'none')
        .attr('stroke', isGain ? '#28a745' : '#dc3545')
        .attr('stroke-width', 3)
        .attr('d', lineGenerator);

     // ────────────────────── axes & grid ──────────────────────
    const numTicks = width < 400 ? 3 : 6;
    formatX = d => {
      const diff = currentXScale.domain()[1] - currentXScale.domain()[0];
      if (diff < 86400000)      return d3.timeFormat('%H:%M')(d);          // < 1 day
      if (diff < 2592000000)    return d3.timeFormat('%b %d %H:%M')(d);    // < 30 days
      return d3.timeFormat('%b %d')(d);
    };

    xAxisGroup.call(d3.axisBottom(currentXScale).ticks(numTicks).tickFormat(formatX));
    yAxisGroup.call(d3.axisLeft(globalYScale).ticks(6));
    yAxisGroup.select('.domain').remove();

    // Grid
    gridGroup.attr('transform', `translate(${margin.left},0)`).call(
      d3.axisLeft(globalYScale)
        .ticks(6)
        .tickSize(-(width - margin.left - margin.right))
        .tickFormat('')
    );
    gridGroup.selectAll('line').attr('stroke', 'grey').attr('stroke-opacity', 0.2);
    gridGroup.select('path').remove();
  }

  // ────────────────────── helpers ──────────────────────
  function getXDomain(range, data) {
    const latest = d3.max(data, d => d.date);
    switch (range) {
      case '1D': return [new Date(latest - 86400000), latest];
      case '1W': return [new Date(latest - 7 * 86400000), latest];
      case '1M': return [new Date(latest - 30 * 86400000), latest];
      case '6M': return [new Date(latest - 180 * 86400000), latest];
      case '1Y': return [new Date(latest - 365 * 86400000), latest];
      case 'Max':
      default:   return d3.extent(data, d => d.date);
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
      new Date(dragStart.domain[1].getTime() - offset)
    ];
    currentXScale.domain(newDomain);

    const updatedTicks = width < 400 ? 3 : 6;
    xAxisGroup.call(
      d3.axisBottom(currentXScale)
        .ticks(updatedTicks)
        .tickFormat(d => {
          const diff = currentXScale.domain()[1] - currentXScale.domain()[0];
          if (diff < 86400000) return d3.timeFormat('%H:%M')(d);
          if (diff < 2592000000) return d3.timeFormat('%b %d %H:%M')(d);
          return d3.timeFormat('%b %d')(d);
        })
    );

    updateYAxisAndLine();
  }

  function updateYAxisAndLine() {
    const visible = sortedData.filter(d => d.date >= currentXScale.domain()[0] && d.date <= currentXScale.domain()[1]);
    const yData = visible.length ? visible : sortedData;
    const min = d3.min(yData, d => d[config.yKey || 'value'] || d.price);
    const max = d3.max(yData, d => d[config.yKey || 'value'] || d.price);
    const pad = (max - min) * 0.02;
    globalYScale.domain([min - pad, max + pad]);

    yAxisGroup.call(d3.axisLeft(globalYScale).ticks(6));
    yAxisGroup.select('.domain').remove();

    gridGroup.call(
      d3.axisLeft(globalYScale)
        .ticks(6)
        .tickSize(-(width - margin.left - margin.right))
        .tickFormat('')
    );
    gridGroup.selectAll('line').attr('stroke', 'grey').attr('stroke-opacity', 0.2);
    gridGroup.select('path').remove();

    lineGenerator.y(d => globalYScale(d[config.yKey || 'value']));
    lineGroup.selectAll('path').attr('d', lineGenerator);

    xAxisGroup.call(d3.axisBottom(currentXScale)
                  .ticks(width < 400 ? 3 : 6)
                  .tickFormat(formatX));   // formatX already defined in render()

  }

  // Initial draw
  render();

  return {
    /**
     * Push fresh data into the graph **without touching the x-domain**,
     * so any pan / zoom the user has made stays exactly as-is.
     */
    update(newData) {
      // 1️⃣  mutate the *same* array reference so the existing <path> keeps its binding
      sortedData.splice(0, sortedData.length,
                        ...newData.sort((a, b) => a.date - b.date));
  
      // 2️⃣  y-axis + line need a refresh because values may be higher/lower now
      updateYAxisAndLine();
  
      // (no call to render(), so the x-scale & buttons stay untouched)
    }
  };
}


