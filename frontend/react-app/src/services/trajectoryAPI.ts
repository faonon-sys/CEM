/**
 * Trajectory API Service for Sprint 5
 * Handles Phase 5 Strategic Outcome Projection endpoints
 */
import axios, { AxiosInstance } from 'axios';

// Types from backend API
export interface TrajectoryPoint {
  timestamp: number;
  state_variables: {
    primary_metric: number;
    gdp_impact: number;
    stability_index: number;
    resource_levels: number;
    operational_capability: number;
    social_cohesion: number;
  };
  confidence_bounds: [number, number];
  cascade_wave: number;
  metadata?: Record<string, any>;
}

export interface DecisionPoint {
  id?: string;
  index: number;
  timestamp: number;
  criticality_score: number;
  alternative_pathways: Array<{
    description: string;
    probability: number;
    effects: Record<string, any>;
  }>;
  intervention_window: number;
  description: string;
  recommended_action: string;
  metadata?: Record<string, any>;
}

export interface InflectionPoint {
  id?: string;
  index: number;
  timestamp: number;
  type: string;
  magnitude: number;
  triggering_condition: string;
  pre_inflection_trend: number;
  post_inflection_trend: number;
  state_change: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface Trajectory {
  trajectory_id: string;
  counterfactual_id: string;
  scenario_id: string;
  time_horizon: number;
  granularity: string;
  baseline_trajectory: TrajectoryPoint[];
  alternative_branches: Array<{
    branch_id: string;
    decision_point_index: number;
    description: string;
    trajectory_points: TrajectoryPoint[];
  }>;
  decision_points: DecisionPoint[];
  inflection_points: InflectionPoint[];
  metadata: Record<string, any>;
  created_at: string;
}

export interface ProjectTrajectoryRequest {
  counterfactual_id: string;
  time_horizons?: number[];
  granularity?: 'monthly' | 'quarterly' | 'yearly';
  detect_decision_points?: boolean;
  detect_inflection_points?: boolean;
  baseline_state?: Record<string, any>;
}

export interface InterventionRequest {
  decision_point_index: number;
  intervention_type: 'mitigation' | 'acceleration' | 'deflection' | 'containment';
  intervention_name: string;
  intervention_description: string;
  impact_modifier: number; // 0-2
  estimated_cost?: 'low' | 'medium' | 'high' | 'very_high';
  implementation_timeframe?: string;
}

export interface InterventionResponse {
  intervention_id: string;
  trajectory_id: string;
  decision_point_index: number;
  intervention_type: string;
  projected_trajectory: TrajectoryPoint[];
  expected_value: number;
  roi_estimate: number | null;
  time_to_impact_months: number;
}

class TrajectoryAPIService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = '/api/trajectories') {
    this.client = axios.create({
      baseURL,
      timeout: 60000, // 60 seconds for trajectory calculations
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  setToken(token: string) {
    this.token = token;
  }

  /**
   * Project trajectory from a counterfactual
   */
  async projectTrajectory(request: ProjectTrajectoryRequest): Promise<Trajectory> {
    const response = await this.client.post('/project', request);
    return response.data;
  }

  /**
   * Get trajectory by ID
   */
  async getTrajectory(trajectoryId: string): Promise<Trajectory> {
    const response = await this.client.get(`/${trajectoryId}`);
    return response.data;
  }

  /**
   * Test an intervention at a decision point
   */
  async testIntervention(
    trajectoryId: string,
    request: InterventionRequest
  ): Promise<InterventionResponse> {
    const response = await this.client.post(`/${trajectoryId}/intervention`, request);
    return response.data;
  }

  /**
   * Get decision points for a trajectory
   */
  async getDecisionPoints(trajectoryId: string): Promise<{
    trajectory_id: string;
    decision_points: DecisionPoint[];
  }> {
    const response = await this.client.get(`/${trajectoryId}/decision-points`);
    return response.data;
  }

  /**
   * Get inflection points for a trajectory
   */
  async getInflectionPoints(trajectoryId: string): Promise<{
    trajectory_id: string;
    inflection_points: InflectionPoint[];
  }> {
    const response = await this.client.get(`/${trajectoryId}/inflection-points`);
    return response.data;
  }

  /**
   * List all trajectories for a scenario
   */
  async listScenarioTrajectories(scenarioId: string): Promise<{
    scenario_id: string;
    trajectories: Array<{
      id: string;
      counterfactual_id: string;
      time_horizon: number;
      granularity: string;
      cascade_depth: number;
      created_at: string;
    }>;
  }> {
    const response = await this.client.get(`/scenarios/${scenarioId}/list`);
    return response.data;
  }
}

// Singleton instance
const trajectoryAPI = new TrajectoryAPIService();

export default trajectoryAPI;
