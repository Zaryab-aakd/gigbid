import React from "react";
import { UserProfileData } from "../types";

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  profile: UserProfileData | null;
  onSwitchPersona: (persona: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  profile,
  onSwitchPersona
}) => {
  const tabs = [
    { id: "inbox", label: "Job Inbox" },
    { id: "pipeline", label: "Pipeline Kanban" },
    { id: "messages", label: "Client Messages" },
    { id: "stream", label: "Agent Live Stream" },
    { id: "analytics", label: "R&D Analytics" },
    { id: "settings", label: "Settings & Memory" },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-indigo-500 bg-clip-text text-transparent">
              GigBid
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 font-mono">
              AI-4016 Copilot
            </span>
          </div>

          <nav className="hidden md:flex space-x-1 pl-4">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setCurrentTab(t.id)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                  currentTab === t.id
                    ? "bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                {t.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="flex items-center space-x-4">
          {/* Persona selector */}
          <select
            value={profile?.user.active_persona || "ai_ml_engineer"}
            onChange={(e) => onSwitchPersona(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="ai_ml_engineer">AI/ML Engineer</option>
            <option value="full_stack_developer">Full-Stack Engineer</option>
            <option value="data_analyst">Data Analyst</option>
          </select>

          {/* Connects Badge */}
          <div className="flex items-center space-x-1.5 bg-slate-900 border border-slate-800 rounded-full px-3 py-1 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-400">Connects:</span>
            <span className="font-semibold text-emerald-400">
              {profile?.connects.current_balance ?? 150}
            </span>
          </div>

          {/* Mode Pill */}
          <div className="hidden sm:block text-xs px-2 py-0.5 rounded border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
            {profile?.user.marketplace_mode.toUpperCase() || "GIGSIM"}
          </div>
        </div>
      </div>
    </header>
  );
};
