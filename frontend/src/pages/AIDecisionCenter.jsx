import React from 'react';
import Badge from '../components/ui/Badge';
import { Cpu, Activity, ShieldAlert, BarChart2, CheckCircle, Network, Search, Zap } from 'lucide-react';

export default function AIDecisionCenter() {
  const agents = [
    { name: "Technical Agent", vote: "BUY", conf: 95, icon: <Activity size={20} />, reason: "EMA Alignment, Breakout" },
    { name: "Macro Agent", vote: "BUY", conf: 82, icon: <Network size={20} />, reason: "Favorable Interest Rates" },
    { name: "Risk Agent", vote: "HOLD", conf: 50, icon: <ShieldAlert size={20} />, reason: "VIX slightly elevated" },
    { name: "Portfolio Agent", vote: "BUY", conf: 90, icon: <BarChart2 size={20} />, reason: "Low Correlation to holdings" },
    { name: "Sentiment Agent", vote: "BUY", conf: 88, icon: <Search size={20} />, reason: "Strong Institutional Buying" },
  ];

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center bg-[rgba(88,166,255,0.1)] p-6 rounded-xl border border-[rgba(88,166,255,0.2)]">
        <div>
          <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
            <Cpu className="text-[var(--accent-primary)]" />
            AI Decision Center
          </h1>
          <p className="text-[var(--text-secondary)]">Multi-Agent Consensus Engine actively evaluating: <span className="text-white font-bold">BEL.NS</span></p>
        </div>
        <div className="flex gap-6 text-center">
          <div>
            <div className="text-[var(--text-secondary)] text-sm mb-1">Consensus</div>
            <div className="text-2xl font-bold text-[var(--signal-up)]">89%</div>
          </div>
          <div>
            <div className="text-[var(--text-secondary)] text-sm mb-1">Confidence</div>
            <div className="text-2xl font-bold">92%</div>
          </div>
          <div>
            <div className="text-[var(--text-secondary)] text-sm mb-1">Quality</div>
            <div className="text-2xl font-bold text-[var(--accent-primary)]">A+</div>
          </div>
          <div className="flex items-center">
            <button className="btn btn-primary ml-4">EXECUTE TRADE</button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 flex-1">
        {/* React Flow / Architecture visualization (Mocked with CSS) */}
        <div className="glass-panel col-span-1 xl:col-span-2 p-6 flex flex-col items-center justify-center relative min-h-[400px]">
          <h3 className="absolute top-4 left-4 font-semibold text-[var(--text-secondary)]">Supervisor Architecture</h3>
          
          <div className="flex flex-col items-center w-full max-w-2xl mt-8">
            <div className="px-6 py-3 rounded-full bg-[var(--bg-surface-elevated)] border-2 border-[var(--glass-border)] font-bold shadow-lg z-10 flex items-center gap-2">
              <Zap className="text-[var(--accent-primary)]" size={18} />
              AI Supervisor
            </div>
            
            <div className="w-px h-8 bg-[var(--glass-border)]"></div>
            <div className="w-full h-px bg-[var(--glass-border)] max-w-lg"></div>
            
            <div className="flex justify-between w-full max-w-xl">
              <div className="w-px h-8 bg-[var(--glass-border)]"></div>
              <div className="w-px h-8 bg-[var(--glass-border)]"></div>
              <div className="w-px h-8 bg-[var(--glass-border)]"></div>
            </div>

            <div className="flex justify-between w-full max-w-2xl mt-2 gap-4">
              <div className="glass-panel p-4 flex-1 text-center bg-[rgba(0,0,0,0.2)]">
                <Activity size={24} className="mx-auto mb-2 text-blue-400" />
                <div className="font-bold text-sm">Technical</div>
                <div className="text-xs text-[var(--signal-up)] mt-1">BUY (95%)</div>
              </div>
              <div className="glass-panel p-4 flex-1 text-center bg-[rgba(0,0,0,0.2)]">
                <Network size={24} className="mx-auto mb-2 text-purple-400" />
                <div className="font-bold text-sm">Macro</div>
                <div className="text-xs text-[var(--signal-up)] mt-1">BUY (82%)</div>
              </div>
              <div className="glass-panel p-4 flex-1 text-center bg-[rgba(0,0,0,0.2)]">
                <ShieldAlert size={24} className="mx-auto mb-2 text-yellow-400" />
                <div className="font-bold text-sm">Risk</div>
                <div className="text-xs text-[var(--text-secondary)] mt-1">HOLD (50%)</div>
              </div>
            </div>

            <div className="flex justify-between w-full max-w-xl">
              <div className="w-px h-8 bg-[var(--glass-border)]"></div>
              <div className="w-px h-8 bg-[var(--glass-border)]"></div>
              <div className="w-px h-8 bg-[var(--glass-border)]"></div>
            </div>
            <div className="w-full h-px bg-[var(--glass-border)] max-w-lg"></div>
            <div className="w-px h-8 bg-[var(--glass-border)]"></div>

            <div className="px-8 py-4 rounded-xl bg-gradient-to-r from-[rgba(63,185,80,0.2)] to-[rgba(63,185,80,0.1)] border border-[rgba(63,185,80,0.3)] shadow-[0_0_20px_rgba(63,185,80,0.2)] font-bold text-xl flex items-center gap-3">
              <CheckCircle className="text-[var(--signal-up)]" />
              CONSENSUS: BUY
            </div>
          </div>
        </div>

        {/* Agent Explanations */}
        <div className="flex flex-col gap-4 overflow-y-auto pr-2">
          <h3 className="font-semibold text-[var(--text-secondary)] mb-2">Agent Explanations</h3>
          {agents.map((agent) => (
            <div key={agent.name} className="glass-panel p-4">
              <div className="flex justify-between items-start mb-3 border-b border-[var(--glass-border)] pb-2">
                <div className="flex items-center gap-2 font-bold text-[var(--text-primary)]">
                  <span className="text-[var(--accent-primary)] opacity-80">{agent.icon}</span>
                  {agent.name}
                </div>
                <Badge variant={agent.vote === 'BUY' ? 'success' : 'neutral'}>{agent.vote}</Badge>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-[var(--text-secondary)]">Confidence</span>
                <span className="text-sm font-bold">{agent.conf}%</span>
              </div>
              <div className="text-sm text-[#cbd5e1]">
                <span className="text-xs text-[var(--text-secondary)] block mb-1">Reasoning:</span>
                "{agent.reason}"
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
