import React from "react";
import { JobDetailData } from "../types";

interface JobDetailScreenProps {
  data: JobDetailData;
  onBack: () => void;
  onRunAgent: (jobId: string) => void;
}

export const JobDetailScreen: React.FC<JobDetailScreenProps> = ({
  data,
  onBack,
  onRunAgent
}) => {
  const { job, client, requirement_evidence_matrix } = data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="text-xs text-slate-400 hover:text-slate-200 flex items-center space-x-1"
        >
          <span>← Back to Inbox</span>
        </button>

        <button
          onClick={() => onRunAgent(job.job_id)}
          className="text-xs bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-medium px-4 py-2 rounded-lg shadow-sm"
        >
          Run LangGraph Copilot Analysis
        </button>
      </div>

      {/* Header Card */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h1 className="text-xl font-bold text-slate-100">{job.title}</h1>
          <div className="text-sm font-semibold text-cyan-400">
            ${job.budget.min} - ${job.budget.max} {job.budget.currency}
          </div>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
          {job.description}
        </p>

        {job.screening_questions && job.screening_questions.length > 0 && (
          <div className="pt-2 border-t border-slate-800">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Screening Questions:
            </h4>
            <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
              {job.screening_questions.map((q, idx) => (
                <li key={idx}>{q}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Client Profile Breakdown */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">
          Client Marketplace Background
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div className="text-slate-500">Total Spend</div>
            <div className="text-slate-200 font-semibold text-sm">
              ${client.total_spend.toLocaleString()}
            </div>
          </div>
          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div className="text-slate-500">Hire Rate</div>
            <div className="text-slate-200 font-semibold text-sm">
              {Math.round(client.hire_rate * 100)}% ({client.hires} hires)
            </div>
          </div>
          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div className="text-slate-500">Rating</div>
            <div className="text-amber-400 font-semibold text-sm">
              ★ {client.rating.toFixed(1)} / 5.0
            </div>
          </div>
          <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div className="text-slate-500">Payment Status</div>
            <div className="text-emerald-400 font-semibold text-sm">
              {client.payment_verified ? "Verified" : "Unverified"}
            </div>
          </div>
        </div>
      </div>

      {/* Requirement-to-Evidence Matrix */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">
            Requirement-to-Evidence Grounding Matrix
          </h3>
          <p className="text-xs text-slate-400">
            Every technical ask must map to verifiable portfolio items to ensure R5 zero-hallucination compliance.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-medium">
                <th className="py-2.5 px-3">Job Requirement</th>
                <th className="py-2.5 px-3">Matched Evidence ID</th>
                <th className="py-2.5 px-3">Case Study Title</th>
                <th className="py-2.5 px-3">Documented Outcome</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {requirement_evidence_matrix.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40">
                  <td className="py-2.5 px-3 font-semibold text-slate-200">
                    {row.requirement}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-cyan-400">
                    {row.matched_evidence_id}
                  </td>
                  <td className="py-2.5 px-3 text-slate-300">
                    {row.evidence_title}
                  </td>
                  <td className="py-2.5 px-3 text-slate-400">
                    {row.outcome}
                  </td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-medium border ${
                        row.status === "grounded"
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                          : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                      }`}
                    >
                      {row.status.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
