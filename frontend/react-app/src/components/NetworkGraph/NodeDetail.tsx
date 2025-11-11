import { GraphNode } from './NetworkGraph'
import './NodeDetail.css'

interface NodeDetailProps {
  node: GraphNode
  onClose: () => void
}

const NodeDetail = ({ node, onClose }: NodeDetailProps) => {
  return (
    <div className="node-detail">
      <div className="node-detail-header">
        <h2>{node.label}</h2>
        <button onClick={onClose} className="close-button">×</button>
      </div>

      <div className="node-detail-content">
        <div className="detail-section">
          <label>Type:</label>
          <span className="type-badge" data-type={node.type}>
            {node.type}
          </span>
        </div>

        {node.severity !== undefined && (
          <div className="detail-section">
            <label>Severity:</label>
            <div className="score-bar">
              <div
                className="score-fill severity"
                style={{ width: `${node.severity * 100}%` }}
              />
              <span className="score-value">{node.severity.toFixed(2)}</span>
            </div>
          </div>
        )}

        {node.probability !== undefined && (
          <div className="detail-section">
            <label>Probability:</label>
            <div className="score-bar">
              <div
                className="score-fill probability"
                style={{ width: `${node.probability * 100}%` }}
              />
              <span className="score-value">{node.probability.toFixed(2)}</span>
            </div>
          </div>
        )}

        {node.metadata && Object.keys(node.metadata).length > 0 && (
          <div className="detail-section">
            <label>Metadata:</label>
            <div className="metadata">
              {Object.entries(node.metadata).map(([key, value]) => (
                <div key={key} className="metadata-item">
                  <strong>{key}:</strong> {JSON.stringify(value)}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default NodeDetail
