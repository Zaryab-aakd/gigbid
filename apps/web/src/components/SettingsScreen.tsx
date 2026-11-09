import React, { useState } from "react";
import { LearnedMemoryItem, UserProfileData } from "../types";

interface SettingsScreenProps {
  profile: UserProfileData | null;
  memories: LearnedMemoryItem[];
  onDeleteMemory: (memoryId: string) => void;
}

export const SettingsScreen: React.FC<SettingsScreenProps> = ({
  profile,
  memories,
  onDeleteMemory
}) => {
  const [autonomy, setAutonomy] = useState("collaborative");
  const [budget, setBudget] = useState(80);

  return (
    <div className="space-y-6">
      <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
        <h1 className="text-xl font-bold text-slate-100">Settings & Memory Inspector</h1>
        <p className="text-xs text-slate-400">
          Configure copilot autonomy levels, weekly budgets, and view or delete promoted long-term rules.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System & Autonomy Settings */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200">Copilot Safeguards & Budgets</h3>

          <div className="space-y-2">
            <label className="text-xs text-slate-400">Autonomy Tier</label>
            <select
              value={autonomy}
              onChange={(e) => setAutonomy(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
            >
              <option value="collaborative">
                Collaborative (Interrupt on every proposal, message, and Connects spend) - RECOMMENDED
              </option>
              <option value="conservative">
                Conservative (Auto-skip low fit / scams; require approval on proposals only)
              </option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-slate-400">Weekly Connects Budget</label>
            <input
              type="number"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
            />
            <p className="text-[11px] text-slate-500">
              Graph decision node automatically skips jobs when weekly Connects budget limit is reached.
            </p>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-800">
            <div className="text-xs font-semibold text-slate-300">Connected Marketplace Accounts</div>
            <div className="flex items-center justify-between p-2.5 bg-slate-900/60 rounded border border-slate-800 text-xs">
              <span className="text-slate-300">GigSim Local Simulator</span>
              <span className="text-emerald-400 font-mono text-[10px]">CONNECTED</span>
            </div>
            <div className="flex items-center justify-between p-2.5 bg-slate-900/60 rounded border border-slate-800 text-xs">
              <span className="text-slate-300">Upwork Live MCP (OAuth 2.1)</span>
              <span className="text-slate-500 font-mono text-[10px]">STANDBY</span>
            </div>
          </div>
        </div>

        {/* Memory Viewer & Deletion Controls */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Long-Term Memory Viewer</h3>
              <p className="text-xs text-slate-400">
                Rule-promoted memories learned from user edits and winning proposals.
              </p>
            </div>
            <span className="text-xs text-cyan-400 font-mono">{memories.length} rules active</span>
          </div>

          <div className="space-y-2.5">
            {memories.length === 0 ? (
              <div className="text-center py-10 text-slate-500 text-xs">
                No promoted memory items yet.
              </div>
            ) : (
              memories.map((m) => (
                <div
                  key={m.memory_id}
                  className="bg-slate-900 border border-slate-800 rounded-lg p-3 space-y-1.5 flex items-start justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 px-1.5 py-0.2 rounded font-mono">
                        {m.type.toUpperCase()}
                      </span>
                      <span className="text-slate-200 font-semibold">{m.rule || m.outcome}</span>
                    </div>
                    <div className="text-slate-400 text-[11px]">
                      {m.preference || `Outcome: ${m.outcome} on evidence ${m.evidence_id || m.evidence_ids?.join(", ")}`}
                    </div>
                    <div className="text-[10px] text-slate-600 font-mono">
                      Learned: {new Date(m.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  <button
                    onClick={() => onDeleteMemory(m.memory_id)}
                    className="text-[10px] bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 px-2 py-1 rounded transition"
                  >
                    Delete Rule
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
