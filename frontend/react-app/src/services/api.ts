/**
 * API Service Layer for Structured Reasoning System
 * Provides typed methods for all backend API endpoints
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

// Types
export interface CounterfactualScore {
  id: string;
  counterfactual_id: string;
  severity_score: number;
  severity_ci_lower: number;
  severity_ci_upper: number;
  probability_score: number;
  probability_ci_lower: number;
  probability_ci_upper: number;
  risk_score: number;
  is_calibrated: boolean;
  calibrated_severity?: number;
  calibrated_probability?: number;
  computed_at: string;
}

export interface Counterfactual {
  id: string;
  scenario_id: string;
  breach_condition: string;
  narrative: string;
  consequences: string[];
  axis_id: string;
  affected_domains: string[];
  time_horizon: string;
  scores?: {
    severity: number;
    severity_ci: [number, number];
    probability: number;
    probability_ci: [number, number];
    risk: number;
    is_expert_adjusted: boolean;
  };
}

export interface GraphNode {
  id: string;
  type: 'assumption' | 'fragility' | 'breach' | 'counterfactual';
  label: string;
  severity?: number;
  probability?: number;
  metadata: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: 'dependency' | 'consequence' | 'transition';
  weight: number;
}

export interface ScenarioGraph {
  scenario_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  statistics: {
    fragilities: number;
    breaches: number;
    counterfactuals: number;
    total_nodes: number;
    total_edges: number;
  };
}

export interface ComputeScoresRequest {
  counterfactual_ids: string[];
  force_recompute?: boolean;
  weights?: {
    severity_weights?: Record<string, number>;
    probability_weights?: Record<string, number>;
  };
}

export interface CalibrateScoreRequest {
  severity_adjustment: number;
  probability_adjustment: number;
  rationale: string;
}

export interface MonteCarloRequest {
  counterfactual_id: string;
  n_simulations: number;
}

export interface PipelineTriggerRequest {
  scenario_id: string;
  fragility_ids?: string[];
  max_breaches_per_fragility?: number;
  custom_scoring_weights?: Record<string, any>;
}

export interface PipelineStatus {
  task_id: string;
  state: string;
  ready: boolean;
  successful: boolean;
  failed: boolean;
  progress?: Record<string, any>;
  result?: Record<string, any>;
}

// ============ Sprint 2: Surface Analysis Types ============

export interface Assumption {
  id: string;
  text: string;
  source_excerpt: string;
  domains: string[];
  domain_confidence: Record<string, number>;
  is_cross_domain: boolean;
  quality_score: number;
  quality_dimensions: {
    specificity: number;
    verifiability: number;
    impact_potential: number;
    source_strength: number;
  };
  priority_tier: 'high' | 'medium' | 'low' | 'needs_review';
  confidence: number;
  validated: boolean;
  user_edited: boolean;
  subcategories?: Record<string, string>;
}

export interface AssumptionRelationship {
  assumption_a_id: string;
  assumption_b_id: string;
  type: 'depends_on' | 'contradicts' | 'reinforces';
  confidence: number;
  explanation: string;
}

export interface GraphAnalysis {
  circular_dependencies: string[][];
  assumption_clusters: string[][];
  critical_assumptions: string[];
  contradiction_pairs: string[][];
}

export interface SurfaceAnalysisMetadata {
  extraction_model: string;
  prompt_version: string;
  consistency_score: number;
  validation_passed: boolean;
  domain_distribution: Record<string, number>;
  total_assumptions: number;
}

export interface SurfaceAnalysis {
  id: string;
  scenario_id: string;
  assumptions: {
    assumptions: Assumption[];
    baseline_narrative: string;
    narrative_themes: string[];
    anchor_assumptions: string[];
    relationships: {
      relationships: AssumptionRelationship[];
      graph_analysis: GraphAnalysis;
      statistics: {
        relationships_found: number;
        dependencies: number;
        reinforcements: number;
        contradictions: number;
      };
    };
    metadata: SurfaceAnalysisMetadata;
  };
  baseline_narrative: string;
  created_at: string;
}

export interface FilterAssumptionsRequest {
  domains?: string[];
  priority?: 'high' | 'medium' | 'low' | 'needs_review';
  min_quality?: number;
}

export interface ValidationAction {
  assumption_id: string;
  action: 'accept' | 'reject' | 'edit';
  new_text?: string;
}

class APIService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = '/api') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - could trigger re-login
          console.error('Unauthorized - token may be expired');
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Set authentication token
   */
  setToken(token: string) {
    this.token = token;
  }

  /**
   * Clear authentication token
   */
  clearToken() {
    this.token = null;
  }

  // ============ Scoring API ============

  /**
   * Compute scores for multiple counterfactuals
   */
  async computeScores(request: ComputeScoresRequest) {
    const response = await this.client.post('/scoring/compute', request);
    return response.data;
  }

  /**
   * Get score for a specific counterfactual
   */
  async getScore(counterfactualId: string): Promise<CounterfactualScore> {
    const response = await this.client.get(`/scoring/${counterfactualId}`);
    return response.data;
  }

  /**
   * Calibrate (adjust) a score with expert judgment
   */
  async calibrateScore(counterfactualId: string, request: CalibrateScoreRequest) {
    const response = await this.client.put(`/scoring/calibrate/${counterfactualId}`, request);
    return response.data;
  }

  /**
   * Get sensitivity analysis for a counterfactual
   */
  async getSensitivityAnalysis(counterfactualId: string) {
    const response = await this.client.get(`/scoring/sensitivity/${counterfactualId}`);
    return response.data;
  }

  /**
   * Run Monte Carlo simulation
   */
  async runMonteCarloSimulation(request: MonteCarloRequest) {
    const response = await this.client.post('/scoring/monte-carlo', request);
    return response.data;
  }

  /**
   * Get calibration statistics
   */
  async getCalibrationStatistics() {
    const response = await this.client.get('/scoring/calibration/statistics');
    return response.data;
  }

  /**
   * Get batch scoring status
   */
  async getBatchStatus(scenarioId?: string) {
    const params = scenarioId ? { scenario_id: scenarioId } : {};
    const response = await this.client.get('/scoring/status/batch', { params });
    return response.data;
  }

  // ============ Phase 3 Pipeline API ============

  /**
   * Trigger Phase 2-3 pipeline
   */
  async triggerPhase3Pipeline(request: PipelineTriggerRequest) {
    const response = await this.client.post('/v1/pipeline/phase3/generate', request);
    return response.data;
  }

  /**
   * Check pipeline status
   */
  async getPhase3PipelineStatus(taskId: string): Promise<PipelineStatus> {
    const response = await this.client.get(`/v1/pipeline/phase3/status/${taskId}`);
    return response.data;
  }

  /**
   * Get counterfactuals for a scenario
   */
  async getScenarioCounterfactuals(
    scenarioId: string,
    options?: {
      include_scores?: boolean;
      min_severity?: number;
      min_probability?: number;
      axis_filter?: string;
    }
  ): Promise<{ scenario_id: string; counterfactuals: Counterfactual[]; total: number }> {
    const response = await this.client.get(`/v1/pipeline/scenarios/${scenarioId}/counterfactuals`, {
      params: options,
    });
    return response.data;
  }

  /**
   * Get scenario graph for network visualization
   */
  async getScenarioGraph(scenarioId: string, includeScores = true): Promise<ScenarioGraph> {
    const response = await this.client.get(`/v1/pipeline/scenarios/${scenarioId}/graph`, {
      params: { include_scores: includeScores },
    });
    return response.data;
  }

  // ============ Scenario API ============

  /**
   * List all scenarios
   */
  async listScenarios() {
    const response = await this.client.get('/scenarios/');
    return response.data;
  }

  /**
   * Get scenario by ID
   */
  async getScenario(scenarioId: string) {
    const response = await this.client.get(`/scenarios/${scenarioId}`);
    return response.data;
  }

  /**
   * Create new scenario
   */
  async createScenario(data: { title: string; description: string }) {
    const response = await this.client.post('/scenarios/', data);
    return response.data;
  }

  // ============ Sprint 2: Surface Analysis API ============

  /**
   * Generate surface analysis for a scenario
   */
  async generateSurfaceAnalysis(
    scenarioId: string,
    options?: {
      validate_consistency?: boolean;
      detect_relationships?: boolean;
    }
  ): Promise<SurfaceAnalysis> {
    const response = await this.client.post(
      `/scenarios/${scenarioId}/surface-analysis-v2`,
      null,
      { params: options, timeout: 180000 } // 3 minute timeout for long analysis
    );
    return response.data;
  }

  /**
   * Get existing surface analysis for a scenario
   */
  async getSurfaceAnalysis(scenarioId: string): Promise<SurfaceAnalysis> {
    const response = await this.client.get(`/scenarios/${scenarioId}/surface-analysis-v2`);
    return response.data;
  }

  /**
   * Filter assumptions by criteria
   */
  async filterAssumptions(
    scenarioId: string,
    filters: FilterAssumptionsRequest
  ): Promise<{
    scenario_id: string;
    total_assumptions: number;
    filtered_assumptions: number;
    assumptions: Assumption[];
  }> {
    const params = new URLSearchParams();
    if (filters.domains?.length) {
      params.append('domains', filters.domains.join(','));
    }
    if (filters.priority) {
      params.append('priority', filters.priority);
    }
    if (filters.min_quality !== undefined) {
      params.append('min_quality', filters.min_quality.toString());
    }

    const response = await this.client.get(
      `/scenarios/${scenarioId}/assumptions/filter?${params.toString()}`
    );
    return response.data;
  }

  /**
   * Batch validate assumptions (accept/reject/edit)
   */
  async validateAssumptions(
    scenarioId: string,
    actions: ValidationAction[]
  ): Promise<{
    message: string;
    total_assumptions: number;
  }> {
    const response = await this.client.post(
      `/scenarios/${scenarioId}/assumptions/validate`,
      actions
    );
    return response.data;
  }

  /**
   * Export analysis as JSON
   */
  async exportAnalysisJSON(scenarioId: string): Promise<Blob> {
    const response = await this.client.get(`/scenarios/${scenarioId}/export/json`, {
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Export analysis as Markdown
   */
  async exportAnalysisMarkdown(scenarioId: string): Promise<Blob> {
    const response = await this.client.get(`/scenarios/${scenarioId}/export/markdown`, {
      responseType: 'blob',
    });
    return response.data;
  }
}

// Create singleton instance
const apiService = new APIService();

export default apiService;
