import React, { useEffect, useState } from 'react';
import MetricCard from '../components/ui/MetricCard';
import Badge from '../components/ui/Badge';
import { ShieldCheck, TrendingUp, AlertTriangle, Lock, Activity, ArrowUpCircle, ArrowDownCircle } from 'lucide-react';
import api from '../services/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

export default function TradabilityIntelligence() {
  const [stats, setStats] = useState(null);
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, promosRes] = await Promise.all([
          api.get('/api/tradability/'),
          api.get('/api/tradability/promotions')
        ]);
        setStats(statsRes.data);
        setPromotions(promosRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading || !stats) {
    return <div className="p-8">Loading Tradability Engine...</div>;
  }

  const categoryData = [
    { name: 'Institutional', count: stats.institutional_grade, fill: '#10b981' },
    { name: 'Highly Tradable', count: stats.highly_tradable, fill: '#3b82f6' },
    { name: 'Tradable', count: stats.tradable, fill: '#eab308' },
    { name: 'Monitor', count: stats.monitor, fill: '#f97316' },
    { name: 'Restricted', count: stats.restricted, fill: '#ef4444' },
  ];

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
            <ShieldCheck className="text-[var(--accent-primary)]" />
            Tradability Intelligence
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">Dynamic execution risk & ML training eligibility filtering</p>
        </div>
        <button className="btn btn-primary flex items-center gap-2">
          <Activity size={16} /> Force Recalculate
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Total Universe" value={stats.universe_size} icon={<Activity size={18} />} trend="up" subtitle="Active Symbols" />
        <MetricCard title="Avg Score" value={stats.avg_score} icon={<ShieldCheck size={18} />} subtitle="Out of 100" />
        <MetricCard title="ML Eligible" value={stats.institutional_grade + stats.highly_tradable + stats.tradable} icon={<TrendingUp size={18} />} subtitle="Tradable+" />
        <MetricCard title="Restricted" value={stats.restricted} icon={<Lock size={18} color="var(--signal-down)" />} subtitle="Do Not Trade" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        <div className="glass-panel p-5 flex flex-col">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4">Universe Distribution</h3>
          <div className="flex-1 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="var(--text-secondary)" fontSize={12} />
                <YAxis stroke="var(--text-secondary)" fontSize={12} />
                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--glass-border)' }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-5 flex flex-col">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4">Recent Regime Shifts</h3>
          <div className="space-y-3 overflow-y-auto">
            {promotions.length > 0 ? promotions.map((p, i) => (
              <div key={i} className="flex justify-between items-center p-3 rounded bg-[rgba(255,255,255,0.02)] border border-[var(--glass-border)]">
                <div>
                  <div className="font-bold">{p.symbol}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{p.old} → {p.new}</div>
                </div>
                {p.type === 'PROMOTION' ? <ArrowUpCircle className="text-[var(--signal-up)]" /> : <ArrowDownCircle className="text-[var(--signal-down)]" />}
              </div>
            )) : (
              <div className="text-sm text-[var(--text-secondary)]">No recent shifts logged.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
