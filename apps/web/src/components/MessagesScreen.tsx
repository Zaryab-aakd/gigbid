import React, { useState } from "react";
import { MessageThreadItem } from "../types";

interface MessagesScreenProps {
  threads: MessageThreadItem[];
}

export const MessagesScreen: React.FC<MessagesScreenProps> = ({ threads }) => {
  const [selectedThread, setSelectedThread] = useState<MessageThreadItem | null>(
    threads[0] || null
  );
  const [replyText, setReplyText] = useState<string>(
    threads[0]?.suggested_reply || ""
  );
  const [sentNotice, setSentNotice] = useState(false);

  const handleSend = () => {
    setSentNotice(true);
    setTimeout(() => setSentNotice(false), 3000);
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
        <h1 className="text-xl font-bold text-slate-100">Client Communications & Liaison</h1>
        <p className="text-xs text-slate-400">
          Client Liaison classifies intent, checks calendar availability via Workspace MCP, and drafts replies.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 min-h-[500px]">
        {/* Threads List */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 space-y-2">
          <div className="text-xs font-semibold text-slate-400 px-2 py-1">Active Threads</div>
          {threads.map((t, idx) => (
            <div
              key={idx}
              onClick={() => {
                setSelectedThread(t);
                setReplyText(t.suggested_reply);
              }}
              className={`p-3 rounded-lg border text-xs cursor-pointer transition ${
                selectedThread?.client_id === t.client_id
                  ? "bg-slate-900 border-cyan-500/50 text-slate-100"
                  : "bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700"
              }`}
            >
              <div className="font-semibold text-slate-200">{t.client_name}</div>
              <div className="text-[11px] text-slate-400 truncate mt-0.5">{t.last_message}</div>
            </div>
          ))}
        </div>

        {/* Message Thread & Suggested Reply */}
        <div className="md:col-span-2 bg-slate-950 border border-slate-800 rounded-xl p-5 flex flex-col justify-between space-y-4">
          {selectedThread ? (
            <>
              <div className="space-y-4">
                <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-slate-100">{selectedThread.client_name}</h3>
                    <span className="text-[10px] text-slate-500 font-mono">Job: {selectedThread.job_id}</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                    INTENT: INTERVIEW REQUEST
                  </span>
                </div>

                {/* Client message bubble */}
                <div className="flex flex-col items-start space-y-1">
                  <div className="text-[10px] text-slate-500">{selectedThread.client_name}</div>
                  <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 max-w-lg">
                    {selectedThread.last_message}
                  </div>
                </div>

                {/* AI suggested reply box */}
                <div className="space-y-2 pt-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-cyan-400 flex items-center space-x-1.5">
                      <span>✨ AI Client Liaison Suggested Reply (Workspace Grounded)</span>
                    </span>
                    <span className="text-[10px] text-slate-500">Requires Human Confirmation</span>
                  </div>

                  <textarea
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    rows={4}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 leading-relaxed font-mono"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-800">
                {sentNotice ? (
                  <span className="text-xs text-emerald-400 font-semibold animate-pulse">
                    ✓ Message Sent & Tentative Calendar Hold Created!
                  </span>
                ) : (
                  <span className="text-[11px] text-slate-500">
                    All sends require approval per R4 platform safety guidelines.
                  </span>
                )}

                <button
                  onClick={handleSend}
                  className="text-xs bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-medium px-4 py-2 rounded-lg shadow transition"
                >
                  Approve & Send Message
                </button>
              </div>
            </>
          ) : (
            <div className="text-center py-20 text-slate-500">No thread selected.</div>
          )}
        </div>
      </div>
    </div>
  );
};
