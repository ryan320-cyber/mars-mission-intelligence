export interface MissionOverviewData {
  project_title: string;
  system_status: string;
  data_freshness: string;
  total_observations: number;
  total_sols_recorded: number;
  active_datasets_count: number;
  anomalies_detected_count: number;
  latest_curiosity_sol: number;
  latest_terrestrial_date: string;
  latest_pressure_pa: number | null;
  latest_temp_max_c: number | null;
  latest_temp_min_c: number | null;
  latest_temp_amplitude_c: number | null;
  latest_solar_longitude_ls: number | null;
  latest_season: string;
  current_meci: ChallengeIndexData;
}

export interface ObservationRecord {
  sol: number;
  terrestrial_date: string;
  solar_longitude_ls?: number | null;
  martian_season?: string;
  air_temp_min_c?: number | null;
  air_temp_max_c?: number | null;
  air_temp_mean_c?: number | null;
  temp_amplitude_c?: number | null;
  ground_temp_min_c?: number | null;
  ground_temp_max_c?: number | null;
  pressure_pa?: number | null;
  pressure_string?: string;
  atmospheric_opacity?: string;
  uv_index?: string;
  sunrise?: string;
  sunset?: string;
  wind_speed_mean_ms?: number | null;
  wind_direction_deg?: number | null;
  wind_direction_cardinal?: string;
  mission: string;
  site: string;
  data_source: string;
}

export interface SensorGap {
  start_sol: number;
  end_sol: number;
  gap_duration_sols: number;
  start_date: string;
  end_date: string;
  reason: string;
}

export interface ObservationsResponse {
  mission: string;
  total_matched: number;
  returned_points: number;
  is_downsampled: boolean;
  sensor_gaps: SensorGap[];
  observations: ObservationRecord[];
}

export interface VerticalProfileLevel {
  altitude_km: number;
  pressure_pa: number;
  temperature_k: number;
  temperature_c: number;
  temperature_uncertainty_k: number;
  dust_extinction_km_inv: number;
  water_ice_extinction_km_inv: number;
}

export interface VerticalProfileData {
  profile_id: string;
  label: string;
  latitude_deg: number;
  longitude_deg_east: number;
  solar_longitude_ls: number;
  orbit_number: number;
  instrument: string;
  spacecraft: string;
  pds_dataset_id: string;
  vertical_levels_count: number;
  levels: VerticalProfileLevel[];
}

export interface AnomalyItem {
  sol: number;
  terrestrial_date: string;
  anomaly_intensity: number;
  severity: "MODERATE" | "HIGH" | "EXTREME";
  observed_values: {
    air_temp_max_c?: number;
    air_temp_min_c?: number;
    temp_amplitude_c?: number;
    pressure_pa?: number;
    season?: string;
  };
  primary_contributors: string[];
  algorithm: string;
  mission: string;
  site: string;
}

export interface EventReplayData {
  target_sol: number;
  event_type: string;
  terrestrial_date: string;
  mission: string;
  site: string;
  narrative: {
    pre_event: string;
    anomaly_event: string;
    post_event: string;
  };
  event_telemetry: ObservationRecord;
  replay_timeline: {
    sol: number;
    terrestrial_date: string;
    offset_sols: number;
    air_temp_max_c?: number;
    air_temp_min_c?: number;
    temp_amplitude_c?: number;
    pressure_pa?: number;
    is_anomaly_center: boolean;
  }[];
}

export interface ChallengeIndexFactor {
  score: number;
  weight: number;
  metric: string;
  rationale: string;
}

export interface ChallengeIndexData {
  index_score: number;
  classification: "LOW" | "MODERATE" | "HIGH" | "EXTREME";
  classification_color: string;
  formula: string;
  factor_breakdown: {
    thermal_stress: ChallengeIndexFactor;
    barometric_instability: ChallengeIndexFactor;
    anomaly_intensity: ChallengeIndexFactor;
    seasonal_dust_forcing: ChallengeIndexFactor;
  };
  disclaimer: string;
}

export interface ModelComparisonItem {
  model_name: string;
  mae: number;
  rmse: number;
  r2: number;
  type: "Baseline" | "Machine Learning";
  improvement_over_baseline_pct?: number;
}

export interface ModelLabData {
  task_description: string;
  dataset_split: {
    methodology: string;
    train_samples: number;
    val_samples: number;
    test_samples: number;
    train_sol_range: string;
    test_sol_range: string;
  };
  models_comparison: ModelComparisonItem[];
  feature_importances: { feature: string; importance: number }[];
  slice_error_analysis: {
    seasonal_slices: Record<string, { sample_count: number; mae: number; max_error: number }>;
    failure_case_analysis: string;
  };
  test_predictions_sample: {
    sol: number;
    terrestrial_date: string;
    actual_amplitude: number;
    predicted_rf: number;
    persistence_baseline: number;
  }[];
}

export interface EvidenceLink {
  label: string;
  target: string;
  sol?: number;
}

export interface AIResponse {
  finding: string;
  data_evidence: string;
  analytical_interpretation: string;
  limitations: string;
  source: string;
  evidence_links: EvidenceLink[];
  data_sufficiency: "HIGH" | "MODERATE" | "LOW" | "INSUFFICIENT";
}

export interface DataCatalogItem {
  id: string;
  name: string;
  mission: string;
  spacecraft: string;
  instrument: string;
  dataset_id: string;
  pds_urn: string;
  doi: string;
  source_url: string;
  pds_archive_url: string;
  processing_level: string;
  spatial_coverage: {
    site: string;
    latitude_deg: number | string;
    longitude_deg_east: number | string;
    elevation_km: number | string;
    coordinate_system: string;
  };
  temporal_coverage: {
    start_earth_date: string;
    end_earth_date: string;
    start_sol: number | string;
    end_sol: number | string;
    observation_cadence: string;
  };
  variables: {
    id: string;
    name: string;
    unit: string;
    sensor: string;
    physical_range: number[];
    uncertainty: string;
  }[];
  data_quality: {
    completeness_pct: number;
    sensor_health: string;
    known_limitations: string[];
  };
}
