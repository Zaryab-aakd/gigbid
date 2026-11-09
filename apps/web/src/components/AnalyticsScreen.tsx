import React from "react";
import { AnalyticsData } from "../types";

interface AnalyticsScreenProps {
  data: AnalyticsData;
}

export const AnalyticsScreen: React.FC<AnalyticsScreenProps> = ({ data }) => {
  return (
    <div className="space-y-6">
      <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
        <h1 className="text-xl font-bold text-slate-100">Performance & R&D Metrics</h1>
        <p className="text-xs text-slate-400">
          Conversion funnels, Connects ROI, latency benchmarks, and rejection taxonomy.
        </p>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Client Reply Rate</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {data.reply_rate_pct}%
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Benchmark against GigSim clients</div>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Hire Win Rate</div>
          <div className="text-2xl font-bold text-cyan-400 mt-1">
            {data.hire_rate_pct}%
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Proposals converted to contracts</div>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Connects ROI Multiplier</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">
            {data.connects_roi}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Revenue per Connect spent</div>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">p95 Analysis Latency</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {data.avg_latency_seconds}s
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Cost: ${data.cost_per_proposal_usd} (Open profile)</div>
        </div>
      </div>

      {/* Rejection Taxonomy Breakdown */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3">
        <h3 className="text-sm font-semibold text-slate-200">
          Proposal Outcome & Rejection Taxonomy
        </h3>
        <p className="text-xs text-slate-400">
          Empirical failure taxonomy grouped across development evaluation runs.
        </p>

        <div className="space-y-2.5 pt-2">
          {data.rejection_breakdown.map((item, idx) => (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300">{item.reason}</span>
                <span className="text-slate-400 font-mono">{item.pct}%</span>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-full"
                  style={{ width: `${item.pct}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
