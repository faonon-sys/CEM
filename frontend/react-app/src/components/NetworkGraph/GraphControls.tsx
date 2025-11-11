import { useGraphState } from '../../stores/graphStore'
import './GraphControls.css'

const GraphControls = () => {
  const { filters, setFilters } = useGraphState()

  const handleNodeTypeToggle = (type: string) => {
    const newTypes = filters.nodeTypes.includes(type)
      ? filters.nodeTypes.filter(t => t !== type)
      : [...filters.nodeTypes, type]
    setFilters({ ...filters, nodeTypes: newTypes })
  }

  const handleSeverityChange = (value: number) => {
    setFilters({ ...filters, minSeverity: value })
  }

  const handleReset = () => {
    setFilters({ nodeTypes: [], minSeverity: 0 })
  }

  return (
    <div className="graph-controls">
      <div className="controls-section">
        <h3>Filters</h3>

        <div className="control-group">
          <label>Node Types:</label>
          <div className="checkbox-group">
            {['assumption', 'fragility', 'breach', 'counterfactual'].map(type => (
              <label key={type} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={filters.nodeTypes.includes(type)}
                  onChange={() => handleNodeTypeToggle(type)}
                />
                <span>{type}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="control-group">
          <label>Min Severity: {filters.minSeverity.toFixed(2)}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={filters.minSeverity}
            onChange={(e) => handleSeverityChange(parseFloat(e.target.value))}
          />
        </div>

        <button onClick={handleReset} className="reset-button">
          Reset Filters
        </button>
      </div>
    </div>
  )
}

export default GraphControls
