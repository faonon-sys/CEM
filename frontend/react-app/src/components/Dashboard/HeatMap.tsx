/**
 * Heat Map Component using D3.js
 * Sprint 4.5 - Task 3
 *
 * Visualizes risk distribution across strategic axes and domains
 */
import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export interface HeatMapData {
  x: string
  y: string
  value: number
}

interface HeatMapProps {
  data: HeatMapData[]
  xLabels: string[]
  yLabels: string[]
  title: string
  colorScale?: d3.ScaleSequential<string>
  onCellClick?: (x: string, y: string, value: number) => void
  width?: number
  height?: number
}

const HeatMap: React.FC<HeatMapProps> = ({
  data,
  xLabels,
  yLabels,
  title,
  colorScale = d3.interpolateReds,
  onCellClick,
  width = 600,
  height = 400
}) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!svgRef.current || !data.length) return

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove()

    const margin = { top: 60, right: 40, bottom: 60, left: 120 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const xScale = d3
      .scaleBand()
      .domain(xLabels)
      .range([0, innerWidth])
      .padding(0.05)

    const yScale = d3
      .scaleBand()
      .domain(yLabels)
      .range([0, innerHeight])
      .padding(0.05)

    // Find max value for color scaling
    const maxValue = d3.max(data, d => d.value) || 1
    const color = d3
      .scaleSequential(colorScale)
      .domain([0, maxValue])

    // Create cells
    svg
      .selectAll('rect')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => xScale(d.x) || 0)
      .attr('y', d => yScale(d.y) || 0)
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', d => d.value > 0 ? color(d.value) : '#f0f0f0')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .attr('rx', 4)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        // Highlight cell
        d3.select(this)
          .attr('stroke', '#000')
          .attr('stroke-width', 3)

        // Show tooltip
        if (tooltipRef.current) {
          const tooltip = d3.select(tooltipRef.current)
          tooltip
            .style('opacity', 1)
            .style('left', `${event.pageX + 10}px`)
            .style('top', `${event.pageY - 10}px`)
            .html(`
              <strong>${d.x} × ${d.y}</strong><br/>
              Count: ${d.value}<br/>
              Percentage: ${((d.value / data.reduce((sum, item) => sum + item.value, 0)) * 100).toFixed(1)}%
            `)
        }
      })
      .on('mouseout', function() {
        // Remove highlight
        d3.select(this)
          .attr('stroke', '#fff')
          .attr('stroke-width', 2)

        // Hide tooltip
        if (tooltipRef.current) {
          d3.select(tooltipRef.current).style('opacity', 0)
        }
      })
      .on('click', function(_event, d) {
        if (onCellClick) {
          onCellClick(d.x, d.y, d.value)
        }
      })

    // Add cell labels (show count if > 0)
    svg
      .selectAll('text.cell-label')
      .data(data.filter(d => d.value > 0))
      .enter()
      .append('text')
      .attr('class', 'cell-label')
      .attr('x', d => (xScale(d.x) || 0) + xScale.bandwidth() / 2)
      .attr('y', d => (yScale(d.y) || 0) + yScale.bandwidth() / 2)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', d => d.value > maxValue * 0.5 ? '#fff' : '#000')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .style('pointer-events', 'none')
      .text(d => d.value)

    // X axis
    svg
      .append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')

    // Y axis
    svg
      .append('g')
      .call(d3.axisLeft(yScale))

    // Title
    svg
      .append('text')
      .attr('x', innerWidth / 2)
      .attr('y', -30)
      .attr('text-anchor', 'middle')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .text(title)

    // Legend
    const legendWidth = 200
    const legendHeight = 20

    const legendScale = d3
      .scaleLinear()
      .domain([0, maxValue])
      .range([0, legendWidth])

    const legendAxis = d3
      .axisBottom(legendScale)
      .ticks(5)

    const legend = svg
      .append('g')
      .attr('transform', `translate(${innerWidth - legendWidth}, ${innerHeight + 40})`)

    // Legend gradient
    const defs = svg.append('defs')
    const gradient = defs
      .append('linearGradient')
      .attr('id', 'legend-gradient')

    const numStops = 10
    for (let i = 0; i <= numStops; i++) {
      const offset = (i / numStops) * 100
      const value = (i / numStops) * maxValue
      gradient
        .append('stop')
        .attr('offset', `${offset}%`)
        .attr('stop-color', color(value))
    }

    legend
      .append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#legend-gradient)')

    legend
      .append('g')
      .attr('transform', `translate(0,${legendHeight})`)
      .call(legendAxis)

  }, [data, xLabels, yLabels, title, colorScale, onCellClick, width, height])

  return (
    <div style={{ position: 'relative' }}>
      <svg ref={svgRef}></svg>
      <div
        ref={tooltipRef}
        style={{
          position: 'absolute',
          opacity: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          color: '#fff',
          padding: '8px 12px',
          borderRadius: '4px',
          fontSize: '12px',
          pointerEvents: 'none',
          zIndex: 1000
        }}
      />
    </div>
  )
}

export default HeatMap
