import React from 'react';
import MetricCard from '../components/ui/MetricCard';
import Badge from '../components/ui/Badge';
import { Activity, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';

export default function MarketIntelligence() {
  const topMetrics = [
    { title: "Market Score", value: "89", icon: <Activity size={18} />, trend: "up", subtitle: "Bull Market" },
    { title: "Market Breadth", value: "82", icon: <TrendingUp size={18} />, trend: "up", subtitle: "Strong" },
    { title: "India VIX", value: "14.2", icon: <TrendingDown size={18} />, trend: "down", subtitle: "-2.1%" },
    { title: "Global Sentiment", value: "Positive", icon: <Activity size={18} />, subtitle: "NASDAQ +1.2%" },
  ];

  const sectors = [
    { name: "Defense", strength: 95 },
    { name: "IT", strength: 82 },
    { name: "Bank", strength: 75 },
    { name: "Auto", strength: 68 },
    { name: "Metal", strength: 55 },
    { name: "Pharma", strength: 40 },
  ];

  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1">Market Intelligence</h1>
          <p className="text-[var(--text-secondary)] text-sm">Real-time regime detection and sector rotation</p>
        </div>
        <Badge variant="success">Risk Level: Moderate</Badge>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {topMetrics.map((m, i) => (
          <MetricCard key={i} {...m} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sector Rotation Heatmap */}
        <div className="glass-panel p-5 col-span-1 lg:col-span-2 flex flex-col">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4">Sector Rotation</h3>
          <div className="flex-1 flex flex-col justify-center gap-4">
            {sectors.map(s => (
              <div key={s.name} className="flex items-center gap-4">
                <span className="w-20 text-sm font-medium text-[var(--text-secondary)]">{s.name}</span>
                <div className="flex-1 h-6 bg-[rgba(255,255,255,0.05)] rounded overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-[var(--accent-primary)] to-[var(--signal-up)] transition-all duration-1000" 
                    style={{ width: `${s.strength}%` }}
                  ></div>
                </div>
                <span className="w-10 text-right text-sm font-bold">{s.strength}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Global Widgets */}
        <div className="flex flex-col gap-4">
          <div className="glass-panel p-4">
            <h4 className="text-sm font-semibold mb-3 border-b border-[var(--glass-border)] pb-2">Institutional Flows</h4>
            <div className="flex justify-between mb-2">
              <span className="text-[var(--text-secondary)] text-sm">FII</span>
              <span className="text-[var(--signal-up)] font-bold">+ ₹1,240 Cr</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--text-secondary)] text-sm">DII</span>
              <span className="text-[var(--signal-down)] font-bold">- ₹320 Cr</span>
            </div>
          </div>
          
          <div className="glass-panel p-4">
            <h4 className="text-sm font-semibold mb-3 border-b border-[var(--glass-border)] pb-2">Global Markets</h4>
            <div className="flex justify-between mb-2">
              <span className="text-[var(--text-secondary)] text-sm">Gift Nifty</span>
              <span className="text-[var(--signal-up)] font-bold">22,450 (+0.4%)</span>
            </div>
            <div className="flex justify-between mb-2">
              <span className="text-[var(--text-secondary)] text-sm">USDINR</span>
              <span className="text-[var(--text-primary)] font-bold">83.45</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--text-secondary)] text-sm">Crude Oil</span>
              <span className="text-[var(--signal-down)] font-bold">$78.20</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
