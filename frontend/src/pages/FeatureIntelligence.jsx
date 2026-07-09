import React, { useEffect, useState } from 'react';
import MetricCard from '../components/ui/MetricCard';
import { Database, Activity, CheckCircle, Clock, Layers, PlayCircle } from 'lucide-react';
import api from '../services/api';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

export default function FeatureIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('/api/features/');
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading || !data) return <div className="p-8">Loading Feature Platform...</div>;

  const COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b'];

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
            <Database className="text-[var(--accent-primary)]" />
            Institutional Alpha Library
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">Feature engineering pipeline & quality monitoring</p>
        </div>
        <button className="btn btn-primary flex items-center gap-2">
          <PlayCircle size={16} /> Run Pipeline
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Total Features" value={data.total_features} icon={<Layers size={18} />} trend="up" />
        <MetricCard title="Latest Version" value={data.latest_version} icon={<Clock size={18} />} subtitle={data.last_updated} />
        <MetricCard title="Quality Score" value={`${data.quality_score}%`} icon={<CheckCircle size={18} color="var(--signal-up)" />} subtitle="Valid Rows" />
        <MetricCard title="Dependencies" value="Resolved" icon={<Activity size={18} />} subtitle="DAG Engine" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        <div className="glass-panel p-5">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4">Feature Distribution</h3>
          <div className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.categories} dataKey="count" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5}>
                  {data.categories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--glass-border)' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-5">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4">Core Drivers</h3>
          <div className="space-y-3">
            {data.top_features.map((feat, i) => (
              <div key={i} className="flex justify-between items-center p-3 rounded bg-[rgba(255,255,255,0.02)] border border-[var(--glass-border)]">
                <span className="font-mono text-sm text-[var(--text-primary)]">{feat}</span>
                <span className="text-xs text-[var(--text-secondary)]">v1.0</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
