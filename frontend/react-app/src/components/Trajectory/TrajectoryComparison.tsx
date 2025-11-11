/**
 * Trajectory Comparison Component - Sprint 5 Task 5
 * Advanced comparison interface for baseline vs counterfactual trajectories
 */
import { useState, useMemo } from 'react';
import {
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  ReferenceLine,
  ReferenceDot,
} from 'recharts';
import type { Trajectory } from '../../services/trajectoryAPI';
import './TrajectoryComparison.css';

interface TrajectoryComparisonProps {
  baselineTrajectory: Trajectory;
  comparisonTrajectories: Trajectory[];
  selectedMetric?: string;
}

interface DivergencePoint {
  timestamp: number;
  index: number;
  magnitude: number;
  description: string;
}

interface ComparisonMetrics {
  timeToFirstDivergence: number; // years
  maxDeviationMagnitude: number;
  areaBetweenCurves: number;
  finalStateDifference: number;
  decisionPointAlignment: number; // percentage
}

const TrajectoryComparison = ({
  baselineTrajectory,
  comparisonTrajectories,
  selectedMetric = 'primary_metric',
}: TrajectoryComparisonProps) => {
  const [showConfidenceBounds, setShowConfidenceBounds] = useState(true);
  const [highlightDivergence, setHighlightDivergence] = useState(true);
  const [selectedComparisonId, setSelectedComparisonId] = useState<string | null>(
    comparisonTrajectories[0]?.trajectory_id || null
  );

  // Get selected comparison trajectory
  const selectedComparison = comparisonTrajectories.find(
    (t) => t.trajectory_id === selectedComparisonId
  );

  // Calculate divergence points
  const divergencePoints = useMemo(() => {
    if (!selectedComparison) return [];

    const points: DivergencePoint[] = [];
    const threshold = 0.10; // 10% divergence threshold

    baselineTrajectory.baseline_trajectory.forEach((basePoint, index) => {
      const compPoint = selectedComparison.baseline_trajectory[index];
      if (!compPoint) return;

      const baseValue =
        basePoint.state_variables[selectedMetric as keyof typeof basePoint.state_variables];
      const compValue =
        compPoint.state_variables[selectedMetric as keyof typeof compPoint.state_variables];

      const percentDiff = Math.abs((compValue - baseValue) / baseValue);

      if (percentDiff > threshold) {
        points.push({
          timestamp: basePoint.timestamp,
          index,
          magnitude: percentDiff,
          description: `${(percentDiff * 100).toFixed(1)}% divergence`,
        });
      }
    });

    return points;
  }, [baselineTrajectory, selectedComparison, selectedMetric]);

  // Calculate comparison metrics
  const comparisonMetrics = useMemo((): ComparisonMetrics | null => {
    if (!selectedComparison) return null;

    // Time to first divergence
    const firstDivergence = divergencePoints[0];
    const timeToFirstDivergence = firstDivergence?.timestamp || baselineTrajectory.time_horizon;

    // Max deviation
    const maxDeviation = Math.max(...divergencePoints.map((d) => d.magnitude), 0);

    // Area between curves (simple trapezoidal integration)
    let area = 0;
    for (let i = 0; i < baselineTrajectory.baseline_trajectory.length - 1; i++) {
      const basePoint = baselineTrajectory.baseline_trajectory[i];
      const compPoint = selectedComparison.baseline_trajectory[i];
      const nextBasePoint = baselineTrajectory.baseline_trajectory[i + 1];
      const nextCompPoint = selectedComparison.baseline_trajectory[i + 1];

      if (!compPoint || !nextCompPoint) continue;

      const baseValue =
        basePoint.state_variables[selectedMetric as keyof typeof basePoint.state_variables];
      const compValue =
        compPoint.state_variables[selectedMetric as keyof typeof compPoint.state_variables];
      const nextBaseValue =
        nextBasePoint.state_variables[selectedMetric as keyof typeof nextBasePoint.state_variables];
      const nextCompValue =
        nextCompPoint.state_variables[selectedMetric as keyof typeof nextCompPoint.state_variables];

      const diff1 = Math.abs(compValue - baseValue);
      const diff2 = Math.abs(nextCompValue - nextBaseValue);
      const dt = nextBasePoint.timestamp - basePoint.timestamp;

      area += ((diff1 + diff2) / 2) * dt;
    }

    // Final state difference
    const baseFinal =
      baselineTrajectory.baseline_trajectory[baselineTrajectory.baseline_trajectory.length - 1]
        .state_variables[selectedMetric as keyof typeof baselineTrajectory.baseline_trajectory[0].state_variables];
    const compFinal =
      selectedComparison.baseline_trajectory[selectedComparison.baseline_trajectory.length - 1]
        .state_variables[selectedMetric as keyof typeof selectedComparison.baseline_trajectory[0].state_variables];
    const finalDiff = Math.abs((compFinal - baseFinal) / baseFinal);

    // Decision point alignment
    const baseDecisionTimes = new Set(
      baselineTrajectory.decision_points.map((dp) => dp.timestamp.toFixed(2))
    );
    const compDecisionTimes = selectedComparison.decision_points.map((dp) =>
      dp.timestamp.toFixed(2)
    );
    const alignedCount = compDecisionTimes.filter((t) => baseDecisionTimes.has(t)).length;
    const alignment =
      baselineTrajectory.decision_points.length > 0
        ? (alignedCount / baselineTrajectory.decision_points.length) * 100
        : 0;

    return {
      timeToFirstDivergence,
      maxDeviationMagnitude: maxDeviation,
      areaBetweenCurves: area,
      finalStateDifference: finalDiff,
      decisionPointAlignment: alignment,
    };
  }, [baselineTrajectory, selectedComparison, selectedMetric, divergencePoints]);

  // Prepare chart data
  const chartData = useMemo(() => {
    return baselineTrajectory.baseline_trajectory.map((basePoint, index) => {
      const baseValue =
        basePoint.state_variables[selectedMetric as keyof typeof basePoint.state_variables];
      const [baseLower, baseUpper] = basePoint.confidence_bounds;

      const dataPoint: any = {
        timestamp: basePoint.timestamp,
        timestampLabel: `T+${basePoint.timestamp.toFixed(1)}y`,
        baseline: baseValue,
        baselineLower: showConfidenceBounds ? baseLower : undefined,
        baselineUpper: showConfidenceBounds ? baseUpper : undefined,
        index,
      };

      // Add comparison trajectories
      comparisonTrajectories.forEach((compTraj) => {
        const compPoint = compTraj.baseline_trajectory[index];
        if (compPoint) {
          const compValue =
            compPoint.state_variables[selectedMetric as keyof typeof compPoint.state_variables];
          dataPoint[`comparison_${compTraj.trajectory_id}`] = compValue;
        }
      });

      return dataPoint;
    });
  }, [baselineTrajectory, comparisonTrajectories, selectedMetric, showConfidenceBounds]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.90)',
            color: 'white',
            padding: '14px',
            borderRadius: '8px',
            fontSize: '13px',
            maxWidth: '280px',
          }}
        >
          <p style={{ margin: '0 0 10px 0', fontWeight: 'bold', fontSize: '14px' }}>
            {data.timestampLabel}
          </p>

          <div style={{ borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '8px' }}>
            <p style={{ margin: '6px 0', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#3b82f6', fontWeight: 'bold' }}>Baseline:</span>
              <span>{data.baseline?.toFixed(3)}</span>
            </p>

            {comparisonTrajectories.map((compTraj, idx) => {
              const key = `comparison_${compTraj.trajectory_id}`;
              const value = data[key];
              const color = COMPARISON_COLORS[idx % COMPARISON_COLORS.length];

              return (
                <p
                  key={key}
                  style={{ margin: '6px 0', display: 'flex', justifyContent: 'space-between' }}
                >
                  <span style={{ color, fontWeight: 'bold' }}>
                    Counterfactual {idx + 1}:
                  </span>
                  <span>{value?.toFixed(3)}</span>
                </p>
              );
            })}
          </div>

          {showConfidenceBounds && data.baselineLower !== undefined && (
            <div
              style={{
                borderTop: '1px solid rgba(255,255,255,0.2)',
                paddingTop: '8px',
                marginTop: '8px',
                fontSize: '11px',
                opacity: 0.8,
              }}
            >
              <p style={{ margin: '4px 0' }}>
                95% CI: [{data.baselineLower.toFixed(3)}, {data.baselineUpper.toFixed(3)}]
              </p>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  const COMPARISON_COLORS = ['#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899'];

  return (
    <div className="trajectory-comparison">
      <div className="comparison-header">
        <h2>Trajectory Comparison</h2>
        <div className="comparison-controls">
          <div className="selector-group">
            <label>Compare Against:</label>
            <select
              value={selectedComparisonId || ''}
              onChange={(e) => setSelectedComparisonId(e.target.value)}
            >
              {comparisonTrajectories.map((traj, idx) => (
                <option key={traj.trajectory_id} value={traj.trajectory_id}>
                  Counterfactual {idx + 1}
                </option>
              ))}
            </select>
          </div>

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
              checked={highlightDivergence}
              onChange={(e) => setHighlightDivergence(e.target.checked)}
            />
            Highlight Divergence Points
          </label>
        </div>
      </div>

      <div className="chart-container" style={{ height: '500px', marginTop: '20px' }}>
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
                value: selectedMetric.replace(/_/g, ' ').toUpperCase(),
                angle: -90,
                position: 'insideLeft',
                style: { fontSize: '13px', fontWeight: 600 },
              }}
              domain={['dataMin - 0.1', 'dataMax + 0.1']}
              stroke="#666"
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} iconType="line" />

            {/* Baseline confidence bounds */}
            {showConfidenceBounds && (
              <>
                <Area
                  type="monotone"
                  dataKey="baselineUpper"
                  stackId="confidence"
                  stroke="none"
                  fill="#3b82f6"
                  fillOpacity={0.12}
                  name="Baseline 95% CI"
                />
                <Area
                  type="monotone"
                  dataKey="baselineLower"
                  stackId="confidence"
                  stroke="none"
                  fill="#3b82f6"
                  fillOpacity={0.12}
                />
              </>
            )}

            {/* Baseline trajectory */}
            <Line
              type="monotone"
              dataKey="baseline"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ fill: '#3b82f6', r: 4 }}
              activeDot={{ r: 6 }}
              name="Baseline"
            />

            {/* Comparison trajectories */}
            {comparisonTrajectories.map((compTraj, idx) => (
              <Line
                key={compTraj.trajectory_id}
                type="monotone"
                dataKey={`comparison_${compTraj.trajectory_id}`}
                stroke={COMPARISON_COLORS[idx % COMPARISON_COLORS.length]}
                strokeWidth={2.5}
                strokeDasharray="5 5"
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
                name={`Counterfactual ${idx + 1}`}
              />
            ))}

            {/* Divergence point markers */}
            {highlightDivergence &&
              divergencePoints.slice(0, 5).map((div, idx) => (
                <ReferenceDot
                  key={`div-${idx}`}
                  x={div.timestamp}
                  y={
                    chartData.find((d) => d.index === div.index)?.baseline ||
                    0
                  }
                  r={8}
                  fill="#f59e0b"
                  fillOpacity={0.7}
                  stroke="#f59e0b"
                  strokeWidth={2}
                />
              ))}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Comparison Metrics Panel */}
      {comparisonMetrics && (
        <div className="metrics-panel">
          <h3>Comparison Metrics</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Time to First Divergence</div>
              <div className="metric-value">
                {comparisonMetrics.timeToFirstDivergence.toFixed(2)}y
              </div>
              <div className="metric-description">
                First 10%+ difference at T+{comparisonMetrics.timeToFirstDivergence.toFixed(1)}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Maximum Deviation</div>
              <div className="metric-value">
                {(comparisonMetrics.maxDeviationMagnitude * 100).toFixed(1)}%
              </div>
              <div className="metric-description">
                Largest percentage difference between trajectories
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Cumulative Divergence</div>
              <div className="metric-value">
                {comparisonMetrics.areaBetweenCurves.toFixed(3)}
              </div>
              <div className="metric-description">
                Integrated area between trajectory curves
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Final State Difference</div>
              <div className="metric-value">
                {(comparisonMetrics.finalStateDifference * 100).toFixed(1)}%
              </div>
              <div className="metric-description">
                Difference in outcome at time horizon
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Decision Point Alignment</div>
              <div className="metric-value">
                {comparisonMetrics.decisionPointAlignment.toFixed(0)}%
              </div>
              <div className="metric-description">
                Percentage of aligned decision points
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Natural Language Summary */}
      {comparisonMetrics && selectedComparison && (
        <div className="summary-panel">
          <h3>Analysis Summary</h3>
          <p className="summary-text">
            The counterfactual trajectory diverges from baseline after{' '}
            <strong>{comparisonMetrics.timeToFirstDivergence.toFixed(1)} years</strong>, with a
            maximum deviation of{' '}
            <strong>{(comparisonMetrics.maxDeviationMagnitude * 100).toFixed(1)}%</strong>. By the
            end of the projection period, the outcomes differ by{' '}
            <strong>{(comparisonMetrics.finalStateDifference * 100).toFixed(1)}%</strong>.
          </p>
          <p className="summary-text">
            The cumulative divergence (area between curves) is{' '}
            <strong>{comparisonMetrics.areaBetweenCurves.toFixed(3)}</strong>, indicating{' '}
            {comparisonMetrics.areaBetweenCurves > 0.5 ? 'substantial' : 'moderate'} overall
            difference in trajectory paths.
          </p>
          <p className="summary-text">
            Decision points align at <strong>{comparisonMetrics.decisionPointAlignment.toFixed(0)}%</strong>,
            suggesting {comparisonMetrics.decisionPointAlignment > 50 ? 'similar' : 'divergent'} critical
            moments across scenarios.
          </p>
        </div>
      )}

      {/* Divergence Points Table */}
      {highlightDivergence && divergencePoints.length > 0 && (
        <div className="divergence-table">
          <h3>Significant Divergence Points</h3>
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Magnitude</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {divergencePoints.slice(0, 10).map((div, idx) => (
                <tr key={idx}>
                  <td>T+{div.timestamp.toFixed(2)}y</td>
                  <td>{(div.magnitude * 100).toFixed(1)}%</td>
                  <td>{div.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TrajectoryComparison;
