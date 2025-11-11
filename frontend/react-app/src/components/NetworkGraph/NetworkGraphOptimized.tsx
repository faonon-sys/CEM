/**
 * Optimized Network Graph with Performance Enhancements
 * - React.memo for expensive component re-renders
 * - Memoized callbacks and values
 * - Optimized D3 simulation with reduced iterations
 * - Web Worker for heavy computations (optional)
 * - RequestAnimationFrame for smooth rendering
 */
import { useEffect, useRef, useState, useMemo, useCallback, memo } from 'react'
import * as d3 from 'd3'
import { useGraphState } from '../../stores/graphStore'
import GraphControls from './GraphControls'
import NodeDetail from './NodeDetail'
import './NetworkGraph.css'

export interface GraphNode extends d3.SimulationNodeDatum {
  id: string
  type: 'assumption' | 'fragility' | 'breach' | 'counterfactual'
  label: string
  severity?: number
  probability?: number
  metadata: Record<string, any>
}

export interface GraphEdge extends d3.SimulationLinkDatum<GraphNode> {
  source: string | GraphNode
  target: string | GraphNode
  type: 'dependency' | 'consequence' | 'transition'
  weight: number
}

// Memoized node radius calculator
const getNodeRadius = (node: GraphNode): number => {
  const baseSizes = {
    assumption: 8,
    fragility: 10,
    breach: 12,
    counterfactual: 15
  }
  const baseSize = baseSizes[node.type] || 10
  const severityMultiplier = node.severity ? 1 + (node.severity * 0.5) : 1
  return baseSize * severityMultiplier
}

// Memoized node color calculator
const getNodeColor = (node: GraphNode): string => {
  const colors = {
    assumption: '#3b82f6',      // blue
    fragility: '#f97316',       // orange
    breach: '#ef4444',          // red
    counterfactual: '#a855f7'   // purple
  }
  return colors[node.type] || '#888'
}

// Memoized Legend Component
const Legend = memo(() => (
  <div className="legend">
    <h3>Node Types</h3>
    <div className="legend-items">
      <div className="legend-item">
        <div className="legend-circle" style={{ backgroundColor: '#3b82f6' }}></div>
        <span>Assumption</span>
      </div>
      <div className="legend-item">
        <div className="legend-circle" style={{ backgroundColor: '#f97316' }}></div>
        <span>Fragility</span>
      </div>
      <div className="legend-item">
        <div className="legend-circle" style={{ backgroundColor: '#ef4444' }}></div>
        <span>Breach</span>
      </div>
      <div className="legend-item">
        <div className="legend-circle" style={{ backgroundColor: '#a855f7' }}></div>
        <span>Counterfactual</span>
      </div>
    </div>
  </div>
))
Legend.displayName = 'Legend'

