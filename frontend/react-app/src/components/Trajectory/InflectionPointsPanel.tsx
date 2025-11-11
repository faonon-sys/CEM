/**
 * Inflection Points Panel - Sprint 5
 * Displays regime change points in the trajectory
 */
import type { InflectionPoint } from '../../services/trajectoryAPI';
import './InflectionPointsPanel.css';

interface InflectionPointsPanelProps {
  inflectionPoints: InflectionPoint[];
}

const InflectionPointsPanel = ({ inflectionPoints }: InflectionPointsPanelProps) => {
  if (inflectionPoints.length === 0) {
    return (
      <div className="empty-panel">
        <p>No inflection points detected in this trajectory</p>
      </div>
    );
  }

  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      'acceleration': '#10b981',
      'deceleration': '#f59e0b',
      'reversal': '#ef4444',
      'stabilization': '#3b82f6',
      'collapse': '#991b1b',
      'recovery': '#059669',
    };
    return colors[type.toLowerCase()] || '#6b7280';
  };

  const getTypeIcon = (type: string): string => {
    const icons: Record<string, string> = {
      'acceleration': '↗',
      'deceleration': '↘',
      'reversal': '↩',
      'stabilization': '→',
      'collapse': '⇊',
      'recovery': '⇈',
    };
    return icons[type.toLowerCase()] || '•';
  };

  return (
    <div className="inflection-points-panel">
      <div className="inflection-points-list">
        {inflectionPoints.map((ip, index) => (
          <div key={ip.id || index} className="inflection-point-card">
            <div className="ip-header">
              <div className="ip-time">
                <strong>T+{ip.timestamp.toFixed(2)} years</strong>
                <span className="ip-index">#{ip.index}</span>
              </div>
              <div
                className="ip-type"
                style={{
                  backgroundColor: getTypeColor(ip.type),
                  color: 'white',
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '11px',
                  fontWeight: 600,
                }}
              >
                {getTypeIcon(ip.type)} {ip.type.toUpperCase()}
              </div>
            </div>

            <div className="ip-content">
              <div className="ip-magnitude">
                <strong>Magnitude:</strong>{' '}
                <span
                  style={{
                    color:
                      ip.magnitude > 0.7
                        ? '#ef4444'
                        : ip.magnitude > 0.4
                        ? '#f59e0b'
                        : '#10b981',
                    fontWeight: 600,
                  }}
                >
                  {(ip.magnitude * 100).toFixed(1)}%
                </span>
              </div>

              <div className="ip-trigger">
                <strong>Triggering Condition:</strong>
                <p>{ip.triggering_condition}</p>
              </div>

              <div className="ip-trends">
                <div className="trend-item">
                  <span className="trend-label">Pre-inflection Trend:</span>
                  <span
                    className={`trend-value ${
                      ip.pre_inflection_trend > 0 ? 'positive' : 'negative'
                    }`}
                  >
                    {ip.pre_inflection_trend > 0 ? '+' : ''}
                    {(ip.pre_inflection_trend * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="trend-item">
                  <span className="trend-label">Post-inflection Trend:</span>
                  <span
                    className={`trend-value ${
                      ip.post_inflection_trend > 0 ? 'positive' : 'negative'
                    }`}
                  >
                    {ip.post_inflection_trend > 0 ? '+' : ''}
                    {(ip.post_inflection_trend * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {ip.state_change && Object.keys(ip.state_change).length > 0 && (
                <div className="ip-state-changes">
                  <strong>State Changes:</strong>
                  <ul>
                    {Object.entries(ip.state_change).map(([key, value]) => (
                      <li key={key}>
                        <span className="state-key">{key}:</span>{' '}
                        <span className="state-value">{JSON.stringify(value)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InflectionPointsPanel;
