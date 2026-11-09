import React, { useEffect, useState } from "react";

interface NodeEvent {
  node: string;
  timestamp: string;
  status: string;
  decision?: string;
  reason?: string;
  recommended_bid?: number;
  preview_opening?: string;
  supported_claims?: number;
  unsupported_claims?: number;
  passed?: boolean;
  score?: number;
}

interface AgentRunViewerScreenProps {
  jobId: string;
  onOpenStudio: (threadId: string) => void;
  onBack: () => void;
}

export const AgentRunViewerScreen: React.FC<AgentRunViewerScreenProps> = ({
  jobId,
  onOpenStudio,
  onBack
}) => {
  const [events, setEvents] = useState<NodeEvent[]>([]);
  const [isInterrupt, setIsInterrupt] = useState(false);
  const [threadId, setThreadId] = useState<string>(`thread-bid-${jobId}`);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(`http://localhost:8000/api/stream/bid/${jobId}`);

    eventSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.event === "start") {
          setThreadId(data.thread_id);
        } else if (data.event === "node_update") {
          setEvents((prev) => [...prev, data.payload]);
        } else if (data.event === "interrupt_pending_approval") {
          setIsInterrupt(true);
        } else if (data.event === "finished") {
          setIsComplete(true);
          eventSource.close();
        }
      } catch (err) {
        console.error("SSE parse error", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE connection error", err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="text-xs text-slate-400 hover:text-slate-200"
        >
          ← Back to Inbox
        </button>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-500 font-mono">Thread ID: {threadId}</span>
        </div>
      </div>

      {/* Header Banner */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100">
            Live LangGraph Multi-Agent Execution Stream
          </h2>
          <p className="text-xs text-slate-400">
            Parallel fanout analysis, bounded critique loops, claim verification, and checkpointed state updates.
          </p>
        </div>

        {isInterrupt ? (
          <button
            onClick={() => onOpenStudio(threadId)}
            className="text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-4 py-2 rounded-lg shadow-lg animate-pulse"
          >
            Review & Approve in Studio →
          </button>
        ) : isComplete ? (
          <span className="text-xs px-3 py-1 rounded bg-slate-800 text-slate-300 font-mono">
            Execution Completed
          </span>
        ) : (
          <div className="flex items-center space-x-2 text-xs text-cyan-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            <span>Streaming Graph Nodes...</span>
          </div>
        )}
      </div>

      {/* Node Progress Timeline */}
      <div className="space-y-3">
        {events.map((ev, idx) => (
          <div
            key={idx}
            className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex items-start justify-between gap-4"
          >
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">
                  Node: {ev.node}
                </span>
                <span className="text-[10px] text-slate-500 font-mono">
                  {new Date(ev.timestamp).toLocaleTimeString()}
                </span>
              </div>

              {ev.decision && (
                <div className="text-xs text-slate-300">
                  <span className="font-semibold">Decision:</span>{" "}
                  <span className="text-emerald-400 font-bold uppercase">{ev.decision}</span>
                  <div className="text-slate-400 text-[11px] mt-0.5">{ev.reason}</div>
                </div>
              )}

              {ev.recommended_bid && (
                <div className="text-xs text-slate-300">
                  Calculated Optimal Bid: <span className="text-cyan-400 font-bold">${ev.recommended_bid}</span>
                </div>
              )}

              {ev.supported_claims !== undefined && (
                <div className="text-xs text-slate-300">
                  Grounding: <span className="text-emerald-400">{ev.supported_claims} supported</span>,{" "}
                  <span className={ev.unsupported_claims > 0 ? "text-rose-400" : "text-slate-500"}>
                    {ev.unsupported_claims} unsupported
                  </span>
                </div>
              )}

              {ev.passed !== undefined && (
                <div className="text-xs text-slate-300">
                  Critic Evaluation:{" "}
                  <span className={ev.passed ? "text-emerald-400 font-semibold" : "text-amber-400 font-semibold"}>
                    {ev.passed ? "PASSED" : "REVISION REQUIRED"} (Score: {ev.score * 10}/10)
                  </span>
                </div>
              )}
            </div>

            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-mono">
              DONE
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
