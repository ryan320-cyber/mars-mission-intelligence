import {
  MissionOverviewData,
  ObservationsResponse,
  VerticalProfileData,
  AnomalyItem,
  EventReplayData,
  ChallengeIndexData,
  ModelLabData,
  AIResponse,
  DataCatalogItem
} from "./types";

const API_BASE = "http://127.0.0.1:8000/api";

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`API request failed for ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  getOverview: (): Promise<MissionOverviewData> => 
    fetchJson<MissionOverviewData>("/overview"),

  getObservations: (mission = "curiosity", maxPoints = 400, startSol?: number, endSol?: number): Promise<ObservationsResponse> => {
    let q = `/observations?mission=${mission}&max_points=${maxPoints}`;
    if (startSol !== undefined) q += `&start_sol=${startSol}`;
    if (endSol !== undefined) q += `&end_sol=${endSol}`;
    return fetchJson<ObservationsResponse>(q);
  },

  getProfiles: (): Promise<{ profiles: VerticalProfileData[] }> => 
    fetchJson<{ profiles: VerticalProfileData[] }>("/profiles"),

  getAnomalies: (variable = "air_temp_max_c"): Promise<{
    variable_analyzed: string;
    univariate_count: number;
    univariate_anomalies: any[];
    multivariate_count: number;
    multivariate_anomalies: AnomalyItem[];
    methodology: string;
  }> => fetchJson(`/anomalies?variable=${variable}`),

  getEventReplay: (targetSol: number): Promise<EventReplayData> => 
    fetchJson<EventReplayData>(`/replay/${targetSol}`),

  getChallengeIndex: (): Promise<ChallengeIndexData> => 
    fetchJson<ChallengeIndexData>("/challenge-index"),

  simulateScenario: (params: {
    temp_variability_multiplier?: number;
    hypothetical_pressure_drop_pa?: number;
    dust_storm_active?: boolean;
  }) => fetchJson<any>("/challenge-index/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params)
  }),

  getModelLab: (): Promise<ModelLabData> => 
    fetchJson<ModelLabData>("/model-lab"),

  queryAI: (query: string): Promise<AIResponse> => 
    fetchJson<AIResponse>("/ai/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    }),

  getCatalog: (): Promise<{ datasets: Record<string, DataCatalogItem>; summary: any[] }> => 
    fetchJson("/catalog"),

  getScorecard: () => 
    fetchJson<any>("/scorecard"),

  getComparison: () => 
    fetchJson<any>("/statistics/comparison"),

  getCorrelation: () => 
    fetchJson<any>("/statistics/correlation")
};
