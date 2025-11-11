/**
 * Filter Panel Component
 * Provides filtering controls for assumptions
 */
import './FilterPanel.css';

interface FilterPanelProps {
  domains: string[];
  filters: {
    domains: string[];
    priority: 'high' | 'medium' | 'low' | 'needs_review' | null;
    minQuality: number;
  };
  onFilterChange: (filters: any) => void;
  totalCount: number;
  filteredCount: number;
}

const PRIORITIES = [
  { value: 'high', label: '🔴 High', color: '#EF4444' },
  { value: 'medium', label: '🟡 Medium', color: '#EAB308' },
  { value: 'low', label: '🟢 Low', color: '#10B981' },
  { value: 'needs_review', label: '⚠️ Needs Review', color: '#F59E0B' },
];

export default function FilterPanel({
  domains,
  filters,
  onFilterChange,
  totalCount,
  filteredCount,
}: FilterPanelProps) {
  const handleDomainToggle = (domain: string) => {
    const newDomains = filters.domains.includes(domain)
      ? filters.domains.filter((d) => d !== domain)
      : [...filters.domains, domain];

    onFilterChange({ ...filters, domains: newDomains });
  };

  const handlePriorityChange = (priority: string) => {
    const newPriority = filters.priority === priority ? null : priority;
    onFilterChange({ ...filters, priority: newPriority });
  };

  const handleQualityChange = (e: React.ChangeEvent<InputHTMLInputElement>) => {
    onFilterChange({ ...filters, minQuality: parseInt(e.target.value) });
  };

  const clearAllFilters = () => {
    onFilterChange({ domains: [], priority: null, minQuality: 0 });
  };

  const hasActiveFilters =
    filters.domains.length > 0 || filters.priority !== null || filters.minQuality > 0;

  return (
    <div className="filter-panel">
      <div className="filter-header">
        <h3>Filters</h3>
        {hasActiveFilters && (
          <button onClick={clearAllFilters} className="btn-clear-filters">
            Clear All
          </button>
        )}
      </div>

      {/* Domains Filter */}
      <div className="filter-section">
        <label className="filter-label">Domains</label>
        <div className="filter-options">
          {domains.map((domain) => (
            <label key={domain} className="checkbox-label">
              <input
                type="checkbox"
                checked={filters.domains.includes(domain)}
                onChange={() => handleDomainToggle(domain)}
              />
              <span>{domain.charAt(0).toUpperCase() + domain.slice(1)}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Priority Filter */}
      <div className="filter-section">
        <label className="filter-label">Priority</label>
        <div className="filter-options">
          {PRIORITIES.map((priority) => (
            <label key={priority.value} className="checkbox-label">
              <input
                type="radio"
                name="priority"
                checked={filters.priority === priority.value}
                onChange={() => handlePriorityChange(priority.value)}
              />
              <span>{priority.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Quality Score Filter */}
      <div className="filter-section">
        <label className="filter-label">
          Minimum Quality Score: {filters.minQuality}
        </label>
        <input
          type="range"
          min="0"
          max="100"
          step="5"
          value={filters.minQuality}
          onChange={handleQualityChange}
          className="quality-slider"
        />
        <div className="slider-labels">
          <span>0</span>
          <span>50</span>
          <span>100</span>
        </div>
      </div>

      {/* Results Count */}
      <div className="filter-results">
        Showing: <strong>{filteredCount}</strong> of <strong>{totalCount}</strong> assumptions
      </div>
    </div>
  );
}
