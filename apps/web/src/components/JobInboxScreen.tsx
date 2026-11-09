import React, { useState } from "react";
import { JobInboxItem } from "../types";

interface JobInboxScreenProps {
  jobs: JobInboxItem[];
  onSelectJob: (jobId: string) => void;
  onStartAgentRun: (jobId: string) => void;
  loading: boolean;
}

export const JobInboxScreen: React.FC<JobInboxScreenProps> = ({
  jobs,
  onSelectJob,
  onStartAgentRun,
  loading
}) => {
  const [filter, setFilter] = useState<string>("all");
  const [search, setSearch] = useState<string>("");

  const filteredJobs = jobs.filter((j) => {
    if (filter === "safe" && j.risk_badge !== "VERIFIED_SAFE") return false;
    if (filter === "risk" && j.risk_badge === "VERIFIED_SAFE") return false;
    if (search && !j.title.toLowerCase().includes(search.toLowerCase()) && !j.description.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Banner & Filters */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-slate-950 p-4 rounded-xl border border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Scouted Job Feed</h1>
          <p className="text-xs text-slate-400">
            Ranked by portfolio fit & evidence grounding. Scams flagged and prompt injections neutralized.
          </p>
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <input
            type="text"
            placeholder="Search keywords..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500 w-full md:w-48"
          />

          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="all">All Jobs</option>
            <option value="safe">Verified Safe Only</option>
            <option value="risk">Risk / Scam Flagged</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-500">Loading incoming opportunities from GigSim...</div>
      ) : filteredJobs.length === 0 ? (
        <div className="text-center py-20 text-slate-500 bg-slate-950/40 rounded-xl border border-slate-800">
          No job matches found for current filter.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredJobs.map((job) => {
            const isSafe = job.risk_badge === "VERIFIED_SAFE";
            const isInjection = job.risk_badge === "INJECTION_BLOCKED";

            return (
              <div
                key={job.job_id}
                className="bg-slate-950 border border-slate-800 hover:border-slate-700 rounded-xl p-5 transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
              >
                <div className="space-y-2 max-w-3xl">
                  <div className="flex items-center space-x-2.5">
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                        isSafe
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                          : isInjection
                          ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                          : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                      }`}
                    >
                      {job.risk_badge.replace("_", " ")}
                    </span>

                    <span className="text-xs text-slate-400 font-mono">
                      Fit: {Math.round(job.fit_score * 100)}%
                    </span>

                    <span className="text-xs text-slate-500 font-mono">
                      Connects: {job.connects_cost}
                    </span>
                  </div>

                  <h3
                    onClick={() => onSelectJob(job.job_id)}
                    className="text-base font-semibold text-slate-100 hover:text-cyan-400 cursor-pointer"
                  >
                    {job.title}
                  </h3>

                  <p className="text-xs text-slate-400 line-clamp-2">
                    {job.description}
                  </p>

                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {job.required_skills.map((skill, sIdx) => (
                      <span
                        key={sIdx}
                        className="text-[10px] bg-slate-900 border border-slate-800 text-slate-300 px-2 py-0.5 rounded"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-row md:flex-col items-end justify-between w-full md:w-44 gap-2 border-t md:border-t-0 pt-3 md:pt-0 border-slate-800">
                  <div className="text-right">
                    <div className="text-sm font-semibold text-cyan-400">
                      {job.budget_display}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {job.recommended_action}
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => onSelectJob(job.job_id)}
                      className="text-xs bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 px-2.5 py-1.5 rounded-lg transition"
                    >
                      Inspect
                    </button>
                    <button
                      onClick={() => onStartAgentRun(job.job_id)}
                      className="text-xs bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-medium px-3 py-1.5 rounded-lg shadow-sm transition"
                    >
                      Run Copilot
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
