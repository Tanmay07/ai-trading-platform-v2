import React, { useEffect, useState } from 'react';
import MetricCard from '../components/ui/MetricCard';
import { Database, ShieldCheck, Activity, Layers, PlayCircle } from 'lucide-react';
import api from '../services/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

export default function DatasetIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('/api/datasets/');
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading || !data) return <div className="p-8">Loading Dataset Platform...</div>;

  const COLORS = ['#10b981', '#34d399', '#6b7280', '#fbbf24', '#ef4444'];

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
            <Database className="text-[var(--accent-primary)]" />
            ML Dataset Engineering
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">Leakage prevention, walk-forward splitting, and dynamic labels</p>
        </div>
        <button className="btn btn-primary flex items-center gap-2">
          <PlayCircle size={16} /> Build Dataset
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Latest Version" value={data.latest_version} icon={<Layers size={18} />} subtitle={data.generated} />
        <MetricCard title="Total Rows" value={`${(data.total_rows / 1000000).toFixed(1)}M`} icon={<Activity size={18} />} subtitle={`${data.features} Alpha Factors`} />
        <MetricCard title="Quality Score" value={`${data.quality_score}%`} icon={<ShieldCheck size={18} color="var(--signal-up)" />} subtitle="Walk-forward Safe" />
        <MetricCard title="Leakage Detections" value={data.leakage} icon={<ShieldCheck size={18} color={data.leakage === 0 ? "var(--signal-up)" : "var(--signal-down)"} />} subtitle="0 Look-ahead bias" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        <div className="glass-panel p-5">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4">Dataset Growth (Rows in Millions)</h3>
          <div className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.growth} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="year" stroke="rgba(255,255,255,0.5)" />
                <YAxis stroke="rgba(255,255,255,0.5)" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--glass-border)' }} />
                <Bar dataKey="rows" fill="var(--accent-primary)" radius={[4, 4, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-5">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4">Multi-Class Label Distribution</h3>
          <div className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.label_distribution} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5}>
                  {data.label_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--glass-border)' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
