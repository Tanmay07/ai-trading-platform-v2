import React, { useEffect, useState } from 'react';
import MetricCard from '../components/ui/MetricCard';
import { Database, Split, Activity, Layers, PlayCircle, BarChart2 } from 'lucide-react';
import api from '../services/api';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

export default function ScenarioIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('/api/scenarios/');
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading || !data) return <div className="p-8">Loading Scenario Generation...</div>;

  const COLORS = ['#10b981', '#fbbf24', '#ef4444', '#3b82f6'];

  return (
    <div className="animate-fade-in flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-1 flex items-center gap-2">
            <Split className="text-[var(--accent-primary)]" />
            Hierarchical Scenario Datasets
          </h1>
          <p className="text-[var(--text-secondary)] text-sm">Specialized datasets for Regimes, Sectors, Volatility, and Events</p>
        </div>
        <button className="btn btn-primary flex items-center gap-2">
          <PlayCircle size={16} /> Generate Scenarios
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Master Dataset" value={data.master_dataset.slice(0, 15)} icon={<Database size={18} />} subtitle="Parent Source" />
        <MetricCard title="Total Scenarios" value={data.total_scenarios} icon={<Layers size={18} />} subtitle="Specialized Partitions" />
        <MetricCard title="Market Coverage" value={`${data.coverage}%`} icon={<Activity size={18} color="var(--signal-up)" />} subtitle="Data accounted for" />
        <MetricCard title="Avg Quality Score" value={`${data.quality_score}%`} icon={<ShieldCheck size={18} color="var(--signal-up)" />} subtitle="Validation Passed" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        
        {/* Regime Pie */}
        <div className="glass-panel p-5 flex flex-col items-center">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4 self-start">Market Regime Distribution</h3>
          <div className="h-[200px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.distributions.regime} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={70} paddingAngle={5}>
                  {data.distributions.regime.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--glass-border)' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Bar */}
        <div className="glass-panel p-5 col-span-2">
          <h3 className="font-semibold text-[var(--text-primary)] mb-4">Top Scenario Volumes</h3>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.top_scenarios} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                <XAxis type="number" stroke="rgba(255,255,255,0.5)" />
                <YAxis dataKey="name" type="category" stroke="rgba(255,255,255,0.8)" width={120} tick={{fontSize: 12}} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--glass-border)' }} />
                <Bar dataKey="rows" fill="var(--accent-primary)" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}

// Ensure you import ShieldCheck in the main file if it fails to compile here.
function ShieldCheck({ size, color }) {
  return <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color || "currentColor"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>;
}
