import React, { useEffect, useState } from 'react';
import MetricCard from '../components/ui/MetricCard';
import { Microscope, Activity, TrendingUp, AlertTriangle, PlayCircle } from 'lucide-react';
import api from '../services/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function AlphaIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('/api/alpha/');
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading || !data) return <div className="p-8">Loading Alpha Registry...</div>;

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
            <Microscope className="text-[var(--accent-primary)]" />
            Alpha Research Platform
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">Quantitative factor evaluation and predictive power (IC)</p>
        </div>
        <button className="btn btn-primary flex items-center gap-2">
          <PlayCircle size={16} /> Evaluate IC
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Total Factors" value={data.total_factors} icon={<Activity size={18} />} trend="up" />
        <MetricCard title="Production" value={data.production_count} icon={<TrendingUp size={18} color="var(--signal-up)" />} subtitle="Passed IC > 0.02" />
        <MetricCard title="Experimental" value={data.experimental_count} icon={<Microscope size={18} color="var(--signal-neutral)" />} subtitle="Testing phase" />
        <MetricCard title="Avg IC Quality" value={`${data.quality_score}%`} icon={<AlertTriangle size={18} color="var(--accent-primary)" />} subtitle="Stability Check" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        <div className="glass-panel p-5">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4">Top Predictive Factors (Information Coefficient)</h3>
          <div className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.top_predictive} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                <XAxis type="number" stroke="rgba(255,255,255,0.5)" />
                <YAxis dataKey="name" type="category" stroke="rgba(255,255,255,0.8)" width={120} tick={{fontSize: 12}} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--glass-border)' }} />
                <Bar dataKey="ic" fill="var(--accent-primary)" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-5 flex flex-col gap-4">
          <div>
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">Alpha Decay Alerts</h3>
            <div className="space-y-2">
              {data.decay_alerts.map((alert, i) => (
                <div key={i} className="flex justify-between items-center p-3 rounded bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.3)]">
                  <span className="font-mono text-sm text-[var(--signal-down)]">{alert.name}</span>
                  <span className="text-xs text-[var(--text-secondary)]">Drop: {alert.degradation} ({alert.recommendation})</span>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">Regime Performance</h3>
            <div className="space-y-2">
              {data.regime_highlights.map((reg, i) => (
                <div key={i} className="flex justify-between items-center p-3 rounded bg-[rgba(255,255,255,0.02)] border border-[var(--glass-border)]">
                  <span className="font-mono text-sm text-[var(--text-primary)]">{reg.regime} Market</span>
                  <span className="text-xs text-[var(--accent-primary)]">Best: {reg.top_factor} (IC: {reg.ic})</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
