/**
 * Analysis Dashboard Component
 * Displays summary metrics and visualizations
 */
import { SurfaceAnalysis } from '../../services/api';
import './AnalysisDashboard.css';

interface AnalysisDashboardProps {
  analysis: SurfaceAnalysis;
}

export default function AnalysisDashboard({ analysis }: AnalysisDashboardProps) {
  const { assumptions, metadata } = analysis.assumptions;

  // Calculate metrics
  const avgQuality =
    assumptions.reduce((sum, a) => sum + a.quality_score, 0) / assumptions.length;
  const avgConfidence =
    assumptions.reduce((sum, a) => sum + a.confidence, 0) / assumptions.length;

  const priorityCounts = assumptions.reduce(
    (acc, a) => {
      acc[a.priority_tier] = (acc[a.priority_tier] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const crossDomainCount = assumptions.filter((a) => a.is_cross_domain).length;
  const validatedCount = assumptions.filter((a) => a.validated).length;

  return (
    <div className="analysis-dashboard">
      <h2>Analysis Summary</h2>

      <div className="metrics-grid">
        {/* Primary Metrics */}
        <div className="metric-card">
          <div className="metric-value">{metadata.total_assumptions}</div>
          <div className="metric-label">Total Assumptions</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{avgQuality.toFixed(1)}/100</div>
          <div className="metric-label">Avg Quality Score</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{(avgConfidence * 100).toFixed(0)}%</div>
          <div className="metric-label">Avg Confidence</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{(metadata.consistency_score * 100).toFixed(0)}%</div>
          <div className="metric-label">Consistency Score</div>
        </div>

        {/* Priority Breakdown */}
        <div className="metric-card priority-breakdown">
          <div className="metric-label">Priority Breakdown</div>
          <div className="priority-bars">
            <div className="priority-item">
              <span className="label">🔴 High:</span>
              <span className="count">{priorityCounts.high || 0}</span>
            </div>
            <div className="priority-item">
              <span className="label">🟡 Medium:</span>
              <span className="count">{priorityCounts.medium || 0}</span>
            </div>
            <div className="priority-item">
              <span className="label">🟢 Low:</span>
              <span className="count">{priorityCounts.low || 0}</span>
            </div>
            <div className="priority-item">
              <span className="label">⚠️ Review:</span>
              <span className="count">{priorityCounts.needs_review || 0}</span>
            </div>
          </div>
        </div>

        {/* Domain Distribution */}
        <div className="metric-card domain-distribution">
          <div className="metric-label">Domain Distribution</div>
          <div className="domain-bars">
            {Object.entries(metadata.domain_distribution)
              .sort((a, b) => b[1] - a[1])
              .map(([domain, count]) => (
                <div key={domain} className="domain-item">
                  <span className="label">{domain}:</span>
                  <span className="count">{count}</span>
                </div>
              ))}
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="metric-card">
          <div className="metric-value">{crossDomainCount}</div>
          <div className="metric-label">Cross-Domain</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{validatedCount}</div>
          <div className="metric-label">Validated</div>
        </div>
      </div>

      {/* Relationship Statistics (if available) */}
      {analysis.assumptions.relationships?.statistics && (
        <div className="relationships-section">
          <h3>Relationships</h3>
          <div className="relationship-stats">
            <div className="stat-item">
              <span className="value">{analysis.assumptions.relationships.statistics.relationships_found}</span>
              <span className="label">Total</span>
            </div>
            <div className="stat-item">
              <span className="value">{analysis.assumptions.relationships.statistics.dependencies}</span>
              <span className="label">Dependencies</span>
            </div>
            <div className="stat-item">
              <span className="value">{analysis.assumptions.relationships.statistics.reinforcements}</span>
              <span className="label">Reinforcements</span>
            </div>
            <div className="stat-item">
              <span className="value">{analysis.assumptions.relationships.statistics.contradictions}</span>
              <span className="label">Contradictions</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
