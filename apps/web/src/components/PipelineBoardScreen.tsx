import React from "react";

interface PipelineBoardScreenProps {
  board: Record<string, any[]>;
}

export const PipelineBoardScreen: React.FC<PipelineBoardScreenProps> = ({ board }) => {
  const stages = [
    { id: "drafted", label: "Drafted", color: "border-slate-700" },
    { id: "submitted", label: "Submitted", color: "border-cyan-500/40" },
    { id: "viewed", label: "Viewed by Client", color: "border-indigo-500/40" },
    { id: "replied", label: "Replied", color: "border-amber-500/40" },
    { id: "interview", label: "Interview", color: "border-teal-500/40" },
    { id: "hired", label: "Hired (Won)", color: "border-emerald-500/40" },
    { id: "lost", label: "Closed / Lost", color: "border-rose-500/40" }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
        <h1 className="text-xl font-bold text-slate-100">Marketplace Pipeline Kanban</h1>
        <p className="text-xs text-slate-400">
          Tracks active proposals through submission, client replies, interview booking, and contract awards.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-7 gap-3 overflow-x-auto min-h-[500px]">
        {stages.map((st) => {
          const cards = board[st.id] || [];
          return (
            <div
              key={st.id}
              className="bg-slate-950/70 border border-slate-800 rounded-xl p-3 flex flex-col space-y-3"
            >
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-xs font-bold text-slate-300">{st.label}</span>
                <span className="text-[10px] bg-slate-900 border border-slate-800 text-slate-400 px-1.5 py-0.5 rounded-full font-mono">
                  {cards.length}
                </span>
              </div>

              <div className="space-y-2.5 flex-1">
                {cards.length === 0 ? (
                  <div className="text-[11px] text-slate-600 text-center py-6">
                    No cards
                  </div>
                ) : (
                  cards.map((c, idx) => (
                    <div
                      key={idx}
                      className={`bg-slate-900/90 border ${st.color} rounded-lg p-3 space-y-1.5 shadow-sm text-xs`}
                    >
                      <div className="font-semibold text-slate-200 line-clamp-2">
                        {c.title}
                      </div>
                      {c.bid_amount && (
                        <div className="text-cyan-400 font-mono text-[11px]">
                          ${c.bid_amount} USD
                        </div>
                      )}
                      {c.submitted_at && (
                        <div className="text-slate-500 text-[10px] font-mono">
                          {new Date(c.submitted_at).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
