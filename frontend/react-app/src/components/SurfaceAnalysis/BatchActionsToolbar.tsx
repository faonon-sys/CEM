/**
 * Batch Actions Toolbar Component
 * Provides bulk operations for selected assumptions
 */
import { useState } from 'react';
import './BatchActionsToolbar.css';

interface BatchActionsToolbarProps {
  selectedIds: Set<string>;
  totalCount: number;
  onAcceptAll: () => void;
  onRejectAll: () => void;
  onClearSelection: () => void;
  onSelectAll: () => void;
}

export default function BatchActionsToolbar({
  selectedIds,
  totalCount,
  onAcceptAll,
  onRejectAll,
  onClearSelection,
  onSelectAll,
}: BatchActionsToolbarProps) {
  const [showConfirm, setShowConfirm] = useState<'accept' | 'reject' | null>(null);

  const selectedCount = selectedIds.size;
  const allSelected = selectedCount === totalCount;

  const handleAccept = () => {
    onAcceptAll();
    setShowConfirm(null);
  };

  const handleReject = () => {
    onRejectAll();
    setShowConfirm(null);
  };

  return (
    <div className="batch-actions-toolbar">
      <div className="selection-info">
        <label>
          <input
            type="checkbox"
            checked={allSelected}
            onChange={allSelected ? onClearSelection : onSelectAll}
          />
          <span>
            {selectedCount > 0
              ? `${selectedCount} selected`
              : 'Select all'}
          </span>
        </label>
      </div>

      {selectedCount > 0 && (
        <div className="batch-buttons">
          <button
            onClick={() => setShowConfirm('accept')}
            className="btn-batch-accept"
          >
            ✓ Accept Selected ({selectedCount})
          </button>
          <button
            onClick={() => setShowConfirm('reject')}
            className="btn-batch-reject"
          >
            ✗ Reject Selected ({selectedCount})
          </button>
          <button onClick={onClearSelection} className="btn-clear">
            Clear Selection
          </button>
        </div>
      )}

      {/* Confirmation Dialog */}
      {showConfirm && (
        <div className="confirm-dialog-overlay" onClick={() => setShowConfirm(null)}>
          <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Batch Action</h3>
            <p>
              Are you sure you want to {showConfirm} {selectedCount} assumption
              {selectedCount > 1 ? 's' : ''}?
            </p>
            <div className="dialog-actions">
              <button onClick={() => setShowConfirm(null)} className="btn-cancel">
                Cancel
              </button>
              <button
                onClick={showConfirm === 'accept' ? handleAccept : handleReject}
                className={showConfirm === 'accept' ? 'btn-confirm-accept' : 'btn-confirm-reject'}
              >
                Confirm {showConfirm === 'accept' ? 'Accept' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
