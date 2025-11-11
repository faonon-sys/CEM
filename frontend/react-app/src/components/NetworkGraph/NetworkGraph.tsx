import { useEffect, useRef, useState } from 'react'
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

const NetworkGraph = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [transform, setTransform] = useState({ k: 1, x: 0, y: 0 })

  const { nodes, edges, filters, loadSampleData } = useGraphState()

  useEffect(() => {
    // Load sample data on mount
    loadSampleData()
  }, [loadSampleData])

  useEffect(() => {
    if (!canvasRef.current || !containerRef.current) return

    const canvas = canvasRef.current
    const context = canvas.getContext('2d')
    if (!context) return

    const width = containerRef.current.clientWidth
    const height = containerRef.current.clientHeight

    canvas.width = width
    canvas.height = height

    // Filter nodes based on active filters
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

    // Create force simulation
    const simulation = d3.forceSimulation(filteredNodes)
      .force('link', d3.forceLink(filteredEdges).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40))

    // Zoom behavior
    const zoom = d3.zoom<HTMLCanvasElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        setTransform(event.transform)
      })

    d3.select(canvas).call(zoom as any)

    // Render function
    const render = () => {
      context.save()
      context.clearRect(0, 0, width, height)

      context.translate(transform.x, transform.y)
      context.scale(transform.k, transform.k)

      // Draw edges
      context.strokeStyle = '#666'
      context.lineWidth = 1 / transform.k
      filteredEdges.forEach(edge => {
        const source = edge.source as GraphNode
        const target = edge.target as GraphNode
        if (!source.x || !source.y || !target.x || !target.y) return

        context.beginPath()
        context.moveTo(source.x, source.y)
        context.lineTo(target.x, target.y)
        context.stroke()
      })

      // Draw nodes
      filteredNodes.forEach(node => {
        if (!node.x || !node.y) return

        const radius = getNodeRadius(node)
        const color = getNodeColor(node)
        const opacity = node.probability ?? 1

        context.globalAlpha = opacity
        context.fillStyle = color
        context.beginPath()
        context.arc(node.x, node.y, radius, 0, 2 * Math.PI)
        context.fill()

        // Draw label if zoomed in enough
        if (transform.k > 0.8) {
          context.globalAlpha = 1
          context.fillStyle = '#fff'
          context.font = `${12 / transform.k}px sans-serif`
          context.textAlign = 'center'
          context.textBaseline = 'middle'
          context.fillText(node.label, node.x, node.y + radius + 15)
        }
      })

      context.restore()
    }

    // Update on simulation tick
    simulation.on('tick', render)

    // Initial render
    render()

    // Click handler
    const handleClick = (event: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      const x = (event.clientX - rect.left - transform.x) / transform.k
      const y = (event.clientY - rect.top - transform.y) / transform.k

      // Find clicked node
      const clicked = filteredNodes.find(node => {
        if (!node.x || !node.y) return false
        const dx = x - node.x
        const dy = y - node.y
        const radius = getNodeRadius(node)
        return Math.sqrt(dx * dx + dy * dy) < radius
      })

      setSelectedNode(clicked ?? null)
    }

    canvas.addEventListener('click', handleClick)

    return () => {
      simulation.stop()
      canvas.removeEventListener('click', handleClick)
    }
  }, [nodes, edges, filters, transform])

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

  const getNodeColor = (node: GraphNode): string => {
    const colors = {
      assumption: '#3b82f6',      // blue
      fragility: '#f97316',       // orange
      breach: '#ef4444',          // red
      counterfactual: '#a855f7'   // purple
    }
    return colors[node.type] || '#888'
  }

  return (
    <div className="network-graph-container" ref={containerRef}>
      <canvas ref={canvasRef} className="network-canvas" />
      <GraphControls />
      {selectedNode && (
        <NodeDetail
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}
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
    </div>
  )
}

export default NetworkGraph
