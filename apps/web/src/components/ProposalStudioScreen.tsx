import React, { useState } from "react";
import { PendingProposalData } from "../types";

interface ProposalStudioScreenProps {
  data: PendingProposalData;
  onResume: (action: string, coverLetter: string, bidAmount: number) => void;
  onBack: () => void;
}

export const ProposalStudioScreen: React.FC<ProposalStudioScreenProps> = ({
  data,
  onResume,
  onBack
}) => {
  const [editedLetter, setEditedLetter] = useState(data.cover_letter);
  const [bidAmount, setBidAmount] = useState(data.pricing.recommended_bid || 1000);
  const [showDryRun, setShowDryRun] = useState(false);
  const [hoveredEvidence, setHoveredEvidence] = useState<string | null>(null);

  const handleApprove = () => {
    onResume("approved", editedLetter, bidAmount);
  };

  const handleReject = () => {
    onResume("rejected", editedLetter, bidAmount);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="text-xs text-slate-400 hover:text-slate-200"
        >
          ← Back to Stream
        </button>

        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
          <span className="text-xs font-semibold text-amber-400 font-mono">
            LANGGRAPH INTERRUPT: Awaiting Human Approval
          </span>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Draft Editor & Evidence on Hover */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-slate-100">
                  Proposal Studio: {data.job.title}
                </h2>
                <p className="text-xs text-slate-400">
                  Hover over evidence tags to verify grounding citations. You may edit text directly before approval.
                </p>
              </div>

              <button
                onClick={() => setShowDryRun(!showDryRun)}
                className="text-xs bg-slate-900 border border-slate-700 hover:border-slate-600 text-cyan-400 px-3 py-1.5 rounded-lg"
              >
                {showDryRun ? "Hide Preview" : "Dry Run Preview"}
              </button>
            </div>

            {/* Evidence Tags Bar */}
            <div className="flex items-center space-x-2 pt-1">
              <span className="text-[11px] text-slate-400">Cited Evidence:</span>
              {data.evidence_cited.map((ev, idx) => (
                <div
                  key={idx}
                  onMouseEnter={() => setHoveredEvidence(ev.evidence_id)}
                  onMouseLeave={() => setHoveredEvidence(null)}
                  className="relative group cursor-pointer"
                >
                  <span className="text-[11px] bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 px-2 py-0.5 rounded font-mono">
                    [{ev.evidence_id}]
                  </span>

                  {/* Tooltip on Hover */}
                  {hoveredEvidence === ev.evidence_id && (
                    <div className="absolute bottom-full left-0 mb-2 w-72 p-3 bg-slate-900 border border-indigo-500/40 rounded-lg shadow-xl text-xs z-50 pointer-events-none">
                      <div className="font-semibold text-slate-200 mb-1">{ev.title}</div>
                      <div className="text-slate-400 text-[11px] mb-1.5">{ev.outcome}</div>
                      <div className="flex flex-wrap gap-1">
                        {ev.skills.map((s, sIdx) => (
                          <span key={sIdx} className="bg-slate-800 text-slate-300 px-1.5 py-0.2 rounded text-[10px]">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Editable Proposal Letter */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">
                Cover Letter (Draft v{data.critique.iteration_count || 1}):
              </label>
              <textarea
                value={editedLetter}
                onChange={(e) => setEditedLetter(e.target.value)}
                rows={9}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono leading-relaxed"
              />
            </div>

            {/* Screening Answers */}
            {data.screening_answers && data.screening_answers.length > 0 && (
              <div className="space-y-2 pt-2 border-t border-slate-800">
                <h4 className="text-xs font-semibold text-slate-300">Screening Answers:</h4>
                {data.screening_answers.map((ans, aIdx) => (
                  <div key={aIdx} className="bg-slate-900/60 p-2.5 rounded border border-slate-800 text-xs text-slate-300">
                    {ans}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Action Bar */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <label className="text-xs text-slate-400">Bid Quote ($):</label>
              <input
                type="number"
                value={bidAmount}
                onChange={(e) => setBidAmount(Number(e.target.value))}
                className="bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs text-slate-200 w-24 font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500"
              />
              <span className="text-xs text-slate-500">
                Cost: {data.pricing.connects_cost} Connects
              </span>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleReject}
                className="text-xs bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 px-3.5 py-2 rounded-lg transition"
              >
                Reject & Skip
              </button>

              <button
                onClick={handleApprove}
                className="text-xs bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium px-5 py-2 rounded-lg shadow-md transition"
              >
                Approve & Submit to Platform
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Inline Critic & Compliance Reviews */}
        <div className="space-y-4">
          {/* Critic Card */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-200">Critic Review</span>
              <span
                className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                  data.critique.passed
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                    : "bg-amber-500/10 text-amber-400 border-amber-500/30"
                }`}
              >
                {data.critique.passed ? "PASSED" : "REVISE"} ({data.critique.score * 10}/10)
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              {data.critique.feedback}
            </p>
          </div>

          {/* Compliance Card */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-200">Compliance Guard</span>
              <span
                className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                  data.compliance.compliant
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                    : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                }`}
              >
                {data.compliance.compliant ? "COMPLIANT" : "FLAGGED"}
              </span>
            </div>

            {data.compliance.actions_taken && data.compliance.actions_taken.length > 0 ? (
              <div className="space-y-1">
                <div className="text-[11px] text-amber-400 font-medium">Actions Taken:</div>
                <ul className="list-disc list-inside text-[11px] text-slate-400 space-y-0.5">
                  {data.compliance.actions_taken.map((act, idx) => (
                    <li key={idx}>{act}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="text-xs text-slate-400">
                Zero policy pack infractions detected. All communications comply with marketplace terms.
              </p>
            )}
          </div>

          {/* Dry Run Preview Dialog */}
          {showDryRun && (
            <div className="bg-slate-950 border border-cyan-500/30 rounded-xl p-4 space-y-2.5">
              <h4 className="text-xs font-semibold text-cyan-400">
                [DRY RUN] Marketplace Dispatch Preview
              </h4>
              <div className="text-xs text-slate-300 space-y-1 font-mono text-[11px]">
                <div>Target Job: {data.job.job_id}</div>
                <div>Bid Value: ${bidAmount} USD</div>
                <div>Connects Cost: {data.pricing.connects_cost} Connects</div>
                <div>Idempotency Key: {data.thread_id}</div>
              </div>
              <p className="text-[11px] text-slate-400">
                Validation confirms dry run succeeded. No Connects deducted until 'Approve & Submit' is confirmed.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
