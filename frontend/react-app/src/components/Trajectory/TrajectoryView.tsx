/**
 * Trajectory Visualization Component - Sprint 5
 * Main view for Phase 5 Strategic Outcome Projection
 */
import { useState } from 'react';
import { useTrajectory, useDecisionPoints, useInflectionPoints } from '../../hooks/useTrajectory';
import TrajectoryChart from './TrajectoryChart';
import DecisionPointsPanel from './DecisionPointsPanel';
import InflectionPointsPanel from './InflectionPointsPanel';
import './TrajectoryView.css';

interface TrajectoryViewProps {
  trajectoryId?: string;
}

const TrajectoryView = ({ trajectoryId: propTrajectoryId }: TrajectoryViewProps) => {
  const [selectedTrajectoryId] = useState(propTrajectoryId || '');
  const [selectedMetric, setSelectedMetric] = useState<string>('primary_metric');
  const [showConfidenceBounds, setShowConfidenceBounds] = useState(true);
  const [showAlternativeBranches, setShowAlternativeBranches] = useState(true);

  // Fetch trajectory data
  const {
    data: trajectory,
    isLoading: trajectoryLoading,
    error: trajectoryError,
  } = useTrajectory(selectedTrajectoryId, !!selectedTrajectoryId);

  const {
    data: decisionPointsData,
    isLoading: dpLoading,
  } = useDecisionPoints(selectedTrajectoryId, !!selectedTrajectoryId);

  const {
    data: inflectionPointsData,
    isLoading: ipLoading,
  } = useInflectionPoints(selectedTrajectoryId, !!selectedTrajectoryId);

  const metrics = [
    { key: 'primary_metric', label: 'Primary Outcome' },
    { key: 'gdp_impact', label: 'GDP Impact' },
    { key: 'stability_index', label: 'Political Stability' },
    { key: 'resource_levels', label: 'Resource Levels' },
    { key: 'operational_capability', label: 'Operational Capability' },
    { key: 'social_cohesion', label: 'Social Cohesion' },
  ];

  if (!selectedTrajectoryId) {
    return (
      <div className="trajectory-view">
        <div className="empty-state">
          <h2>No Trajectory Selected</h2>
          <p>Please select or project a trajectory to visualize strategic outcomes</p>
        </div>
      </div>
    );
  }

  if (trajectoryLoading || dpLoading || ipLoading) {
    return (
      <div className="trajectory-view">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading trajectory projection...</p>
        </div>
      </div>
    );
  }

  if (trajectoryError) {
    return (
      <div className="trajectory-view">
        <div className="error-state">
          <h2>Error Loading Trajectory</h2>
          <p>{(trajectoryError as Error).message}</p>
        </div>
      </div>
    );
  }

  if (!trajectory) {
    return null;
  }

  const decisionPoints = (decisionPointsData as any)?.decision_points || [];
  const inflectionPoints = (inflectionPointsData as any)?.inflection_points || [];

  return (
    <div className="trajectory-view">
      <header className="trajectory-header">
        <div className="trajectory-info">
          <h1>Strategic Outcome Trajectory</h1>
          <div className="trajectory-meta">
            <span className="meta-item">
              <strong>Time Horizon:</strong> {(trajectory as any).time_horizon} years
            </span>
            <span className="meta-item">
              <strong>Granularity:</strong> {(trajectory as any).granularity}
            </span>
            <span className="meta-item">
              <strong>Decision Points:</strong> {decisionPoints.length}
            </span>
            <span className="meta-item">
              <strong>Inflection Points:</strong> {inflectionPoints.length}
            </span>
          </div>
        </div>

        <div className="trajectory-controls">
          <div className="metric-selector">
            <label>Metric:</label>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
            >
              {metrics.map((m) => (
                <option key={m.key} value={m.key}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          <div className="view-options">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={showConfidenceBounds}
                onChange={(e) => setShowConfidenceBounds(e.target.checked)}
              />
              Show Confidence Bounds
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={showAlternativeBranches}
                onChange={(e) => setShowAlternativeBranches(e.target.checked)}
              />
              Show Alternative Branches
            </label>
          </div>
        </div>
      </header>

      <div className="trajectory-content">
        <div className="chart-section">
          <TrajectoryChart
            trajectory={trajectory as any}
            selectedMetric={selectedMetric}
            showConfidenceBounds={showConfidenceBounds}
            showAlternativeBranches={showAlternativeBranches}
            decisionPoints={decisionPoints}
            inflectionPoints={inflectionPoints}
          />
        </div>

        <div className="panels-section">
          <div className="panel">
            <h2>Decision Points</h2>
            <DecisionPointsPanel
              decisionPoints={decisionPoints}
              trajectoryId={selectedTrajectoryId}
            />
          </div>

          <div className="panel">
            <h2>Inflection Points</h2>
            <InflectionPointsPanel inflectionPoints={inflectionPoints} />
          </div>
        </div>
      </div>

      <div className="trajectory-metadata">
        <h3>Projection Metadata</h3>
        <div className="metadata-grid">
          {(trajectory as any).metadata?.cascade_depth && (
            <div className="metadata-item">
              <strong>Cascade Depth:</strong> {(trajectory as any).metadata.cascade_depth}
            </div>
          )}
          {(trajectory as any).metadata?.cascade_waves_count && (
            <div className="metadata-item">
              <strong>Cascade Waves:</strong> {(trajectory as any).metadata.cascade_waves_count}
            </div>
          )}
          {(trajectory as any).metadata?.affected_domains && (
            <div className="metadata-item">
              <strong>Affected Domains:</strong>{' '}
              {Array.isArray((trajectory as any).metadata?.affected_domains)
                ? (trajectory as any).metadata.affected_domains.join(', ')
                : (trajectory as any).metadata?.affected_domains}
            </div>
          )}
          {(trajectory as any).metadata?.feedback_loops && (
            <div className="metadata-item">
              <strong>Feedback Loops:</strong> {(trajectory as any).metadata.feedback_loops}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrajectoryView;
