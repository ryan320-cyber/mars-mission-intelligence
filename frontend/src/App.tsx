import React, { useState, useEffect } from "react";
import { Header } from "./components/layout/Header";
import { MissionOverview } from "./components/overview/MissionOverview";
import { MultiMissionExplorer } from "./components/explorer/MultiMissionExplorer";
import { VerticalProfileViewer } from "./components/atmospheric/VerticalProfileViewer";
import { AnomalyTimeline } from "./components/anomaly/AnomalyTimeline";
import { MarsEnvironmentMap } from "./components/map/MarsEnvironmentMap";
import { ChallengeIndexCard } from "./components/risk/ChallengeIndexCard";
import { ModelLab } from "./components/model/ModelLab";
import { MarsAIScientist } from "./components/ai/MarsAIScientist";
import { DataCatalog } from "./components/catalog/DataCatalog";
import { ScienceNotebook } from "./components/methodology/ScienceNotebook";
import { JudgeDemoMode } from "./components/demo/JudgeDemoMode";
import { ErrorBoundary } from "./components/common/ErrorBoundary";
import { MissionOverviewData } from "./lib/types";
import { api } from "./lib/api";

const OFFLINE_FALLBACK_OVERVIEW: MissionOverviewData = {
  project_title: "Mars Mission Intelligence",
  system_status: "STANDALONE CACHE (BACKEND OFFLINE)",
  data_freshness: "OFFLINE HISTORICAL SNAPSHOT",
  total_observations: 4745,
  total_sols_recorded: 4745,
  active_datasets_count: 3,
  anomalies_detected_count: 24,
  latest_curiosity_sol: 4745,
  latest_terrestrial_date: "2026-08-15",
  latest_pressure_pa: 842.5,
  latest_temp_max_c: -12.4,
  latest_temp_min_c: -78.2,
  latest_temp_amplitude_c: 65.8,
  latest_solar_longitude_ls: 142.6,
  latest_season: "Northern Summer / Southern Winter",
  current_meci: {
    index_score: 58.4,
    classification: "HIGH",
    classification_color: "#f59e0b",
    formula: "MECI = 0.35 * Thermal + 0.25 * Pressure + 0.25 * Anomaly + 0.15 * Dust",
    factor_breakdown: {
      thermal_stress: { score: 65.8, weight: 0.35, metric: "Δ 65.8 °C", rationale: "Diurnal thermal swing" },
      barometric_instability: { score: 48.2, weight: 0.25, metric: "1.2 Pa/sol", rationale: "Pressure variation" },
      anomaly_intensity: { score: 55.0, weight: 0.25, metric: "55/100", rationale: "Isolation forest intensity" },
      seasonal_dust_forcing: { score: 62.0, weight: 0.15, metric: "Ls 142.6°", rationale: "Seasonal dust forcing" }
    },
    disclaimer: "Static historical snapshot rendered in offline mode. Live telemetry stream unavailable."
  },
  data_origin: "observed"
};

