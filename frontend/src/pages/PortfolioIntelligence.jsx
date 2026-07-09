import React, { useState } from 'react';
import MetricCard from '../components/ui/MetricCard';
import Badge from '../components/ui/Badge';
import { Briefcase, TrendingUp, ShieldAlert, Activity, CheckCircle2, ChevronRight, PieChart } from 'lucide-react';

export default function PortfolioIntelligence() {
  const [selectedStock, setSelectedStock] = useState(null);

  const portfolioMetrics = [
    { title: "Portfolio Score", value: "92", icon: <Activity size={18} />, trend: "up", subtitle: "Top 10%" },
    { title: "Diversification", value: "Excellent", icon: <PieChart size={18} /> },
    { title: "Market Exposure", value: "Moderate", icon: <TrendingUp size={18} /> },
    { title: "Cash Available", value: "₹1,24,000", icon: <Briefcase size={18} /> },
    { title: "Expected Return (Weekly)", value: "₹8,420", icon: <TrendingUp size={18} />, trend: "up", subtitle: "9.4%" },
    { title: "Expected Drawdown", value: "2.8%", icon: <ShieldAlert size={18} />, trend: "down", subtitle: "Low Risk" },
  ];

  const holdings = [
    { ticker: 'BEL.NS', current: '0%', target: '3.4%', confidence: '92%', fit: '96%', expected: '9.4%', risk: 'Low', kelly: '3.4%', corr: '0.12', sector: 'Defense' },
    { ticker: 'TCS.NS', current: '12%', target: '10%', confidence: '85%', fit: '90%', expected: '4.2%', risk: 'Low', kelly: '2.1%', corr: '0.45', sector: 'IT' },
    { ticker: 'HDFCBANK.NS', current: '18%', target: '6%', confidence: '60%', fit: '40%', expected: '1.2%', risk: 'Medium', kelly: '0%', corr: '0.85', sector: 'Bank' },
  ];

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full relative">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1">Portfolio Intelligence</h1>
          <p className="text-[var(--text-secondary)] text-sm">AI-driven analysis of your portfolio fit and correlation</p>
        </div>
        <Badge variant="primary">Kelly Utilization: 43%</Badge>
      </div>

      {/* Top Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {portfolioMetrics.map((m, i) => (
          <MetricCard key={i} {...m} />
        ))}
      </div>

      <div className="flex gap-6 flex-1 overflow-hidden">
        {/* Main Table */}
        <div className="glass-panel flex-1 flex flex-col overflow-hidden">
          <div className="p-4 border-b border-[var(--glass-border)] bg-[rgba(0,0,0,0.1)]">
            <h3 className="font-semibold text-[var(--text-primary)]">Recommended Portfolio Adjustments</h3>
          </div>
          <div className="overflow-auto flex-1">
            <table className="w-full text-sm text-left">
              <thead className="text-[var(--text-secondary)] bg-[var(--bg-surface-elevated)] sticky top-0 z-10">
                <tr>
                  <th className="px-4 py-3 font-medium">Ticker</th>
                  <th className="px-4 py-3 font-medium">Current</th>
                  <th className="px-4 py-3 font-medium">Target</th>
                  <th className="px-4 py-3 font-medium">Confidence</th>
                  <th className="px-4 py-3 font-medium">Fit</th>
                  <th className="px-4 py-3 font-medium">Risk</th>
                  <th className="px-4 py-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--glass-border)]">
                {holdings.map((h) => (
                  <tr 
                    key={h.ticker} 
                    onClick={() => setSelectedStock(h)}
                    className={`cursor-pointer transition-colors ${selectedStock?.ticker === h.ticker ? 'bg-[var(--glass-highlight)]' : 'hover:bg-[rgba(255,255,255,0.02)]'}`}
                  >
                    <td className="px-4 py-3 font-medium">{h.ticker.replace('.NS', '')}</td>
                    <td className="px-4 py-3">{h.current}</td>
                    <td className="px-4 py-3 text-[var(--text-primary)] font-medium">{h.target}</td>
                    <td className="px-4 py-3 text-[var(--signal-up)]">{h.confidence}</td>
                    <td className="px-4 py-3">{h.fit}</td>
                    <td className="px-4 py-3"><Badge variant={h.risk === 'Low' ? 'success' : 'warning'}>{h.risk}</Badge></td>
                    <td className="px-4 py-3">
                      <button className="text-[var(--accent-primary)] hover:text-[var(--accent-hover)] transition-colors">
                        Details <ChevronRight size={14} className="inline" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Drawer (Simulated inline for layout) */}
        {selectedStock && (
          <div className="glass-panel w-80 flex flex-col overflow-hidden animate-fade-in border-l-[3px] border-l-[var(--accent-primary)]">
            <div className="p-5 border-b border-[var(--glass-border)] flex justify-between items-center bg-[rgba(0,0,0,0.1)]">
              <div>
                <h2 className="text-xl font-bold">{selectedStock.ticker.replace('.NS', '')}</h2>
                <div className="text-[var(--text-secondary)] text-sm">{selectedStock.sector}</div>
              </div>
              <Badge variant="success">BUY</Badge>
            </div>
            
            <div className="p-5 flex-1 overflow-y-auto flex flex-col gap-5">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-[var(--text-secondary)] text-xs mb-1">Portfolio Fit</div>
                  <div className="text-lg font-bold text-[var(--signal-up)]">{selectedStock.fit}</div>
                </div>
                <div>
                  <div className="text-[var(--text-secondary)] text-xs mb-1">Kelly Allocation</div>
                  <div className="text-lg font-bold">{selectedStock.kelly}</div>
                </div>
                <div>
                  <div className="text-[var(--text-secondary)] text-xs mb-1">Breakout Score</div>
                  <div className="text-lg font-bold">94</div>
                </div>
                <div>
                  <div className="text-[var(--text-secondary)] text-xs mb-1">Correlation</div>
                  <div className="text-lg font-bold">{selectedStock.corr}</div>
                </div>
              </div>
              
              <div className="mt-2">
                <h4 className="text-sm font-semibold mb-3 border-b border-[var(--glass-border)] pb-2">AI Reasoning</h4>
                <ul className="text-sm space-y-2 text-[var(--text-secondary)]">
                  <li className="flex gap-2 items-start"><CheckCircle2 size={16} className="text-[var(--signal-up)] shrink-0 mt-0.5" /> <span>Strong Breakout momentum detected</span></li>
                  <li className="flex gap-2 items-start"><CheckCircle2 size={16} className="text-[var(--signal-up)] shrink-0 mt-0.5" /> <span>Low correlation (0.12) to existing holdings</span></li>
                  <li className="flex gap-2 items-start"><CheckCircle2 size={16} className="text-[var(--signal-up)] shrink-0 mt-0.5" /> <span>Favorable sector rotation into Defense</span></li>
                </ul>
              </div>
              
              <button className="btn btn-primary w-full mt-auto">Execute Allocation</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
