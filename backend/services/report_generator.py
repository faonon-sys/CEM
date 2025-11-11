"""
Sprint 5 - Task 7: Report Generation Service
============================================

Generates exportable strategic outcome reports in multiple formats:
- JSON: Machine-readable trajectory data
- HTML: Interactive web-based reports
- PDF: Executive summaries (requires ReportLab)
- PPTX: Presentation slides (requires python-pptx)

Currently implements JSON and HTML exports. PDF and PPTX require additional dependencies.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID
import base64
from io import BytesIO


class ReportGenerator:
    """
    Generates trajectory reports in multiple formats.

    Supports:
    - JSON exports for programmatic access
    - HTML dashboards with embedded visualizations
    - PDF reports (requires reportlab)
    - PowerPoint presentations (requires python-pptx)
    """

    def __init__(self):
        self.supported_formats = ['json', 'html']  # 'pdf', 'pptx' require additional deps

    def generate_report(
        self,
        trajectory_data: Dict,
        decision_points: List[Dict],
        inflection_points: List[Dict],
        format: str = 'json',
        template: str = 'executive',
        include_metadata: bool = True
    ) -> Dict:
        """
        Generate trajectory report in specified format.

        Args:
            trajectory_data: Complete trajectory projection data
            decision_points: List of decision points
            inflection_points: List of inflection points
            format: Output format ('json', 'html', 'pdf', 'pptx')
            template: Report template ('executive', 'technical', 'risk_management')
            include_metadata: Include computational metadata

        Returns:
            Dictionary with report content and metadata
        """
        if format not in self.supported_formats:
            raise ValueError(f"Format '{format}' not supported. Available: {self.supported_formats}")

        if format == 'json':
            return self._generate_json_report(
                trajectory_data, decision_points, inflection_points, include_metadata
            )
        elif format == 'html':
            return self._generate_html_report(
                trajectory_data, decision_points, inflection_points, template
            )
        # PDF and PPTX generation would go here
        # elif format == 'pdf':
        #     return self._generate_pdf_report(...)
        # elif format == 'pptx':
        #     return self._generate_pptx_report(...)

    def _generate_json_report(
        self,
        trajectory_data: Dict,
        decision_points: List[Dict],
        inflection_points: List[Dict],
        include_metadata: bool
    ) -> Dict:
        """Generate JSON export of trajectory data."""

        report = {
            'report_type': 'trajectory_projection',
            'generated_at': datetime.utcnow().isoformat(),
            'trajectory': {
                'id': trajectory_data.get('trajectory_id'),
                'counterfactual_id': trajectory_data.get('counterfactual_id'),
                'scenario_id': trajectory_data.get('scenario_id'),
                'time_horizon': trajectory_data.get('time_horizon'),
                'granularity': trajectory_data.get('granularity'),
                'baseline_trajectory': trajectory_data.get('baseline_trajectory', []),
                'alternative_branches': trajectory_data.get('alternative_branches', [])
            },
            'analysis': {
                'decision_points': decision_points,
                'inflection_points': inflection_points,
                'decision_points_count': len(decision_points),
                'inflection_points_count': len(inflection_points)
            }
        }

        if include_metadata:
            report['metadata'] = trajectory_data.get('metadata', {})

        # Calculate summary statistics
        baseline = trajectory_data.get('baseline_trajectory', [])
        if baseline:
            initial_value = baseline[0]['state_variables']['primary_metric']
            final_value = baseline[-1]['state_variables']['primary_metric']
            report['summary_statistics'] = {
                'initial_primary_metric': initial_value,
                'final_primary_metric': final_value,
                'total_change': final_value - initial_value,
                'percent_change': ((final_value - initial_value) / initial_value * 100) if initial_value > 0 else 0,
                'trajectory_points_count': len(baseline)
            }

        return {
            'format': 'json',
            'content': json.dumps(report, indent=2),
            'content_type': 'application/json',
            'filename': f'trajectory_report_{trajectory_data.get("trajectory_id", "unknown")}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
        }

    def _generate_html_report(
        self,
        trajectory_data: Dict,
        decision_points: List[Dict],
        inflection_points: List[Dict],
        template: str
    ) -> Dict:
        """Generate interactive HTML dashboard."""

        trajectory_id = trajectory_data.get('trajectory_id', 'unknown')
        time_horizon = trajectory_data.get('time_horizon', 0)

        # Prepare data for visualization
        baseline = trajectory_data.get('baseline_trajectory', [])

        # Generate chart data JSON
        chart_data = json.dumps([
            {
                'timestamp': point['timestamp'],
                'primary_metric': point['state_variables']['primary_metric'],
                'confidence_lower': point['confidence_bounds'][0],
                'confidence_upper': point['confidence_bounds'][1]
            }
            for point in baseline
        ])

        # Generate HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trajectory Report - {trajectory_id}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #1f2937;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        header {{
            background: white;
            padding: 32px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 24px;
        }}
        h1 {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #1f2937;
        }}
        .subtitle {{
            font-size: 16px;
            color: #6b7280;
        }}
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }}
        .metadata-item {{
            background: #f3f4f6;
            padding: 12px 16px;
            border-radius: 6px;
        }}
        .metadata-label {{
            font-size: 12px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metadata-value {{
            font-size: 20px;
            font-weight: 700;
            color: #1f2937;
            margin-top: 4px;
        }}
        .section {{
            background: white;
            padding: 32px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 24px;
        }}
        h2 {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #1f2937;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        thead {{
            background: #f3f4f6;
        }}
        th {{
            padding: 12px 16px;
            text-align: left;
            font-size: 13px;
            font-weight: 700;
            color: #374151;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #e5e7eb;
        }}
        td {{
            padding: 12px 16px;
            font-size: 14px;
            color: #6b7280;
            border-bottom: 1px solid #e5e7eb;
        }}
        tbody tr:hover {{
            background: #f9fafb;
        }}
        .criticality-high {{
            color: #ef4444;
            font-weight: 600;
        }}
        .criticality-medium {{
            color: #f59e0b;
            font-weight: 600;
        }}
        .criticality-low {{
            color: #10b981;
            font-weight: 600;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #9ca3af;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Strategic Outcome Trajectory Report</h1>
            <p class="subtitle">Generated on {datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")}</p>
            <div class="metadata">
                <div class="metadata-item">
                    <div class="metadata-label">Trajectory ID</div>
                    <div class="metadata-value">{trajectory_id[:8]}...</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Time Horizon</div>
                    <div class="metadata-value">{time_horizon} years</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Granularity</div>
                    <div class="metadata-value">{trajectory_data.get('granularity', 'monthly').capitalize()}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Decision Points</div>
                    <div class="metadata-value">{len(decision_points)}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Inflection Points</div>
                    <div class="metadata-value">{len(inflection_points)}</div>
                </div>
            </div>
        </header>

        <section class="section">
            <h2>Trajectory Projection</h2>
            <div class="chart-container">
                <canvas id="trajectoryChart"></canvas>
            </div>
        </section>

        <section class="section">
            <h2>Critical Decision Points</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Criticality</th>
                        <th>Description</th>
                        <th>Intervention Window</th>
                        <th>Recommended Action</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td>T+{dp.get('timestamp', 0):.1f}y</td>
                        <td class="criticality-{('high' if dp.get('criticality_score', 0) > 0.7 else 'medium' if dp.get('criticality_score', 0) > 0.4 else 'low')}">
                            {dp.get('criticality_score', 0) * 100:.0f}%
                        </td>
                        <td>{dp.get('description', 'N/A')[:100]}</td>
                        <td>{dp.get('intervention_window', 6.0):.1f} months</td>
                        <td>{dp.get('recommended_action', 'N/A')[:80]}</td>
                    </tr>
                    ''' for dp in decision_points])}
                </tbody>
            </table>
        </section>

        <section class="section">
            <h2>Inflection Points</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Type</th>
                        <th>Magnitude</th>
                        <th>Triggering Condition</th>
                        <th>Trend Change</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td>T+{ip.get('timestamp', 0):.1f}y</td>
                        <td>{ip.get('type', 'N/A').replace('_', ' ').title()}</td>
                        <td>{ip.get('magnitude', 0):.3f}</td>
                        <td>{ip.get('triggering_condition', 'N/A')[:100]}</td>
                        <td>{ip.get('pre_inflection_trend', 0):.3f} → {ip.get('post_inflection_trend', 0):.3f}</td>
                    </tr>
                    ''' for ip in inflection_points])}
                </tbody>
            </table>
        </section>

        <footer>
            <p>🤖 Generated with Structured Reasoning System - Strategic Outcome Projection Engine</p>
            <p>Phase 5 Sprint 5 Implementation</p>
        </footer>
    </div>

    <script>
        const chartData = {chart_data};

        const ctx = document.getElementById('trajectoryChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: chartData.map(d => `T+${{d.timestamp.toFixed(1)}}y`),
                datasets: [
                    {{
                        label: 'Primary Metric',
                        data: chartData.map(d => d.primary_metric),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.2
                    }},
                    {{
                        label: '95% CI Upper',
                        data: chartData.map(d => d.confidence_upper),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: '+1',
                        tension: 0.2
                    }},
                    {{
                        label: '95% CI Lower',
                        data: chartData.map(d => d.confidence_lower),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.2
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }},
                    title: {{
                        display: true,
                        text: 'Strategic Outcome Trajectory with 95% Confidence Intervals'
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'Time (years)'
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Primary Outcome Metric'
                        }},
                        beginAtZero: false
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

        return {
            'format': 'html',
            'content': html_content,
            'content_type': 'text/html',
            'filename': f'trajectory_report_{trajectory_id}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.html'
        }


# Helper functions for future PDF/PPTX generation
def _generate_pdf_report_stub(trajectory_data, decision_points, inflection_points, template):
    """
    Stub for PDF report generation. Requires:
    - reportlab: pip install reportlab
    - pillow: pip install pillow (for image embedding)
    """
    raise NotImplementedError("PDF generation requires reportlab. Install with: pip install reportlab pillow")


def _generate_pptx_report_stub(trajectory_data, decision_points, inflection_points, template):
    """
    Stub for PowerPoint generation. Requires:
    - python-pptx: pip install python-pptx
    """
    raise NotImplementedError("PPTX generation requires python-pptx. Install with: pip install python-pptx")


# Example usage
if __name__ == "__main__":
    print("=== Report Generator Validation ===\n")

    # Sample trajectory data
    sample_trajectory = {
        'trajectory_id': 'test-traj-001',
        'counterfactual_id': 'test-cf-001',
        'scenario_id': 'test-scenario-001',
        'time_horizon': 5.0,
        'granularity': 'monthly',
        'baseline_trajectory': [
            {
                'timestamp': i * 0.5,
                'state_variables': {'primary_metric': 0.75 - i * 0.05},
                'confidence_bounds': [0.70 - i * 0.05, 0.80 - i * 0.05]
            }
            for i in range(10)
        ],
        'metadata': {
            'cascade_depth': 4,
            'cascade_waves_count': 3
        }
    }

    sample_decision_points = [
        {
            'index': 3,
            'timestamp': 1.5,
            'criticality_score': 0.75,
            'description': 'Critical decision moment requiring intervention',
            'intervention_window': 6.0,
            'recommended_action': 'Implement mitigation measures'
        }
    ]

    sample_inflection_points = [
        {
            'index': 5,
            'timestamp': 2.5,
            'type': 'acceleration',
            'magnitude': 0.15,
            'triggering_condition': 'New cascade wave activation',
            'pre_inflection_trend': -0.05,
            'post_inflection_trend': -0.12
        }
    ]

    generator = ReportGenerator()

    # Test JSON export
    print("Testing JSON export...")
    json_report = generator.generate_report(
        sample_trajectory,
        sample_decision_points,
        sample_inflection_points,
        format='json'
    )
    print(f"✅ JSON report generated: {json_report['filename']}")
    print(f"   Content length: {len(json_report['content'])} bytes")

    # Test HTML export
    print("\nTesting HTML export...")
    html_report = generator.generate_report(
        sample_trajectory,
        sample_decision_points,
        sample_inflection_points,
        format='html',
        template='executive'
    )
    print(f"✅ HTML report generated: {html_report['filename']}")
    print(f"   Content length: {len(html_report['content'])} bytes")

    print("\n=== All validation tests passed ===")
