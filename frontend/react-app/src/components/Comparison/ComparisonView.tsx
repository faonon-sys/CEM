import './ComparisonView.css'

const ComparisonView = () => {
  return (
    <div className="comparison-view">
      <h1>Scenario Comparison</h1>
      <p className="subtitle">Compare and analyze multiple counterfactual scenarios</p>

      <div className="comparison-container">
        <div className="comparison-header">
          <button className="add-scenario-btn">+ Add Scenario</button>
          <button className="export-btn">Export to Phase 5</button>
        </div>

        <div className="comparison-grid">
          <div className="scenario-column">
            <div className="scenario-header">
              <h3>Trade War Escalation</h3>
              <span className="axis-badge">Economic Axis</span>
            </div>
            <div className="scenario-content">
              <div className="score-display">
                <label>Severity</label>
                <div className="score-bar-lg severity">
                  <div className="fill" style={{ width: '85%' }}>0.85</div>
                </div>
              </div>
              <div className="score-display">
                <label>Probability</label>
                <div className="score-bar-lg probability">
                  <div className="fill" style={{ width: '45%' }}>0.45</div>
                </div>
              </div>
              <div className="domains-list">
                <strong>Affected Domains:</strong>
                <div className="domains">
                  <span className="domain-tag">Economic</span>
                  <span className="domain-tag">Political</span>
                </div>
              </div>
            </div>
          </div>

          <div className="scenario-column">
            <div className="scenario-header">
              <h3>Regional Conflict</h3>
              <span className="axis-badge">Military Axis</span>
            </div>
            <div className="scenario-content">
              <div className="score-display">
                <label>Severity</label>
                <div className="score-bar-lg severity">
                  <div className="fill" style={{ width: '95%' }}>0.95</div>
                </div>
              </div>
              <div className="score-display">
                <label>Probability</label>
                <div className="score-bar-lg probability">
                  <div className="fill" style={{ width: '30%' }}>0.30</div>
                </div>
              </div>
              <div className="domains-list">
                <strong>Affected Domains:</strong>
                <div className="domains">
                  <span className="domain-tag">Military</span>
                  <span className="domain-tag">Political</span>
                  <span className="domain-tag">Social</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="overlap-analysis">
          <h2>Overlap Analysis</h2>
          <p>Common consequences appearing in 50%+ scenarios:</p>
          <div className="overlap-items">
            <div className="overlap-item">
              <span className="consequence">Political Instability</span>
              <span className="frequency">100%</span>
            </div>
            <div className="overlap-item">
              <span className="consequence">Economic Disruption</span>
              <span className="frequency">50%</span>
            </div>
          </div>
        </div>

        <div className="portfolio-builder">
          <h2>Portfolio Management</h2>
          <p>Drag scenarios to create portfolios for Phase 5 analysis</p>
          <div className="portfolio-zone">
            <div className="dropzone">
              <p>Drop scenarios here to create portfolio</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ComparisonView
