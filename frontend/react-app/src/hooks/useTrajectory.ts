/**
 * React Query hooks for Trajectory API
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import trajectoryAPI, {
  ProjectTrajectoryRequest,
  InterventionRequest,
} from '../services/trajectoryAPI';

/**
 * Hook to fetch a trajectory by ID
 */
export function useTrajectory(trajectoryId: string, enabled = true) {
  return useQuery({
    queryKey: ['trajectory', trajectoryId],
    queryFn: () => trajectoryAPI.getTrajectory(trajectoryId),
    enabled: enabled && !!trajectoryId,
    staleTime: 300000, // 5 minutes
  } as any);
}

/**
 * Hook to project a new trajectory
 */
export function useProjectTrajectory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ProjectTrajectoryRequest) =>
      trajectoryAPI.projectTrajectory(request),
    onSuccess: (data) => {
      queryClient.setQueryData(['trajectory', data.trajectory_id], data);
      queryClient.invalidateQueries({ queryKey: ['scenarios'] });
    },
  });
}

/**
 * Hook to test an intervention
 */
export function useTestIntervention(trajectoryId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: InterventionRequest) =>
      trajectoryAPI.testIntervention(trajectoryId, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trajectory', trajectoryId] });
      queryClient.invalidateQueries({ queryKey: ['interventions', trajectoryId] });
    },
  });
}

/**
 * Hook to get decision points
 */
export function useDecisionPoints(trajectoryId: string, enabled = true) {
  return useQuery({
    queryKey: ['decision-points', trajectoryId],
    queryFn: () => trajectoryAPI.getDecisionPoints(trajectoryId),
    enabled: enabled && !!trajectoryId,
    staleTime: 300000,
  } as any);
}

/**
 * Hook to get inflection points
 */
export function useInflectionPoints(trajectoryId: string, enabled = true) {
  return useQuery({
    queryKey: ['inflection-points', trajectoryId],
    queryFn: () => trajectoryAPI.getInflectionPoints(trajectoryId),
    enabled: enabled && !!trajectoryId,
    staleTime: 300000,
  } as any);
}

/**
 * Hook to list trajectories for a scenario
 */
export function useScenarioTrajectories(scenarioId: string, enabled = true) {
  return useQuery({
    queryKey: ['scenario-trajectories', scenarioId],
    queryFn: () => trajectoryAPI.listScenarioTrajectories(scenarioId),
    enabled: enabled && !!scenarioId,
  } as any);
}
