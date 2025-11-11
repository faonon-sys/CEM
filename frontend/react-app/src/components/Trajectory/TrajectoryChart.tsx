/**
 * Trajectory Chart Component - Recharts Implementation
 * Visualizes trajectory with confidence bounds, decision points, and inflection points
 */
import {
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ComposedChart,
} from 'recharts';
import type { Trajectory, DecisionPoint, InflectionPoint } from '../../services/trajectoryAPI';

interface TrajectoryChartProps {
  trajectory: Trajectory;
  selectedMetric: string;
  showConfidenceBounds: boolean;
  showAlternativeBranches: boolean;
  decisionPoints: DecisionPoint[];
  inflectionPoints: InflectionPoint[];
}

const TrajectoryChart = ({
  trajectory,
  selectedMetric,
  showConfidenceBounds,
  showAlternativeBranches,
  decisionPoints,
  inflectionPoints,
}: TrajectoryChartProps) => {
  // Transform data for Recharts
  const chartData = trajectory.baseline_trajectory.map((point, index) => {
    const metricValue = point.state_variables[selectedMetric as keyof typeof point.state_variables];
    const [lowerBound, upperBound] = point.confidence_bounds;

    return {
      timestamp: point.timestamp,
      timestampLabel: `T+${point.timestamp.toFixed(1)}y`,
      value: metricValue,
      lowerBound: showConfidenceBounds ? lowerBound : undefined,
      upperBound: showConfidenceBounds ? upperBound : undefined,
      cascadeWave: point.cascade_wave,
      index,
    };
  });

  // Add alternative branches if enabled
  const branchData: Record<string, any[]> = {};
  if (showAlternativeBranches && trajectory.alternative_branches) {
    trajectory.alternative_branches.forEach((branch, branchIndex) => {
      const branchKey = `branch_${branchIndex}`;
      branchData[branchKey] = branch.trajectory_points.map((point) => ({
        timestamp: point.timestamp,
        value: point.state_variables[selectedMetric as keyof typeof point.state_variables],
      }));
    });
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            color: 'white',
            padding: '12px',
            borderRadius: '6px',
            fontSize: '13px',
          }}
        >
          <p style={{ margin: '0 0 8px 0', fontWeight: 'bold' }}>{data.timestampLabel}</p>
          <p style={{ margin: '4px 0' }}>
            <strong>Value:</strong> {data.value?.toFixed(3)}
          </p>
          {data.lowerBound !== undefined && (
            <p style={{ margin: '4px 0', fontSize: '11px', opacity: 0.8 }}>
              95% CI: [{data.lowerBound.toFixed(3)}, {data.upperBound.toFixed(3)}]
            </p>
          )}
          <p style={{ margin: '4px 0', fontSize: '11px', opacity: 0.7 }}>
            Cascade Wave: {data.cascadeWave}
          </p>
        </div>
      );
    }
    return null;
  };

  // Decision point markers
  const decisionPointMarkers = decisionPoints.map((dp) => (
    <ReferenceLine
      key={`dp-${dp.index}`}
      x={chartData.find((d) => d.index === dp.index)?.timestamp || dp.timestamp}
      stroke="#FF6B6B"
      strokeWidth={2}
      strokeDasharray="5 5"
      label={{
        value: `Decision Point`,
        position: 'top',
        fill: '#FF6B6B',
        fontSize: 11,
      }}
    />
  ));

  // Inflection point markers
  const inflectionPointMarkers = inflectionPoints.map((ip) => (
    <ReferenceLine
      key={`ip-${ip.index}`}
      x={chartData.find((d) => d.index === ip.index)?.timestamp || ip.timestamp}
      stroke="#FFB84D"
      strokeWidth={2}
      label={{
        value: ip.type,
        position: 'bottom',
        fill: '#FFB84D',
        fontSize: 10,
      }}
    />
  ));

  return (
    <div style={{ width: '100%', height: '500px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 40, left: 20, bottom: 60 }}
        >
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
          <Legend
            wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
            iconType="line"
          />

          {/* Confidence bounds as area */}
          {showConfidenceBounds && (
            <Area
              type="monotone"
              dataKey="upperBound"
              stackId="confidence"
              stroke="none"
              fill="#3b82f6"
              fillOpacity={0.15}
              name="95% Confidence Interval"
            />
          )}
          {showConfidenceBounds && (
            <Area
              type="monotone"
              dataKey="lowerBound"
              stackId="confidence"
              stroke="none"
              fill="#3b82f6"
              fillOpacity={0.15}
            />
          )}

          {/* Main trajectory line */}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }}
            name="Baseline Trajectory"
          />

          {/* Alternative branches */}
          {showAlternativeBranches &&
            Object.entries(branchData).map(([branchKey], idx) => (
              <Line
                key={branchKey}
                type="monotone"
                dataKey={branchKey}
                stroke={`hsl(${(idx * 60) % 360}, 70%, 50%)`}
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name={`Alternative Branch ${idx + 1}`}
              />
            ))}

          {/* Decision point markers */}
          {decisionPointMarkers}

          {/* Inflection point markers */}
          {inflectionPointMarkers}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Legend for markers */}
      <div style={{ marginTop: '10px', fontSize: '12px', color: '#666', textAlign: 'center' }}>
        <span style={{ marginRight: '20px' }}>
          <span style={{ color: '#FF6B6B', fontWeight: 'bold' }}>⎯⎯⎯</span> Decision Points
        </span>
        <span>
          <span style={{ color: '#FFB84D', fontWeight: 'bold' }}>⎯⎯⎯</span> Inflection Points
        </span>
      </div>
    </div>
  );
};

export default TrajectoryChart;
