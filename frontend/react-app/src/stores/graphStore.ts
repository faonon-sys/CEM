import { create } from 'zustand'
import { GraphNode, GraphEdge } from '../components/NetworkGraph/NetworkGraph'

interface GraphFilters {
  nodeTypes: string[]
  minSeverity: number
}

interface GraphState {
  nodes: GraphNode[]
  edges: GraphEdge[]
  filters: GraphFilters
  setNodes: (nodes: GraphNode[]) => void
  setEdges: (edges: GraphEdge[]) => void
  setFilters: (filters: GraphFilters) => void
  loadSampleData: () => void
  persistLayout: (scenarioId: string) => void
  loadLayout: (scenarioId: string) => void
}

export const useGraphState = create<GraphState>((set, get) => ({
  nodes: [],
  edges: [],
  filters: {
    nodeTypes: [],
    minSeverity: 0
  },

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setFilters: (filters) => set({ filters }),

  loadSampleData: () => {
    // Sample data for demonstration
    const sampleNodes: GraphNode[] = [
      {
        id: 'assumption-1',
        type: 'assumption',
        label: 'Regional Stability',
        severity: 0.3,
        probability: 0.7,
        metadata: { category: 'geopolitical', confidence: 0.8 }
      },
      {
        id: 'fragility-1',
        type: 'fragility',
        label: 'Economic Dependency',
        severity: 0.6,
        probability: 0.5,
        metadata: { evidence_strength: 0.7 }
      },
      {
        id: 'breach-1',
        type: 'breach',
        label: 'Supply Chain Disruption',
        severity: 0.8,
        probability: 0.4,
        metadata: { trigger_type: 'external_shock' }
      },
      {
        id: 'counterfactual-1',
        type: 'counterfactual',
        label: 'Trade War Escalation',
        severity: 0.85,
        probability: 0.45,
        metadata: { axis: 'economic_axis', domains: ['economic', 'political'] }
      },
      {
        id: 'counterfactual-2',
        type: 'counterfactual',
        label: 'Regional Conflict',
        severity: 0.95,
        probability: 0.3,
        metadata: { axis: 'military_axis', domains: ['military', 'political', 'social'] }
      }
    ]

    const sampleEdges: GraphEdge[] = [
      {
        source: 'assumption-1',
        target: 'fragility-1',
        type: 'dependency',
        weight: 1
      },
      {
        source: 'fragility-1',
        target: 'breach-1',
        type: 'dependency',
        weight: 1
      },
      {
        source: 'breach-1',
        target: 'counterfactual-1',
        type: 'consequence',
        weight: 0.8
      },
      {
        source: 'breach-1',
        target: 'counterfactual-2',
        type: 'consequence',
        weight: 0.6
      }
    ]

    set({ nodes: sampleNodes, edges: sampleEdges })
  },

  persistLayout: (scenarioId: string) => {
    const { nodes } = get()
    const positions = nodes.map(n => ({ id: n.id, x: n.x, y: n.y }))
    localStorage.setItem(`graph-layout-${scenarioId}`, JSON.stringify(positions))
  },

  loadLayout: (scenarioId: string) => {
    const saved = localStorage.getItem(`graph-layout-${scenarioId}`)
    if (!saved) return

    const positions = JSON.parse(saved)
    const { nodes } = get()

    const updatedNodes = nodes.map(node => {
      const savedPos = positions.find((p: any) => p.id === node.id)
      if (savedPos) {
        return { ...node, x: savedPos.x, y: savedPos.y }
      }
      return node
    })

    set({ nodes: updatedNodes })
  }
}))
