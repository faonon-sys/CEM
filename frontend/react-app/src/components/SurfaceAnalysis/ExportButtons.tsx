/**
 * Export Buttons Component
 * Provides export functionality for analysis results
 */
import { useState } from 'react';
import apiService from '../../services/api';
import './ExportButtons.css';

interface ExportButtonsProps {
  scenarioId: string;
}

export default function ExportButtons({ scenarioId }: ExportButtonsProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async (format: 'json' | 'markdown') => {
    setIsExporting(true);

    try {
      let blob: Blob;
      let filename: string;

      if (format === 'json') {
        blob = await apiService.exportAnalysisJSON(scenarioId);
        filename = `scenario_${scenarioId}_analysis.json`;
      } else {
        blob = await apiService.exportAnalysisMarkdown(scenarioId);
        filename = `scenario_${scenarioId}_analysis.md`;
      }

      // Trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export error:', err);
      alert(`Failed to export as ${format.toUpperCase()}`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="export-buttons">
      <button
        onClick={() => handleExport('json')}
        disabled={isExporting}
        className="btn-export-json"
      >
        📄 Export JSON
      </button>
      <button
        onClick={() => handleExport('markdown')}
        disabled={isExporting}
        className="btn-export-markdown"
      >
        📝 Export Markdown
      </button>
    </div>
  );
}
