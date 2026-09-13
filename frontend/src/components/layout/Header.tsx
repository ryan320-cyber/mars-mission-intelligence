import React, { useState, useEffect } from "react";
import { 
  Compass, 
  Activity, 
  BarChart3, 
  AlertTriangle, 
  MapPin, 
  ShieldAlert, 
  BrainCircuit, 
  Bot, 
  Database, 
  BookOpen, 
  Award,
  Radio
} from "lucide-react";

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isJudgeMode: boolean;
  setIsJudgeMode: (active: boolean) => void;
  systemStatus?: string;
  dataFreshness?: string;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  isJudgeMode,
  setIsJudgeMode,
  systemStatus = "OPERATIONAL",
  dataFreshness = "AUTHORITATIVE NASA PDS"
}) => {
  const [utcTime, setUtcTime] = useState<string>("");

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setUtcTime(now.toISOString().replace("T", " ").substring(0, 19) + " UTC");
    };
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, []);

  const navItems = [
    { id: "overview", label: "01 Overview", icon: Activity },
    { id: "explorer", label: "02 Explorer", icon: Compass },
    { id: "atmospheric", label: "03 Atmosphere", icon: BarChart3 },
    { id: "anomaly", label: "04 Anomalies", icon: AlertTriangle },
    { id: "map", label: "05 Mars Map", icon: MapPin },
    { id: "meci", label: "06 Challenge Index", icon: ShieldAlert },
    { id: "model", label: "07 Model Lab", icon: BrainCircuit },
    { id: "ai", label: "08 AI Scientist", icon: Bot },
    { id: "catalog", label: "09 Data Catalog", icon: Database },
    { id: "notebook", label: "10 Methodology", icon: BookOpen },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-mars-border bg-mars-darkest/95 backdrop-blur-md">
      {/* Top Banner: Telemetry & Mission Control Metadata */}
      <div className="flex flex-wrap items-center justify-between px-4 py-2 border-b border-mars-border/60 text-xs font-mono">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-mars-amber font-semibold tracking-wider uppercase">
            <Radio className="w-3.5 h-3.5 text-mars-rust animate-pulse" />
            NASA Space Apps Challenge
          </span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-400">PLANETARY SCIENCE DIVISION</span>
          <span className="text-slate-500">|</span>
          <span className="text-mars-cyan">{dataFreshness}</span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-emerald-400 font-bold">{systemStatus}</span>
          </div>
          <span className="text-slate-400">{utcTime}</span>
          <button
            onClick={() => setIsJudgeMode(!isJudgeMode)}
            className={`flex items-center gap-1.5 px-3 py-1 rounded font-bold transition-all ${
              isJudgeMode 
                ? "bg-mars-amber text-white shadow-glow-amber ring-2 ring-mars-amber/50" 
                : "bg-mars-panel text-slate-300 hover:text-white border border-mars-border hover:border-mars-amber"
            }`}
          >
            <Award className="w-3.5 h-3.5" />
            <span>JUDGE DEMO MODE</span>
          </button>
        </div>
      </div>

      {/* Main Title & Nav Bar */}
      <div className="px-4 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-mars-rust to-mars-amber flex items-center justify-center shadow-glow-amber">
            <span className="font-bold text-white tracking-widest text-sm">♂</span>
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              MARS MISSION INTELLIGENCE
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-mars-surface border border-mars-border text-slate-400 font-mono">
                v1.0.0
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Multi-Mission Environmental Analytics, Machine Learning & Grounded AI
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? "bg-mars-surface text-mars-cyan border border-mars-cyan/40 shadow-glow-cyan"
                    : "text-slate-400 hover:text-slate-200 hover:bg-mars-panel"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
