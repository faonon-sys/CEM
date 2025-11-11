/**
 * Surface Analysis Page - Sprint 2 UI Implementation
 * Main component that orchestrates the surface premise analysis workflow
 */
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import apiService, { SurfaceAnalysis as SurfaceAnalysisType, Assumption } from '../../services/api';
import AssumptionCard from './AssumptionCard';
import FilterPanel from './FilterPanel';
import AnalysisDashboard from './AnalysisDashboard';
import BatchActionsToolbar from './BatchActionsToolbar';
import ExportButtons from './ExportButtons';
import './SurfaceAnalysis.css';

interface FilterState {
  domains: string[];
  priority: 'high' | 'medium' | 'low' | 'needs_review' | null;
  minQuality: number;
}

export default function SurfaceAnalysis() {
  const { scenarioId } = useParams<{ scenarioId: string }>();
  const [analysis, setAnalysis] = useState<SurfaceAnalysisType | null>(null);
  const [filteredAssumptions, setFilteredAssumptions] = useState<Assumption[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    domains: [],
    priority: null,
    minQuality: 0,
  });
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  // Load existing analysis on mount
  useEffect(() => {
    if (scenarioId) {
      loadAnalysis();
    }
  }, [scenarioId]);

  // Apply filters when they change or analysis loads
  useEffect(() => {
    if (analysis) {
      applyFilters();
    }
  }, [analysis, filters]);

  const loadAnalysis = async () => {
    if (!scenarioId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await apiService.getSurfaceAnalysis(scenarioId);
      setAnalysis(data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('No analysis found. Click "Generate Analysis" to create one.');
      } else {
        setError('Failed to load analysis. Please try again.');
        console.error('Load analysis error:', err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const generateAnalysis = async () => {
    if (!scenarioId) return;

    setIsGenerating(true);
    setError(null);

    try {
      const data = await apiService.generateSurfaceAnalysis(scenarioId, {
        validate_consistency: true,
        detect_relationships: true,
      });
      setAnalysis(data);
      showToast('Analysis generated successfully!', 'success');
    } catch (err: any) {
      setError('Failed to generate analysis. Please try again.');
      showToast('Failed to generate analysis', 'error');
      console.error('Generate analysis error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const applyFilters = async () => {
    if (!scenarioId || !analysis) return;

    // If no filters applied, show all assumptions
    if (filters.domains.length === 0 && !filters.priority && filters.minQuality === 0) {
      setFilteredAssumptions(analysis.assumptions.assumptions);
      return;
    }

    try {
      const filterRequest: any = {};
      if (filters.domains.length > 0) filterRequest.domains = filters.domains;
      if (filters.priority) filterRequest.priority = filters.priority;
      if (filters.minQuality > 0) filterRequest.min_quality = filters.minQuality;

      const result = await apiService.filterAssumptions(scenarioId, filterRequest);
      setFilteredAssumptions(result.assumptions);
    } catch (err) {
      console.error('Filter error:', err);
      // Fall back to client-side filtering
      let filtered = [...analysis.assumptions.assumptions];

      if (filters.domains.length > 0) {
        filtered = filtered.filter((a) =>
          a.domains.some((d) => filters.domains.includes(d))
        );
      }

      if (filters.priority) {
        filtered = filtered.filter((a) => a.priority_tier === filters.priority);
      }

      if (filters.minQuality > 0) {
        filtered = filtered.filter((a) => a.quality_score >= filters.minQuality);
      }

      setFilteredAssumptions(filtered);
    }
  };

  const handleValidate = async (assumptionId: string, action: 'accept' | 'reject') => {
    if (!scenarioId) return;

    try {
      // Optimistic update
      setAnalysis((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          assumptions: {
            ...prev.assumptions,
            assumptions: prev.assumptions.assumptions.map((a) =>
              a.id === assumptionId
                ? { ...a, validated: action === 'accept' }
                : a
            ),
          },
        };
      });

      await apiService.validateAssumptions(scenarioId, [
        { assumption_id: assumptionId, action },
      ]);

      showToast(`Assumption ${action}ed`, 'success');
    } catch (err) {
      console.error('Validate error:', err);
      showToast(`Failed to ${action} assumption`, 'error');
      // Revert optimistic update
      await loadAnalysis();
    }
  };

  const handleBatchValidate = async (action: 'accept' | 'reject') => {
    if (!scenarioId || selectedIds.size === 0) return;

    try {
      const actions = Array.from(selectedIds).map((id) => ({
        assumption_id: id,
        action,
      }));

      await apiService.validateAssumptions(scenarioId, actions);

      // Reload analysis to get fresh data
      await loadAnalysis();
      setSelectedIds(new Set());
      showToast(`${selectedIds.size} assumptions ${action}ed`, 'success');
    } catch (err) {
      console.error('Batch validate error:', err);
      showToast(`Failed to ${action} assumptions`, 'error');
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const selectAll = () => {
    setSelectedIds(new Set(filteredAssumptions.map((a) => a.id)));
  };

  const clearSelection = () => {
    setSelectedIds(new Set());
  };

  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  if (isLoading) {
    return (
      <div className="surface-analysis loading">
        <div className="spinner" />
        <p>Loading analysis...</p>
      </div>
    );
  }

  if (error && !analysis) {
    return (
      <div className="surface-analysis error">
        <div className="error-message">{error}</div>
        <button onClick={generateAnalysis} disabled={isGenerating} className="btn-primary">
          {isGenerating ? 'Generating... (this may take 50-100 seconds)' : 'Generate Analysis'}
        </button>
      </div>
    );
  }

  return (
    <div className="surface-analysis">
      {/* Toast Notification */}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.message}
        </div>
      )}

      {/* Header */}
      <div className="analysis-header">
        <h1>Surface Premise Analysis</h1>
        <div className="header-actions">
          <button
            onClick={generateAnalysis}
            disabled={isGenerating}
            className="btn-secondary"
          >
            {isGenerating ? 'Regenerating...' : 'Regenerate Analysis'}
          </button>
          {analysis && <ExportButtons scenarioId={scenarioId!} />}
        </div>
      </div>

      {analysis && (
        <>
          {/* Dashboard with metrics and charts */}
          <AnalysisDashboard analysis={analysis} />

          {/* Filter Panel */}
          <FilterPanel
            domains={Object.keys(analysis.assumptions.metadata.domain_distribution)}
            filters={filters}
            onFilterChange={setFilters}
            totalCount={analysis.assumptions.assumptions.length}
            filteredCount={filteredAssumptions.length}
          />

          {/* Batch Actions Toolbar */}
          {filteredAssumptions.length > 0 && (
            <BatchActionsToolbar
              selectedIds={selectedIds}
              totalCount={filteredAssumptions.length}
              onAcceptAll={() => handleBatchValidate('accept')}
              onRejectAll={() => handleBatchValidate('reject')}
              onClearSelection={clearSelection}
              onSelectAll={selectAll}
            />
          )}

          {/* Assumptions List */}
          <div className="assumptions-list">
            {filteredAssumptions.length === 0 ? (
              <div className="empty-state">
                <p>No assumptions match the current filters.</p>
                <button onClick={() => setFilters({ domains: [], priority: null, minQuality: 0 })}>
                  Clear Filters
                </button>
              </div>
            ) : (
              filteredAssumptions.map((assumption) => (
                <AssumptionCard
                  key={assumption.id}
                  assumption={assumption}
                  isSelected={selectedIds.has(assumption.id)}
                  onToggleSelect={() => toggleSelect(assumption.id)}
                  onAccept={() => handleValidate(assumption.id, 'accept')}
                  onReject={() => handleValidate(assumption.id, 'reject')}
                />
              ))
            )}
          </div>

          {/* Baseline Narrative Section */}
          {analysis.baseline_narrative && (
            <div className="baseline-narrative-section">
              <h2>Baseline Narrative</h2>
              <p className="narrative-text">{analysis.baseline_narrative}</p>
              {analysis.assumptions.narrative_themes.length > 0 && (
                <div className="themes">
                  <h3>Key Themes</h3>
                  <ul>
                    {analysis.assumptions.narrative_themes.map((theme, idx) => (
                      <li key={idx}>{theme}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
