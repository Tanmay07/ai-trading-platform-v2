import React from 'react';
import Badge from '../components/ui/Badge';
import { Gavel, CheckCircle, XCircle } from 'lucide-react';

export default function StrategyCenter() {
  const strategies = [
    { id: "Swing Breakout", version: "v2.1", status: "Production", capital: "40%", health: "Healthy" },
    { id: "Momentum", version: "v1.4", status: "Production", capital: "35%", health: "Warning" },
    { id: "Mean Reversion", version: "v1.0", status: "Candidate", capital: "0%", health: "Testing" },
  ];

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
            <Gavel className="text-[var(--accent-primary)]" />
            Strategy Governance
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">Phase 12: Strategy Promotion, Demotion, and Capital Bounds</p>
        </div>
      </div>

      <div className="glass-panel flex-1 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-[var(--glass-border)] bg-[rgba(0,0,0,0.1)] flex justify-between items-center">
          <h3 className="font-semibold text-[var(--text-primary)]">Strategy Marketplace</h3>
          <span className="text-xs text-[var(--text-secondary)]">Total Capital Allocated: 75% / 100%</span>
        </div>
        <div className="overflow-auto p-4">
          <table className="w-full text-sm text-left">
            <thead className="text-[var(--text-secondary)] border-b border-[var(--glass-border)]">
              <tr>
                <th className="px-4 py-3 font-medium">Strategy</th>
                <th className="px-4 py-3 font-medium">Version</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Max Capital</th>
                <th className="px-4 py-3 font-medium">Health</th>
                <th className="px-4 py-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--glass-border)]">
              {strategies.map((s) => (
                <tr key={s.id} className="hover:bg-[rgba(255,255,255,0.02)] transition-colors">
                  <td className="px-4 py-4 font-bold text-[var(--text-primary)]">{s.id}</td>
                  <td className="px-4 py-4">{s.version}</td>
                  <td className="px-4 py-4"><Badge variant={s.status === 'Production' ? 'primary' : 'neutral'}>{s.status}</Badge></td>
                  <td className="px-4 py-4 font-mono">{s.capital}</td>
                  <td className="px-4 py-4"><Badge variant={s.health === 'Healthy' ? 'success' : s.health === 'Warning' ? 'warning' : 'neutral'}>{s.health}</Badge></td>
                  <td className="px-4 py-4">
                    {s.status === 'Candidate' ? (
                      <button className="flex items-center gap-1 text-[var(--signal-up)] hover:text-green-400 font-bold transition-colors">
                        <CheckCircle size={16} /> Promote
                      </button>
                    ) : (
                      <button className="flex items-center gap-1 text-[var(--signal-down)] hover:text-red-400 font-bold transition-colors">
                        <XCircle size={16} /> Demote
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
