/**
 * Intervention Builder Component - Sprint 5 Task 6
 * Interactive tool for testing intervention scenarios at decision points
 */
import { useState } from 'react';
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, ReferenceLine } from 'recharts';
import trajectoryAPI, { type Trajectory, type DecisionPoint, type InterventionRequest, type InterventionResponse } from '../../services/trajectoryAPI';
import './InterventionBuilder.css';

interface InterventionBuilderProps {
  trajectory: Trajectory;
  decisionPoints: DecisionPoint[];
  onInterventionTested?: (intervention: InterventionResponse) => void;
}

const InterventionBuilder = ({
  trajectory,
  decisionPoints,
  onInterventionTested,
}: InterventionBuilderProps) => {
  const [selectedDecisionPointIndex, setSelectedDecisionPointIndex] = useState<number | null>(
    decisionPoints[0]?.index || null
  );
  const [interventionType, setInterventionType] = useState<'mitigation' | 'acceleration' | 'deflection' | 'containment'>('mitigation');
  const [interventionName, setInterventionName] = useState('');
  const [interventionDescription, setInterventionDescription] = useState('');
  const [impactModifier, setImpactModifier] = useState(0.5);
  const [estimatedCost, setEstimatedCost] = useState<'low' | 'medium' | 'high' | 'very_high'>('medium');
  const [implementationTimeframe, setImplementationTimeframe] = useState('short-term');
  const [isTestingIntervention, setIsTestingIntervention] = useState(false);
  const [testedInterventions, setTestedInterventions] = useState<InterventionResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  const selectedDecisionPoint = decisionPoints.find(
    (dp) => dp.index === selectedDecisionPointIndex
  );

  const handleTestIntervention = async () => {
    if (selectedDecisionPointIndex === null || !interventionName.trim()) {
      setError('Please select a decision point and provide an intervention name');
      return;
    }

    setIsTestingIntervention(true);
    setError(null);

    try {
      const request: InterventionRequest = {
        decision_point_index: selectedDecisionPointIndex,
        intervention_type: interventionType,
        intervention_name: interventionName,
        intervention_description: interventionDescription || interventionName,
        impact_modifier: impactModifier,
        estimated_cost: estimatedCost,
        implementation_timeframe: implementationTimeframe,
      };

      const response = await trajectoryAPI.testIntervention(trajectory.trajectory_id, request);
      setTestedInterventions([...testedInterventions, response]);

      if (onInterventionTested) {
        onInterventionTested(response);
      }

      // Reset form
      setInterventionName('');
      setInterventionDescription('');
      setImpactModifier(0.5);

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to test intervention');
      console.error('Intervention test failed:', err);
    } finally {
      setIsTestingIntervention(false);
    }
  };

  // Prepare chart data with baseline and interventions
  const chartData = trajectory.baseline_trajectory.map((point, index) => {
    const dataPoint: any = {
      timestamp: point.timestamp,
      timestampLabel: `T+${point.timestamp.toFixed(1)}y`,
      baseline: point.state_variables.primary_metric,
      index,
    };

    // Add intervention trajectories
    testedInterventions.forEach((intervention, idx) => {
      const interventionPoint = intervention.projected_trajectory[index];
      if (interventionPoint) {
        dataPoint[`intervention_${idx}`] = interventionPoint.state_variables.primary_metric;
      }
    });

    return dataPoint;
  });

  const INTERVENTION_COLORS = ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="intervention-builder">
      <div className="builder-header">
        <h2>Intervention Builder</h2>
        <p className="subtitle">Test strategic interventions at critical decision points</p>
      </div>

      <div className="builder-content">
        {/* Configuration Panel */}
        <div className="config-panel">
          <h3>Configure Intervention</h3>

          {/* Decision Point Selection */}
          <div className="form-group">
            <label>Decision Point</label>
            <select
              value={selectedDecisionPointIndex ?? ''}
              onChange={(e) => setSelectedDecisionPointIndex(parseInt(e.target.value))}
              className="form-select"
            >
              <option value="">Select decision point...</option>
              {decisionPoints.map((dp) => (
                <option key={dp.index} value={dp.index}>
                  T+{dp.timestamp.toFixed(1)}y - {dp.description.substring(0, 50)}
                  {dp.description.length > 50 ? '...' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Decision Point Details */}
          {selectedDecisionPoint && (
            <div className="decision-point-detail">
              <div className="detail-row">
                <span className="detail-label">Criticality:</span>
                <span className="detail-value">
                  <div className="criticality-bar">
                    <div
                      className="criticality-fill"
                      style={{ width: `${selectedDecisionPoint.criticality_score * 100}%` }}
                    />
                  </div>
                  {(selectedDecisionPoint.criticality_score * 100).toFixed(0)}%
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Intervention Window:</span>
                <span className="detail-value">
                  {selectedDecisionPoint.intervention_window.toFixed(1)} months
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Recommended Action:</span>
                <span className="detail-value">{selectedDecisionPoint.recommended_action}</span>
              </div>
            </div>
          )}

          {/* Intervention Type */}
          <div className="form-group">
            <label>Intervention Type</label>
            <div className="button-group">
              {(['mitigation', 'acceleration', 'deflection', 'containment'] as const).map((type) => (
                <button
                  key={type}
                  className={`type-button ${interventionType === type ? 'active' : ''}`}
                  onClick={() => setInterventionType(type)}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Intervention Name */}
          <div className="form-group">
            <label>Intervention Name *</label>
            <input
              type="text"
              value={interventionName}
              onChange={(e) => setInterventionName(e.target.value)}
              placeholder="e.g., Policy Reform Package"
              className="form-input"
            />
          </div>

          {/* Intervention Description */}
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={interventionDescription}
              onChange={(e) => setInterventionDescription(e.target.value)}
              placeholder="Detailed description of intervention measures..."
              className="form-textarea"
              rows={3}
            />
          </div>

          {/* Impact Modifier */}
          <div className="form-group">
            <label>
              Impact Modifier: {impactModifier.toFixed(2)}x
              <span className="help-text">
                {impactModifier < 0.5
                  ? 'Strong mitigation'
                  : impactModifier < 1.0
                  ? 'Moderate mitigation'
                  : impactModifier === 1.0
                  ? 'No change'
                  : 'Acceleration'}
              </span>
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={impactModifier}
              onChange={(e) => setImpactModifier(parseFloat(e.target.value))}
              className="form-range"
            />
            <div className="range-labels">
              <span>0.0 (Strong)</span>
              <span>1.0 (None)</span>
              <span>2.0 (Acceleration)</span>
            </div>
          </div>

          {/* Estimated Cost */}
          <div className="form-group">
            <label>Estimated Cost</label>
            <div className="button-group">
              {(['low', 'medium', 'high', 'very_high'] as const).map((cost) => (
                <button
                  key={cost}
                  className={`cost-button ${estimatedCost === cost ? 'active' : ''}`}
                  onClick={() => setEstimatedCost(cost)}
                >
                  {cost.replace('_', ' ').toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Implementation Timeframe */}
          <div className="form-group">
            <label>Implementation Timeframe</label>
            <select
              value={implementationTimeframe}
              onChange={(e) => setImplementationTimeframe(e.target.value)}
              className="form-select"
            >
              <option value="immediate">Immediate (0-3 months)</option>
              <option value="short-term">Short-term (3-12 months)</option>
              <option value="medium-term">Medium-term (1-3 years)</option>
              <option value="long-term">Long-term (3+ years)</option>
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Test Button */}
          <button
            onClick={handleTestIntervention}
            disabled={isTestingIntervention || !selectedDecisionPointIndex || !interventionName.trim()}
            className="test-button"
          >
            {isTestingIntervention ? 'Testing Intervention...' : 'Test Intervention'}
          </button>
        </div>

        {/* Visualization Panel */}
        <div className="visualization-panel">
          <h3>Impact Projection</h3>

          <div className="chart-container" style={{ height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 20, right: 40, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis
                  dataKey="timestamp"
                  label={{
                    value: 'Time (years)',
                    position: 'insideBottom',
                    offset: -10,
                    style: { fontSize: '13px', fontWeight: 600 },
                  }}
                  tickFormatter={(value) => `+${value.toFixed(1)}`}
                  stroke="#666"
                />
                <YAxis
                  label={{
                    value: 'Primary Outcome Metric',
                    angle: -90,
                    position: 'insideLeft',
                    style: { fontSize: '13px', fontWeight: 600 },
                  }}
                  domain={[0, 1]}
                  stroke="#666"
                />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} iconType="line" />

                {/* Baseline trajectory */}
                <Line
                  type="monotone"
                  dataKey="baseline"
                  stroke="#6b7280"
                  strokeWidth={2}
                  strokeDasharray="3 3"
                  dot={false}
                  name="Baseline (No Intervention)"
                />

                {/* Tested interventions */}
                {testedInterventions.map((intervention, idx) => (
                  <Line
                    key={`intervention_${idx}`}
                    type="monotone"
                    dataKey={`intervention_${idx}`}
                    stroke={INTERVENTION_COLORS[idx % INTERVENTION_COLORS.length]}
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    name={`Intervention ${idx + 1}`}
                  />
                ))}

                {/* Decision point marker */}
                {selectedDecisionPoint && (
                  <ReferenceLine
                    x={selectedDecisionPoint.timestamp}
                    stroke="#ef4444"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    label={{ value: 'Intervention Point', position: 'top', fill: '#ef4444' }}
                  />
                )}
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Tested Interventions List */}
          {testedInterventions.length > 0 && (
            <div className="interventions-list">
              <h4>Tested Interventions ({testedInterventions.length})</h4>
              {testedInterventions.map((intervention, idx) => (
                <div key={idx} className="intervention-card">
                  <div className="intervention-header">
                    <div
                      className="intervention-color-indicator"
                      style={{ backgroundColor: INTERVENTION_COLORS[idx % INTERVENTION_COLORS.length] }}
                    />
                    <h5>Intervention {idx + 1}</h5>
                  </div>
                  <div className="intervention-body">
                    <div className="intervention-metric">
                      <span className="metric-label">Expected Value:</span>
                      <span className="metric-value">{intervention.expected_value.toFixed(3)}</span>
                    </div>
                    {intervention.roi_estimate !== null && (
                      <div className="intervention-metric">
                        <span className="metric-label">ROI Estimate:</span>
                        <span
                          className={`metric-value ${
                            intervention.roi_estimate > 0 ? 'positive' : 'negative'
                          }`}
                        >
                          {intervention.roi_estimate > 0 ? '+' : ''}
                          {intervention.roi_estimate.toFixed(1)}%
                        </span>
                      </div>
                    )}
                    <div className="intervention-metric">
                      <span className="metric-label">Time to Impact:</span>
                      <span className="metric-value">
                        {intervention.time_to_impact_months.toFixed(1)} months
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterventionBuilder;
