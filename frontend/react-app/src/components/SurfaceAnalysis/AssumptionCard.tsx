/**
 * Assumption Card Component
 * Displays a single assumption with all enriched data
 */
import { useState } from 'react';
import { Assumption } from '../../services/api';
import './AssumptionCard.css';

interface AssumptionCardProps {
  assumption: Assumption;
  isSelected: boolean;
  onToggleSelect: () => void;
  onAccept: () => void;
  onReject: () => void;
}

const PRIORITY_COLORS = {
  high: '#EF4444',
  medium: '#EAB308',
  low: '#10B981',
  needs_review: '#F59E0B',
};

const PRIORITY_LABELS = {
  high: '🔴 High Priority',
  medium: '🟡 Medium Priority',
  low: '🟢 Low Priority',
  needs_review: '⚠️ Needs Review',
};

const DOMAIN_COLORS: Record<string, string> = {
  political: '#8B5CF6',
  economic: '#3B82F6',
  technological: '#14B8A6',
  social: '#EC4899',
  operational: '#6B7280',
  strategic: '#6366F1',
  environmental: '#22C55E',
  cultural: '#F97316',
};

export default function AssumptionCard({
  assumption,
  isSelected,
  onToggleSelect,
  onAccept,
  onReject,
}: AssumptionCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getProgressBarWidth = (score: number) => {
    return `${score}%`;
  };

  return (
    <div className={`assumption-card ${isSelected ? 'selected' : ''} ${expanded ? 'expanded' : ''}`}>
      {/* Header */}
      <div className="card-header">
        <div className="header-left">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onToggleSelect}
            className="checkbox"
          />
          <span
            className="priority-badge"
            style={{ backgroundColor: PRIORITY_COLORS[assumption.priority_tier] }}
          >
            {PRIORITY_LABELS[assumption.priority_tier]}
          </span>
        </div>
        <div className="header-right">
          <span className="quality-score">
            Quality: {assumption.quality_score.toFixed(1)}/100
          </span>
          {assumption.validated && (
            <span className="validation-badge validated">✓ Validated</span>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="card-body">
        <p className="assumption-text">{assumption.text}</p>

        {/* Domains */}
        <div className="domains">
          {assumption.domains.map((domain) => (
            <span
              key={domain}
              className="domain-badge"
              style={{
                backgroundColor: DOMAIN_COLORS[domain] || '#6B7280',
                color: '#fff',
              }}
            >
              {domain.charAt(0).toUpperCase() + domain.slice(1)}
            </span>
          ))}
          {assumption.is_cross_domain && (
            <span className="cross-domain-indicator">Cross-domain</span>
          )}
        </div>

        {/* Confidence */}
        <div className="confidence-bar">
          <label>Confidence: {(assumption.confidence * 100).toFixed(0)}%</label>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: getProgressBarWidth(assumption.confidence * 100) }}
            />
          </div>
        </div>

        {/* Expandable Details */}
        {expanded && (
          <div className="card-details">
            {/* Source Excerpt */}
            {assumption.source_excerpt && (
              <div className="source-excerpt">
                <strong>Source:</strong>
                <blockquote>"{assumption.source_excerpt}"</blockquote>
              </div>
            )}

            {/* Quality Breakdown */}
            <div className="quality-breakdown">
              <h4>Quality Dimensions</h4>
              <div className="dimension">
                <label>Specificity: {assumption.quality_dimensions.specificity.toFixed(0)}</label>
                <div className="progress-bar">
                  <div
                    className="progress-fill specificity"
                    style={{ width: getProgressBarWidth(assumption.quality_dimensions.specificity) }}
                  />
                </div>
              </div>
              <div className="dimension">
                <label>Verifiability: {assumption.quality_dimensions.verifiability.toFixed(0)}</label>
                <div className="progress-bar">
                  <div
                    className="progress-fill verifiability"
                    style={{ width: getProgressBarWidth(assumption.quality_dimensions.verifiability) }}
                  />
                </div>
              </div>
              <div className="dimension">
                <label>Impact Potential: {assumption.quality_dimensions.impact_potential.toFixed(0)}</label>
                <div className="progress-bar">
                  <div
                    className="progress-fill impact"
                    style={{ width: getProgressBarWidth(assumption.quality_dimensions.impact_potential) }}
                  />
                </div>
              </div>
              <div className="dimension">
                <label>Source Strength: {assumption.quality_dimensions.source_strength.toFixed(0)}</label>
                <div className="progress-bar">
                  <div
                    className="progress-fill source"
                    style={{ width: getProgressBarWidth(assumption.quality_dimensions.source_strength) }}
                  />
                </div>
              </div>
            </div>

            {/* Domain Confidence */}
            {Object.keys(assumption.domain_confidence).length > 0 && (
              <div className="domain-confidence">
                <h4>Domain Confidence</h4>
                {Object.entries(assumption.domain_confidence).map(([domain, confidence]) => (
                  <div key={domain} className="domain-conf-item">
                    <span className="domain-name">
                      {domain.charAt(0).toUpperCase() + domain.slice(1)}:
                    </span>
                    <span className="conf-value">{(confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="card-actions">
        <button onClick={() => setExpanded(!expanded)} className="btn-expand">
          {expanded ? '▲ Collapse' : '▼ Expand Details'}
        </button>
        <div className="action-buttons">
          <button onClick={onAccept} className="btn-accept" disabled={assumption.validated}>
            ✓ Accept
          </button>
          <button onClick={onReject} className="btn-reject">
            ✗ Reject
          </button>
        </div>
      </div>
    </div>
  );
}
