/**
 * Decision Points Panel - Sprint 5
 * Displays critical decision points with intervention capabilities
 */
import { useState } from 'react';
import { useTestIntervention } from '../../hooks/useTrajectory';
import type { DecisionPoint } from '../../services/trajectoryAPI';
import './DecisionPointsPanel.css';

interface DecisionPointsPanelProps {
  decisionPoints: DecisionPoint[];
  trajectoryId: string;
}

const DecisionPointsPanel = ({ decisionPoints, trajectoryId }: DecisionPointsPanelProps) => {
  const [selectedDP, setSelectedDP] = useState<DecisionPoint | null>(null);
  const [showInterventionForm, setShowInterventionForm] = useState(false);

  const testIntervention = useTestIntervention(trajectoryId);

  const handleIntervention = async (dp: DecisionPoint) => {
    setSelectedDP(dp);
    setShowInterventionForm(true);
  };

  const handleSubmitIntervention = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedDP) return;

    const formData = new FormData(e.currentTarget);

    try {
      await testIntervention.mutateAsync({
        decision_point_index: selectedDP.index,
        intervention_type: formData.get('intervention_type') as any,
        intervention_name: formData.get('intervention_name') as string,
        intervention_description: formData.get('intervention_description') as string,
        impact_modifier: parseFloat(formData.get('impact_modifier') as string),
        estimated_cost: formData.get('estimated_cost') as any,
        implementation_timeframe: formData.get('implementation_timeframe') as string,
      });

      setShowInterventionForm(false);
      setSelectedDP(null);
    } catch (error) {
      console.error('Intervention test failed:', error);
    }
  };

  if (decisionPoints.length === 0) {
    return (
      <div className="empty-panel">
        <p>No decision points detected in this trajectory</p>
      </div>
    );
  }

  return (
    <div className="decision-points-panel">
      <div className="decision-points-list">
        {decisionPoints.map((dp, index) => (
          <div key={dp.id || index} className="decision-point-card">
            <div className="dp-header">
              <div className="dp-time">
                <strong>T+{dp.timestamp.toFixed(2)} years</strong>
                <span className="dp-index">#{dp.index}</span>
              </div>
              <div className="dp-criticality">
                <div
                  className="criticality-bar"
                  style={{
                    width: `${dp.criticality_score * 100}%`,
                    backgroundColor:
                      dp.criticality_score > 0.7
                        ? '#ef4444'
                        : dp.criticality_score > 0.4
                        ? '#f59e0b'
                        : '#10b981',
                  }}
                />
                <span className="criticality-label">
                  Criticality: {(dp.criticality_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <div className="dp-content">
              <p className="dp-description">{dp.description}</p>

              <div className="dp-details">
                <div className="detail-item">
                  <strong>Intervention Window:</strong> {dp.intervention_window} months
                </div>
                <div className="detail-item">
                  <strong>Alternative Pathways:</strong> {dp.alternative_pathways.length}
                </div>
              </div>

              {dp.recommended_action && (
                <div className="dp-recommendation">
                  <strong>Recommended Action:</strong> {dp.recommended_action}
                </div>
              )}

              <div className="dp-pathways">
                <strong>Pathways:</strong>
                <ul>
                  {dp.alternative_pathways.slice(0, 3).map((pathway, idx) => (
                    <li key={idx}>
                      {pathway.description} (p={pathway.probability.toFixed(2)})
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="dp-actions">
              <button
                className="test-intervention-btn"
                onClick={() => handleIntervention(dp)}
              >
                Test Intervention
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Intervention Form Modal */}
      {showInterventionForm && selectedDP && (
        <div className="modal-overlay" onClick={() => setShowInterventionForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Test Intervention at Decision Point #{selectedDP.index}</h3>
            <form onSubmit={handleSubmitIntervention}>
              <div className="form-group">
                <label>Intervention Type:</label>
                <select name="intervention_type" required>
                  <option value="mitigation">Mitigation</option>
                  <option value="acceleration">Acceleration</option>
                  <option value="deflection">Deflection</option>
                  <option value="containment">Containment</option>
                </select>
              </div>

              <div className="form-group">
                <label>Intervention Name:</label>
                <input type="text" name="intervention_name" required />
              </div>

              <div className="form-group">
                <label>Description:</label>
                <textarea name="intervention_description" rows={3} required />
              </div>

              <div className="form-group">
                <label>Impact Modifier (0-2):</label>
                <input
                  type="number"
                  name="impact_modifier"
                  min="0"
                  max="2"
                  step="0.1"
                  defaultValue="1.0"
                  required
                />
              </div>

              <div className="form-group">
                <label>Estimated Cost:</label>
                <select name="estimated_cost">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="very_high">Very High</option>
                </select>
              </div>

              <div className="form-group">
                <label>Implementation Timeframe:</label>
                <input type="text" name="implementation_timeframe" defaultValue="short-term" />
              </div>

              <div className="form-actions">
                <button type="submit" className="submit-btn" disabled={testIntervention.isPending}>
                  {testIntervention.isPending ? 'Testing...' : 'Test Intervention'}
                </button>
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowInterventionForm(false)}
                >
                  Cancel
                </button>
              </div>

              {testIntervention.isError && (
                <div className="error-message">
                  Error: {(testIntervention.error as Error).message}
                </div>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DecisionPointsPanel;
