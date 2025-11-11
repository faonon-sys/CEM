/**
 * React Query hooks for API data fetching
 */
import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query';
import apiService from '../services/api';
import type {
  ComputeScoresRequest,
  CalibrateScoreRequest,
  MonteCarloRequest,
  PipelineTriggerRequest,
} from '../services/api';

// ============ Scoring Hooks ============

/**
 * Hook to fetch score for a counterfactual
 */
export function useCounterfactualScore(counterfactualId: string, options?: UseQueryOptions) {
  return useQuery({
    queryKey: ['score', counterfactualId],
    queryFn: () => apiService.getScore(counterfactualId),
    enabled: !!counterfactualId,
    ...options,
  } as any);
}

/**
 * Hook to compute scores for counterfactuals
 */
export function useComputeScores() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ComputeScoresRequest) => apiService.computeScores(request),
    onSuccess: (_data, variables) => {
      // Invalidate score queries for computed counterfactuals
      variables.counterfactual_ids.forEach((id) => {
        queryClient.invalidateQueries({ queryKey: ['score', id] });
      });
      queryClient.invalidateQueries({ queryKey: ['batch-status'] });
    },
  });
}

/**
 * Hook to calibrate a score
 */
export function useCalibrateScore(counterfactualId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CalibrateScoreRequest) =>
      apiService.calibrateScore(counterfactualId, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['score', counterfactualId] });
      queryClient.invalidateQueries({ queryKey: ['calibration-statistics'] });
      queryClient.invalidateQueries({ queryKey: ['counterfactuals'] });
    },
  });
}

/**
 * Hook to get sensitivity analysis
 */
export function useSensitivityAnalysis(counterfactualId: string) {
  return useQuery({
    queryKey: ['sensitivity', counterfactualId],
    queryFn: () => apiService.getSensitivityAnalysis(counterfactualId),
    enabled: !!counterfactualId,
  } as any);
}

/**
 * Hook to run Monte Carlo simulation
 */
export function useMonteCarloSimulation() {
  return useMutation({
    mutationFn: (request: MonteCarloRequest) => apiService.runMonteCarloSimulation(request),
  });
}

/**
 * Hook to get calibration statistics
 */
export function useCalibrationStatistics() {
  return useQuery({
    queryKey: ['calibration-statistics'],
    queryFn: () => apiService.getCalibrationStatistics(),
    staleTime: 60000, // 1 minute
  } as any);
}

/**
 * Hook to get batch scoring status
 */
export function useBatchStatus(scenarioId?: string) {
  return useQuery({
    queryKey: ['batch-status', scenarioId],
    queryFn: () => apiService.getBatchStatus(scenarioId),
    refetchInterval: 5000, // Poll every 5 seconds
  } as any);
}

// ============ Pipeline Hooks ============

/**
 * Hook to trigger Phase 3 pipeline
 */
export function useTriggerPhase3Pipeline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: PipelineTriggerRequest) => apiService.triggerPhase3Pipeline(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['counterfactuals'] });
    },
  });
}

/**
 * Hook to check pipeline status
 */
export function usePipelineStatus(taskId: string, enabled = true) {
  return useQuery({
    queryKey: ['pipeline-status', taskId],
    queryFn: () => apiService.getPhase3PipelineStatus(taskId),
    enabled: enabled && !!taskId,
    refetchInterval: (data: any) => {
      // Stop polling when pipeline is complete or failed
      if (data?.ready || data?.failed) {
        return false;
      }
      return 3000; // Poll every 3 seconds
    },
  } as any);
}

/**
 * Hook to fetch counterfactuals for a scenario
 */
export function useScenarioCounterfactuals(
  scenarioId: string,
  options?: {
    include_scores?: boolean;
    min_severity?: number;
    min_probability?: number;
    axis_filter?: string;
  }
) {
  return useQuery({
    queryKey: ['counterfactuals', scenarioId, options],
    queryFn: () => apiService.getScenarioCounterfactuals(scenarioId, options),
    enabled: !!scenarioId,
  } as any);
}

/**
 * Hook to fetch scenario graph for network visualization
 */
export function useScenarioGraph(scenarioId: string, includeScores = true) {
  return useQuery({
    queryKey: ['scenario-graph', scenarioId, includeScores],
    queryFn: () => apiService.getScenarioGraph(scenarioId, includeScores),
    enabled: !!scenarioId,
    staleTime: 30000, // 30 seconds
  } as any);
}

// ============ Scenario Hooks ============

/**
 * Hook to list all scenarios
 */
export function useScenarios() {
  return useQuery({
    queryKey: ['scenarios'],
    queryFn: () => apiService.listScenarios(),
  } as any);
}

/**
 * Hook to get a single scenario
 */
export function useScenario(scenarioId: string) {
  return useQuery({
    queryKey: ['scenario', scenarioId],
    queryFn: () => apiService.getScenario(scenarioId),
    enabled: !!scenarioId,
  } as any);
}

/**
 * Hook to create a new scenario
 */
export function useCreateScenario() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { title: string; description: string }) =>
      apiService.createScenario(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] });
    },
  });
}
