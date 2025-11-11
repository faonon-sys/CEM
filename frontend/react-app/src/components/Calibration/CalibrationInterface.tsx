import { useState, useEffect } from 'react'
import './CalibrationInterface.css'

interface ScoreData {
  counterfactual_id: string
  original_severity: number
  original_probability: number
  adjusted_severity: number
  adjusted_probability: number
  factors: {
    severity: Record<string, number>
    probability: Record<string, number>
  }
  sensitivity: {
    severity: Record<string, number>
    probability: Record<string, number>
  }
}

interface CalibrationStats {
  total_adjustments: number
  severity_bias: {
    mean_adjustment: number
    tendency: string
  }
  probability_bias: {
    mean_adjustment: number
    tendency: string
  }
}

const CalibrationInterface = () => {
  const [scenarios, setScenarios] = useState<any[]>([])
  const [selectedScenario, setSelectedScenario] = useState<string>('')
  const [scoreData, setScoreData] = useState<ScoreData | null>(null)
  const [adjustedSeverity, setAdjustedSeverity] = useState<number>(0)
  const [adjustedProbability, setAdjustedProbability] = useState<number>(0)
  const [rationale, setRationale] = useState<string>('')
  const [calibrationStats, setCalibrationStats] = useState<CalibrationStats | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Load scenarios with counterfactuals
    loadScenarios()
    loadCalibrationStats()
  }, [])

  useEffect(() => {
    if (selectedScenario) {
      loadScenarioScores(selectedScenario)
    }
  }, [selectedScenario])

  const loadScenarios = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await axios.get('/api/v1/scenarios')
      // setScenarios(response.data)

      // Mock data for now
      setScenarios([
        { id: '1', name: 'Trade War Escalation' },
        { id: '2', name: 'Regional Conflict' },
        { id: '3', name: 'Supply Chain Disruption' }
      ])
    } catch (error) {
      console.error('Failed to load scenarios:', error)
    }
  }

  const loadScenarioScores = async (scenarioId: string) => {
    try {
      setLoading(true)
      // TODO: Replace with actual API call
      // const response = await axios.get(`/api/v1/scoring/counterfactuals/${scenarioId}`)

      // Mock data
      const mockData: ScoreData = {
        counterfactual_id: scenarioId,
        original_severity: 0.85,
        original_probability: 0.45,
        adjusted_severity: 0.85,
        adjusted_probability: 0.45,
        factors: {
          severity: {
            cascade_depth: 0.21,
            breadth_of_impact: 0.19,
            deviation_magnitude: 0.25,
            irreversibility: 0.20
          },
          probability: {
            fragility_strength: 0.16,
            historical_precedent: 0.14,
            dependency_failures: 0.09,
            time_horizon: 0.06
          }
        },
        sensitivity: {
          severity: {
            cascade_depth: 0.30,
            breadth_of_impact: 0.25,
            deviation_magnitude: 0.25,
            irreversibility: 0.20
          },
          probability: {
            fragility_strength: 0.35,
            historical_precedent: 0.30,
            dependency_failures: 0.20,
            time_horizon: 0.15
          }
        }
      }

      setScoreData(mockData)
      setAdjustedSeverity(mockData.original_severity)
      setAdjustedProbability(mockData.original_probability)
    } catch (error) {
      console.error('Failed to load scenario scores:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadCalibrationStats = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await axios.get('/api/v1/scoring/calibration/stats')

      // Mock data
      setCalibrationStats({
        total_adjustments: 47,
        severity_bias: {
          mean_adjustment: -0.08,
          tendency: 'underestimate'
        },
        probability_bias: {
          mean_adjustment: 0.05,
          tendency: 'overestimate'
        }
      })
    } catch (error) {
      console.error('Failed to load calibration stats:', error)
    }
  }

  const handleSaveCalibration = async () => {
    if (!scoreData) return

    try {
      setLoading(true)

      const adjustmentData = {
        counterfactual_id: scoreData.counterfactual_id,
        original_severity: scoreData.original_severity,
        adjusted_severity: adjustedSeverity,
        original_probability: scoreData.original_probability,
        adjusted_probability: adjustedProbability,
        expert_rationale: rationale
      }

      // TODO: Replace with actual API call
      // await axios.post('/api/v1/scoring/calibration/adjust', adjustmentData)

      console.log('Saving calibration:', adjustmentData)
      alert('Calibration saved successfully!')

      // Reload stats
      await loadCalibrationStats()
    } catch (error) {
      console.error('Failed to save calibration:', error)
      alert('Failed to save calibration')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    if (scoreData) {
      setAdjustedSeverity(scoreData.original_severity)
      setAdjustedProbability(scoreData.original_probability)
      setRationale('')
    }
  }

  const formatFactorName = (name: string): string => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <div className="calibration-interface">
      <h1>Score Calibration</h1>
      <p className="subtitle">Expert adjustment of algorithmic scores</p>

      <div className="calibration-container">
        <div className="scenario-selector">
          <label>Select Scenario:</label>
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            disabled={loading}
          >
            <option value="">-- Select a scenario --</option>
            {scenarios.map(scenario => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.name}
              </option>
            ))}
          </select>
        </div>

        {loading && <div className="loading">Loading...</div>}

        {scoreData && !loading && (
          <>
            <div className="calibration-grid">
              <div className="score-adjustment-card">
                <h2>Severity Score</h2>
                <div className="current-score">
                  <span className="label">Algorithmic Score:</span>
                  <span className="value">{scoreData.original_severity.toFixed(2)}</span>
                </div>
                <div className="adjustment-controls">
                  <label>Adjusted Score:</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={adjustedSeverity}
                    onChange={(e) => setAdjustedSeverity(parseFloat(e.target.value))}
                  />
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={adjustedSeverity}
                    onChange={(e) => setAdjustedSeverity(parseFloat(e.target.value))}
                  />
                </div>
                <div className="factor-breakdown">
                  <h3>Factor Contributions:</h3>
                  <div className="factors">
                    {Object.entries(scoreData.factors.severity).map(([key, value]) => (
                      <div key={key} className="factor">
                        <span>{formatFactorName(key)}:</span>
                        <span>{value.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="sensitivity-display">
                  <h4>Sensitivity (Most Influential):</h4>
                  <div className="sensitivity-factors">
                    {Object.entries(scoreData.sensitivity.severity)
                      .sort((a, b) => b[1] - a[1])
                      .slice(0, 3)
                      .map(([key, value]) => (
                        <div key={key} className="sensitivity-item">
                          <span>{formatFactorName(key)}</span>
                          <div className="sensitivity-bar">
                            <div
                              className="sensitivity-fill"
                              style={{ width: `${value * 100}%` }}
                            />
                          </div>
                          <span>{value.toFixed(2)}</span>
                        </div>
                      ))}
                  </div>
                </div>
              </div>

              <div className="score-adjustment-card">
                <h2>Probability Score</h2>
                <div className="current-score">
                  <span className="label">Algorithmic Score:</span>
                  <span className="value">{scoreData.original_probability.toFixed(2)}</span>
                </div>
                <div className="adjustment-controls">
                  <label>Adjusted Score:</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={adjustedProbability}
                    onChange={(e) => setAdjustedProbability(parseFloat(e.target.value))}
                  />
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={adjustedProbability}
                    onChange={(e) => setAdjustedProbability(parseFloat(e.target.value))}
                  />
                </div>
                <div className="factor-breakdown">
                  <h3>Factor Contributions:</h3>
                  <div className="factors">
                    {Object.entries(scoreData.factors.probability).map(([key, value]) => (
                      <div key={key} className="factor">
                        <span>{formatFactorName(key)}:</span>
                        <span>{value.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="sensitivity-display">
                  <h4>Sensitivity (Most Influential):</h4>
                  <div className="sensitivity-factors">
                    {Object.entries(scoreData.sensitivity.probability)
                      .sort((a, b) => b[1] - a[1])
                      .slice(0, 3)
                      .map(([key, value]) => (
                        <div key={key} className="sensitivity-item">
                          <span>{formatFactorName(key)}</span>
                          <div className="sensitivity-bar">
                            <div
                              className="sensitivity-fill"
                              style={{ width: `${value * 100}%` }}
                            />
                          </div>
                          <span>{value.toFixed(2)}</span>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="delta-summary">
              <h3>Adjustment Summary</h3>
              <div className="deltas">
                <div className="delta-item">
                  <span>Severity Delta:</span>
                  <span className={adjustedSeverity - scoreData.original_severity > 0 ? 'positive' : 'negative'}>
                    {(adjustedSeverity - scoreData.original_severity >= 0 ? '+' : '')}
                    {(adjustedSeverity - scoreData.original_severity).toFixed(3)}
                  </span>
                </div>
                <div className="delta-item">
                  <span>Probability Delta:</span>
                  <span className={adjustedProbability - scoreData.original_probability > 0 ? 'positive' : 'negative'}>
                    {(adjustedProbability - scoreData.original_probability >= 0 ? '+' : '')}
                    {(adjustedProbability - scoreData.original_probability).toFixed(3)}
                  </span>
                </div>
              </div>
            </div>

            <div className="rationale-section">
              <label>Adjustment Rationale (Required for learning):</label>
              <textarea
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
                placeholder="Explain why you adjusted these scores... (e.g., 'Severity underestimated due to regulatory cascade effects not captured by algorithm')"
                rows={4}
              />
            </div>

            <div className="calibration-actions">
              <button
                className="save-btn"
                onClick={handleSaveCalibration}
                disabled={loading || !rationale.trim()}
              >
                {loading ? 'Saving...' : 'Save Calibration'}
              </button>
              <button
                className="reset-btn"
                onClick={handleReset}
                disabled={loading}
              >
                Reset to Original
              </button>
            </div>
          </>
        )}

        {calibrationStats && (
          <div className="learning-stats">
            <h2>Calibration Statistics</h2>
            <p>Algorithm learning from expert adjustments</p>
            <div className="stats-display">
              <div className="stat">
                <span className="stat-label">Total Adjustments:</span>
                <span className="stat-value">{calibrationStats.total_adjustments}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Severity Bias:</span>
                <span className="stat-value">
                  {calibrationStats.severity_bias.tendency.charAt(0).toUpperCase() + calibrationStats.severity_bias.tendency.slice(1)} by {Math.abs(calibrationStats.severity_bias.mean_adjustment).toFixed(2)}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Probability Bias:</span>
                <span className="stat-value">
                  {calibrationStats.probability_bias.tendency.charAt(0).toUpperCase() + calibrationStats.probability_bias.tendency.slice(1)} by {Math.abs(calibrationStats.probability_bias.mean_adjustment).toFixed(2)}
                </span>
              </div>
            </div>
            <div className="recommendation">
              <h3>Recommendation:</h3>
              <p>
                {calibrationStats.severity_bias.tendency === 'underestimate' &&
                  'Consider increasing severity factor weights to better match expert judgment.'}
                {calibrationStats.severity_bias.tendency === 'overestimate' &&
                  'Consider decreasing severity factor weights to better match expert judgment.'}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CalibrationInterface
