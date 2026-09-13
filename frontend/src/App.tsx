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
import { MissionOverviewData } from "./lib/types";
import { api } from "./lib/api";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [isJudgeMode, setIsJudgeMode] = useState<boolean>(false);
  const [overviewData, setOverviewData] = useState<MissionOverviewData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    api.getOverview()
      .then((res) => {
        if (isMounted) {
          setOverviewData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.warn("Using fallback overview data:", err);
        setLoading(false);
      });
    return () => { isMounted = false; };
  }, []);

  const handleNavigate = (tabId: string, sol?: number) => {
    setActiveTab(tabId);
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
        systemStatus={overviewData?.system_status || "OPERATIONAL"}
        dataFreshness={overviewData?.data_freshness || "REAL NASA TELEMETRY CACHED"}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-3 md:px-6 md:py-4 space-y-4">
        {/* Judge Demo Banner (if active) */}
        {isJudgeMode && (
          <JudgeDemoMode
            onStepSelect={(tabId) => handleNavigate(tabId)}
            onExit={() => setIsJudgeMode(false)}
          />
        )}

        {/* Tab Content */}
        {activeTab === "overview" && (
          <MissionOverview data={overviewData} onNavigate={handleNavigate} />
        )}

        {activeTab === "explorer" && (
          <MultiMissionExplorer />
        )}

        {activeTab === "atmospheric" && (
          <VerticalProfileViewer />
        )}

        {activeTab === "anomaly" && (
          <AnomalyTimeline />
        )}

        {activeTab === "map" && (
          <MarsEnvironmentMap />
        )}

        {activeTab === "meci" && (
          <ChallengeIndexCard />
        )}

        {activeTab === "model" && (
          <ModelLab />
        )}

        {activeTab === "ai" && (
          <MarsAIScientist onNavigate={handleNavigate} />
        )}

        {activeTab === "catalog" && (
          <DataCatalog />
        )}

        {activeTab === "notebook" && (
          <ScienceNotebook />
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
