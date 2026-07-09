import React from 'react';
import Badge from '../components/ui/Badge';
import { FlaskConical, Beaker, Library, Trophy } from 'lucide-react';

export default function ResearchLab() {
  const experiments = [
    { id: "EXP-902", status: "Running", factor: "Order Book Imbalance", cagr: "+12.4%", draw: "4.1%" },
    { id: "EXP-901", status: "Completed", factor: "Sentiment + VCP", cagr: "+28.1%", draw: "2.4%" },
    { id: "EXP-900", status: "Failed", factor: "RSI Mean Reversion", cagr: "-4.2%", draw: "12.8%" },
  ];

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
            <FlaskConical className="text-[var(--accent-primary)]" />
            Autonomous Research Lab
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">Phase 11: Continuous discovery of new alpha factors</p>
        </div>
        <button className="btn btn-primary">Start New Experiment</button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        {/* Active Experiments */}
        <div className="glass-panel p-5 flex flex-col">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Beaker size={18} /> Recent Experiments
          </h3>
          <div className="flex flex-col gap-3">
            {experiments.map(exp => (
              <div key={exp.id} className="p-4 bg-[rgba(255,255,255,0.02)] rounded-lg border border-[var(--glass-border)] flex justify-between items-center">
                <div>
                  <div className="font-bold text-[var(--accent-primary)]">{exp.id}</div>
                  <div className="text-sm text-[var(--text-secondary)]">{exp.factor}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold text-[var(--signal-up)]">{exp.cagr} CAGR</div>
                  <div className="text-xs text-[var(--text-secondary)]">Max DD: {exp.draw}</div>
                </div>
                <Badge variant={exp.status === 'Running' ? 'primary' : exp.status === 'Completed' ? 'success' : 'danger'}>
                  {exp.status}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Feature Store / Leaderboard */}
        <div className="flex flex-col gap-6">
          <div className="glass-panel p-5 flex-1">
            <h3 className="font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <Trophy size={18} className="text-yellow-400" /> Alpha Leaderboard
            </h3>
            <ul className="space-y-4">
              <li className="flex justify-between items-center border-b border-[var(--glass-border)] pb-2">
                <span className="text-sm font-medium">1. Volatility Contraction Pattern (VCP)</span>
                <span className="text-sm text-[var(--signal-up)] font-bold">Sharpe 2.4</span>
              </li>
              <li className="flex justify-between items-center border-b border-[var(--glass-border)] pb-2">
                <span className="text-sm font-medium">2. Sector Momentum Rotation</span>
                <span className="text-sm text-[var(--signal-up)] font-bold">Sharpe 2.1</span>
              </li>
              <li className="flex justify-between items-center">
                <span className="text-sm font-medium">3. Institutional Block Deals</span>
                <span className="text-sm text-[var(--signal-up)] font-bold">Sharpe 1.9</span>
              </li>
            </ul>
          </div>
          
          <div className="glass-panel p-5 flex-1 bg-[rgba(139,148,158,0.1)]">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2 flex items-center gap-2">
              <Library size={18} /> Feature Store Registry
            </h3>
            <p className="text-sm text-[var(--text-secondary)] mb-4">
              420 engineered features currently tracked across 12 sectors.
            </p>
            <button className="btn w-full">Browse Registry</button>
          </div>
        </div>
      </div>
    </div>
  );
}