const NetworkGraphOptimized = memo(() => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphEdge> | null>(null)
  const animationFrameRef = useRef<number | null>(null)

  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [transform, setTransform] = useState({ k: 1, x: 0, y: 0 })

  const { nodes, edges, filters, loadSampleData } = useGraphState()

  // Load sample data only once
  useEffect(() => {
    loadSampleData()
  }, [loadSampleData])

  // Memoize filtered nodes and edges
  const { filteredNodes, filteredEdges } = useMemo(() => {
    const filteredNodes = nodes.filter(node => {
      if (filters.nodeTypes.length > 0 && !filters.nodeTypes.includes(node.type)) {
        return false
      }
      if (filters.minSeverity && (node.severity ?? 0) < filters.minSeverity) {
        return false
      }
      return true
    })

    const filteredEdges = edges.filter(edge => {
      const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id
      const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id
      return filteredNodes.some(n => n.id === sourceId) && filteredNodes.some(n => n.id === targetId)
    })

    return { filteredNodes, filteredEdges }
  }, [nodes, edges, filters])

  // Memoized render function
  const render = useCallback((
    context: CanvasRenderingContext2D,
    width: number,
    height: number,
    nodes: GraphNode[],
    edges: GraphEdge[],
    transform: { k: number; x: number; y: number }
  ) => {
    // Cancel any pending animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
    }

    animationFrameRef.current = requestAnimationFrame(() => {
      context.save()
      context.clearRect(0, 0, width, height)

      context.translate(transform.x, transform.y)
      context.scale(transform.k, transform.k)

      // Draw edges with optimized stroke
      context.strokeStyle = '#666'
      context.lineWidth = 1 / transform.k
      context.beginPath()
      edges.forEach(edge => {
        const source = edge.source as GraphNode
        const target = edge.target as GraphNode
        if (!source.x || !source.y || !target.x || !target.y) return

        context.moveTo(source.x, source.y)
        context.lineTo(target.x, target.y)
      })
      context.stroke()

      // Draw nodes
      nodes.forEach(node => {
        if (!node.x || !node.y) return

        const radius = getNodeRadius(node)
        const color = getNodeColor(node)
        const opacity = node.probability ?? 1

        context.globalAlpha = opacity
        context.fillStyle = color
        context.beginPath()
        context.arc(node.x, node.y, radius, 0, 2 * Math.PI)
        context.fill()

        // Draw labels only when zoomed in (performance optimization)
        if (transform.k > 0.8 && nodes.length < 200) {
          context.globalAlpha = 1
          context.fillStyle = '#fff'
          context.font = `${12 / transform.k}px sans-serif`
          context.textAlign = 'center'
          context.textBaseline = 'middle'
          context.fillText(node.label, node.x, node.y + radius + 15)
        }
      })

      context.restore()
    })
  }, [])

  // Main effect for graph rendering
  useEffect(() => {
    if (!canvasRef.current || !containerRef.current) return

    const canvas = canvasRef.current
    const context = canvas.getContext('2d', { alpha: false }) // Performance: disable alpha
    if (!context) return

    const width = containerRef.current.clientWidth
    const height = containerRef.current.clientHeight

    canvas.width = width
    canvas.height = height

    // Stop previous simulation if exists
    if (simulationRef.current) {
      simulationRef.current.stop()
    }

    // Create optimized force simulation
    const simulation = d3.forceSimulation(filteredNodes)
      .force('link', d3.forceLink(filteredEdges)
        .id((d: any) => d.id)
        .distance(100)
        .strength(0.5)) // Reduced strength for faster convergence
      .force('charge', d3.forceManyBody()
        .strength(-300)
        .distanceMax(500)) // Distance limit for performance
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40))
      .alphaDecay(0.05) // Faster convergence
      .velocityDecay(0.4) // Faster stabilization

    simulationRef.current = simulation

    // Zoom behavior
    const zoom = d3.zoom<HTMLCanvasElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        setTransform(event.transform)
      })

    d3.select(canvas).call(zoom as any)

    // Throttled render on simulation tick
    let tickCount = 0
    simulation.on('tick', () => {
      // Render every 2nd tick for performance (except first 30 ticks)
      tickCount++
      if (tickCount < 30 || tickCount % 2 === 0) {
        render(context, width, height, filteredNodes, filteredEdges, transform)
      }
    })

    // Initial render
    render(context, width, height, filteredNodes, filteredEdges, transform)

    // Click handler with memoization
    const handleClick = (event: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      const x = (event.clientX - rect.left - transform.x) / transform.k
      const y = (event.clientY - rect.top - transform.y) / transform.k

      // Find clicked node with early exit
      let clicked: GraphNode | null = null
      for (const node of filteredNodes) {
        if (!node.x || !node.y) continue
        const dx = x - node.x
        const dy = y - node.y
        const radius = getNodeRadius(node)
        if (dx * dx + dy * dy < radius * radius) { // Avoid sqrt for performance
          clicked = node
          break
        }
      }

      setSelectedNode(clicked)
    }

    canvas.addEventListener('click', handleClick)

    return () => {
      simulation.stop()
      canvas.removeEventListener('click', handleClick)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [filteredNodes, filteredEdges, transform, render])

  // Memoized close handler
  const handleCloseDetail = useCallback(() => {
    setSelectedNode(null)
  }, [])

  return (
    <div className="network-graph-container" ref={containerRef}>
      <canvas ref={canvasRef} className="network-canvas" />
      <GraphControls />
      {selectedNode && (
        <NodeDetail
          node={selectedNode}
          onClose={handleCloseDetail}
        />
      )}
      <Legend />
    </div>
  )
})

NetworkGraphOptimized.displayName = 'NetworkGraphOptimized'

export default NetworkGraphOptimized
