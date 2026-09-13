import React, { useState, useEffect } from "react";
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Clock, 
  AlertTriangle, 
  Thermometer, 
  Gauge, 
  ChevronRight,
  Info
} from "lucide-react";
import { EventReplayData } from "../../lib/types";
import { api } from "../../lib/api";

interface EventReplayProps {
  targetSol: number;
  onClose?: () => void;
}

export const EventReplay: React.FC<EventReplayProps> = ({ targetSol, onClose }) => {
  const [replayData, setReplayData] = useState<EventReplayData | null>(null);
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(12); // Default to center anomaly
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getEventReplay(targetSol)
      .then((res) => {
        if (isMounted) {
          setReplayData(res);
          const centerIdx = res.replay_timeline.findIndex((p) => p.is_anomaly_center);
          setCurrentStepIdx(centerIdx !== -1 ? centerIdx : 12);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load event replay:", err);
        setLoading(false);
      });
    return () => { isMounted = false; };
  }, [targetSol]);

  // Automated Playback Timer
  useEffect(() => {
    let interval: any = null;
    if (isPlaying && replayData) {
      interval = setInterval(() => {
        setCurrentStepIdx((prev) => {
          if (prev >= replayData.replay_timeline.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1200);
    }
    return () => clearInterval(interval);
  }, [isPlaying, replayData]);

  if (loading || !replayData) {
    return (
      <div className="p-8 text-center font-mono text-xs text-slate-400">
        Reconstructing Martian Environmental Event (Sol {targetSol})...
      </div>
    );
  }

  const timeline = replayData.replay_timeline;
  const currentPoint = timeline[currentStepIdx] || timeline[0];
  const offset = currentPoint.offset_sols;

  // Narrative based on phase
  let phaseLabel = "T - 0 (ANOMALY EVENT PEAK)";
  let phaseNarrative = replayData.narrative.anomaly_event;
  let phaseColor = "text-mars-rust";

  if (offset < -3) {
    phaseLabel = `T ${offset} SOLS (PRE-EVENT STABLE REGIME)`;
    phaseNarrative = replayData.narrative.pre_event;
    phaseColor = "text-sky-400";
  } else if (offset > 3) {
    phaseLabel = `T +${offset} SOLS (POST-EVENT EQUILIBRATION)`;
    phaseNarrative = replayData.narrative.post_event;
    phaseColor = "text-emerald-400";
  }

  return (
    <div className="bg-mars-darkest border border-mars-amber/50 rounded-xl p-6 shadow-glow-amber space-y-6">
      {/* Replay Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-mars-border pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-mars-amber font-bold">
            <span className="w-2 h-2 rounded-full bg-mars-amber animate-ping" />
            SIGNATURE EVENT REPLAY: MARS DUST & PRESSURE RECONSTRUCTION
          </div>
          <h2 className="text-xl font-bold font-mono text-white mt-1">
            {replayData.event_type} — Sol {replayData.target_sol}
          </h2>
          <div className="text-xs text-slate-400 font-mono">
            Mission: {replayData.mission} | Site: {replayData.site} | Earth Date: {replayData.terrestrial_date}
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="px-3 py-1 bg-mars-panel hover:bg-mars-surface border border-mars-border text-slate-300 rounded font-mono text-xs"
          >
            Close Replay
          </button>
        )}
      </div>

      {/* Scrub Bar & Player Controls (Directive 60) */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-3 py-1.5 rounded bg-mars-amber hover:bg-mars-rust text-white font-bold flex items-center gap-1.5 transition-colors"
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              <span>{isPlaying ? "PAUSE" : "PLAY TIMELINE"}</span>
            </button>
            <button
              onClick={() => { setIsPlaying(false); setCurrentStepIdx(0); }}
              className="p-1.5 rounded bg-mars-surface border border-mars-border text-slate-400 hover:text-white"
              title="Rewind to T - 12 Sols"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex items-center gap-2 text-slate-300">
            <Clock className="w-3.5 h-3.5 text-mars-cyan" />
            <span className={`font-bold ${phaseColor}`}>{phaseLabel}</span>
          </div>
        </div>

        {/* Timeline Slider Track */}
        <div className="space-y-1">
          <input
            type="range"
            min={0}
            max={timeline.length - 1}
            value={currentStepIdx}
            onChange={(e) => {
              setIsPlaying(false);
              setCurrentStepIdx(Number(e.target.value));
            }}
            className="w-full h-2 bg-mars-surface rounded-lg appearance-none cursor-pointer accent-mars-amber"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>T - 12 Sols ({timeline[0]?.sol})</span>
            <span className="text-mars-amber font-bold">Event Center (Sol {targetSol})</span>
            <span>T + 12 Sols ({timeline[timeline.length - 1]?.sol})</span>
          </div>
        </div>
      </div>

      {/* Dynamic Telemetry Gauges at Current Replay Step */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
        <div className="p-3 bg-mars-panel border border-mars-border rounded-lg space-y-1">
          <span className="text-slate-400 text-[10px]">CURRENT STEP SOL</span>
          <div className="text-lg font-bold text-mars-amber">Sol {currentPoint.sol}</div>
          <div className="text-[10px] text-slate-500">{currentPoint.terrestrial_date}</div>
        </div>

        <div className="p-3 bg-mars-panel border border-mars-border rounded-lg space-y-1">
          <span className="text-slate-400 text-[10px]">ATMOSPHERIC PRESSURE</span>
          <div className="text-lg font-bold text-white flex items-baseline gap-1">
            <Gauge className="w-3.5 h-3.5 text-sky-400 inline mr-1" />
            <span>{currentPoint.pressure_pa ?? "--"}</span>
            <span className="text-[10px] text-slate-400">Pa</span>
          </div>
          <div className="text-[10px] text-slate-500">Surface Sensor</div>
        </div>

        <div className="p-3 bg-mars-panel border border-mars-border rounded-lg space-y-1">
          <span className="text-slate-400 text-[10px]">DIURNAL THERMAL SWING</span>
          <div className="text-lg font-bold text-rose-400 flex items-baseline gap-1">
            <Thermometer className="w-3.5 h-3.5 inline mr-1" />
            <span>Δ {currentPoint.temp_amplitude_c ?? "--"}</span>
            <span className="text-[10px] text-slate-400">°C</span>
          </div>
          <div className="text-[10px] text-slate-500">Peak Thermal Stress</div>
        </div>

        <div className="p-3 bg-mars-panel border border-mars-border rounded-lg space-y-1">
          <span className="text-slate-400 text-[10px]">OFFSET FROM EVENT</span>
          <div className={`text-lg font-bold ${phaseColor}`}>
            {offset === 0 ? "PEAK (T-0)" : `${offset > 0 ? "+" : ""}${offset} Sols`}
          </div>
          <div className="text-[10px] text-slate-500">Temporal Phase</div>
        </div>
      </div>

      {/* Dynamic Scientific Narrative Card */}
      <div className="p-4 bg-mars-panel border border-mars-border rounded-lg space-y-2">
        <div className="flex items-center gap-2 text-xs font-mono text-mars-cyan font-bold">
          <Info className="w-4 h-4" />
          <span>SCIENTIFIC EVENT RECONSTRUCTION NARRATIVE</span>
        </div>
        <p className="text-xs md:text-sm text-slate-200 leading-relaxed font-sans">
          {phaseNarrative}
        </p>
      </div>
    </div>
  );
};
