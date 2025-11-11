import './Dashboard.css'

const Dashboard = () => {
  return (
    <div className="dashboard">
      <h1>Heat Maps Dashboard</h1>
      <p className="subtitle">Risk distribution across strategic dimensions</p>

      <div className="dashboard-grid">
        <div className="heatmap-card">
          <h2>Axes × Domains</h2>
          <div className="heatmap-placeholder">
            <p>Heat map showing severity across strategic axes and impact domains</p>
            <div className="heatmap-legend">
              <span className="legend-low">Low</span>
              <span className="legend-mid">Medium</span>
              <span className="legend-high">High</span>
            </div>
          </div>
        </div>

        <div className="heatmap-card">
          <h2>Axes × Time Horizon</h2>
          <div className="heatmap-placeholder">
            <p>Temporal distribution of counterfactual scenarios</p>
          </div>
        </div>

        <div className="heatmap-card">
          <h2>Domains × Severity</h2>
          <div className="heatmap-placeholder">
            <p>Impact severity by domain</p>
          </div>
        </div>

        <div className="summary-card">
          <h2>Summary Statistics</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-value">42</span>
              <span className="stat-label">Total Counterfactuals</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">0.73</span>
              <span className="stat-label">Avg Severity</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">Economic</span>
              <span className="stat-label">Highest Risk Domain</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">Short-term</span>
              <span className="stat-label">Most Likely Timeframe</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