const normalizeTab = (rawTab: string): string => {
  switch (rawTab) {
    case "anomaly_timeline":
    case "event_replay":
      return "anomaly";
    case "challenge_index":
    case "what_if_simulator":
      return "meci";
    case "model_lab":
    case "slice_analysis":
      return "model";
    case "vertical_profiles":
      return "atmospheric";
    case "data_explorer":
    case "mission_comparison":
    case "correlation_matrix":
      return "explorer";
    case "data_catalog":
      return "catalog";
    default:
      return rawTab;
  }
};

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [isJudgeMode, setIsJudgeMode] = useState<boolean>(false);
  const [overviewData, setOverviewData] = useState<MissionOverviewData | null>(null);
  const [selectedReplaySol, setSelectedReplaySol] = useState<number | null>(null);
  const [isOffline, setIsOffline] = useState<boolean>(false);
  const [isRetrying, setIsRetrying] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    api.getOverview()
      .then((res) => {
        if (isMounted) {
          setOverviewData(res);
          setIsOffline(false);
        }
      })
      .catch((err) => {
        console.warn("Backend API unreachable. Using offline telemetry cache:", err);
        if (isMounted) {
          setOverviewData(OFFLINE_FALLBACK_OVERVIEW);
          setIsOffline(true);
        }
      });
    return () => { isMounted = false; };
  }, []);

  const handleManualRetry = () => {
    setIsRetrying(true);
    api.getOverview()
      .then((res) => {
        setOverviewData(res);
        setIsOffline(false);
      })
      .catch((err) => {
        console.warn("Backend API retry failed. Using offline telemetry cache:", err);
        setOverviewData(OFFLINE_FALLBACK_OVERVIEW);
        setIsOffline(true);
      })
      .finally(() => {
        setIsRetrying(false);
      });
  };

  const handleNavigate = (tabId: string, sol?: number) => {
    const normalized = normalizeTab(tabId);
    setActiveTab(normalized);
    if (sol !== undefined) {
      setSelectedReplaySol(sol);
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen flex flex-col bg-mars-darkest text-slate-200">
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isJudgeMode={isJudgeMode}
        setIsJudgeMode={setIsJudgeMode}
        systemStatus={overviewData?.system_status || (isOffline ? "STANDALONE CACHE" : "OPERATIONAL")}
        dataFreshness={overviewData?.data_freshness || (isOffline ? "OFFLINE CACHED SNAPSHOT" : "REAL NASA TELEMETRY CACHED")}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-3 md:px-6 md:py-4 space-y-4">
        {/* Offline Outage Notice */}
        {isOffline && (
          <div className="bg-amber-950/60 border border-amber-500/50 rounded-lg p-3 px-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-amber-200 shadow-lg">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
              <span>
                <strong>Backend Disconnected:</strong> Displaying offline historical telemetry cache. Live dynamic queries and model calculations are currently unavailable.
              </span>
            </div>
            <button
              onClick={handleManualRetry}
              disabled={isRetrying}
              className="px-3 py-1 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded font-mono font-bold tracking-wider transition-colors"
            >
              {isRetrying ? "RECONNECTING..." : "RETRY CONNECTION"}
            </button>
          </div>
        )}
        {/* Judge Demo Banner (if active) */}
        {isJudgeMode && (
          <JudgeDemoMode
            onStepSelect={(tabId, sol) => handleNavigate(tabId, sol)}
            onExit={() => setIsJudgeMode(false)}
          />
        )}

        {/* Tab Content with Module Error Boundaries */}
        {activeTab === "overview" && (
          <ErrorBoundary fallbackTitle="MISSION OVERVIEW STREAM INTERRUPTED">
            <MissionOverview data={overviewData} onNavigate={handleNavigate} />
          </ErrorBoundary>
        )}

        {activeTab === "explorer" && (
          <ErrorBoundary fallbackTitle="MULTI-MISSION DATA EXPLORER INTERRUPTED">
            <MultiMissionExplorer />
          </ErrorBoundary>
        )}

        {activeTab === "atmospheric" && (
          <ErrorBoundary fallbackTitle="VERTICAL ATMOSPHERIC PROFILES INTERRUPTED">
            <VerticalProfileViewer />
          </ErrorBoundary>
        )}

        {activeTab === "anomaly" && (
          <ErrorBoundary fallbackTitle="MARS ANOMALY INTELLIGENCE INTERRUPTED">
            <AnomalyTimeline 
              initialReplaySol={selectedReplaySol}
              onClearReplay={() => setSelectedReplaySol(null)}
            />
          </ErrorBoundary>
        )}

        {activeTab === "map" && (
          <ErrorBoundary fallbackTitle="MARS SPATIAL ENVIRONMENT MAP INTERRUPTED">
            <MarsEnvironmentMap />
          </ErrorBoundary>
        )}

        {activeTab === "meci" && (
          <ErrorBoundary fallbackTitle="CHALLENGE INDEX ENGINE INTERRUPTED">
            <ChallengeIndexCard />
          </ErrorBoundary>
        )}

        {activeTab === "model" && (
          <ErrorBoundary fallbackTitle="ML MODEL LAB INTERRUPTED">
            <ModelLab />
          </ErrorBoundary>
        )}

        {activeTab === "ai" && (
          <ErrorBoundary fallbackTitle="GROUNDED AI SCIENTIST INTERRUPTED">
            <MarsAIScientist onNavigate={handleNavigate} />
          </ErrorBoundary>
        )}

        {activeTab === "catalog" && (
          <ErrorBoundary fallbackTitle="NASA DATA CATALOG INTERRUPTED">
            <DataCatalog />
          </ErrorBoundary>
        )}

        {activeTab === "notebook" && (
          <ErrorBoundary fallbackTitle="SCIENCE NOTEBOOK INTERRUPTED">
            <ScienceNotebook />
          </ErrorBoundary>
        )}
      </main>

      {/* Scientific Footer */}
      <footer className="border-t border-mars-border/60 bg-mars-darkest px-6 py-6 text-xs font-mono text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-mars-amber" />
            <span className="text-slate-300 font-bold">MARS MISSION INTELLIGENCE</span>
            <span>— NASA Space Apps Challenge Prototype</span>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-[11px]">
            <span className="text-slate-400">Sources: NASA MSL REMS, InSight TWINS/APSS, MRO MCS</span>
            <span>|</span>
            <span className="text-mars-cyan">Authoritative PDS Data Grounded</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
