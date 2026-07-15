import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList,
  LineChart, Line, AreaChart, Area, Cell, Legend
} from 'recharts';
import { Beaker, Target, BarChart2, ShieldAlert, Cpu } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

const ResearchLab = () => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/research/report`);
        setReport(response.data);
      } catch (error) {
        console.error("Failed to fetch research report", error);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, []);

  if (loading) return <div className="p-8 text-slate-300 flex items-center justify-center h-full">Compiling Diagnostic Report...</div>;
  if (!report || report.error) return <div className="p-8 text-slate-300">No Diagnostic Report Available. Run the diagnostic generator script.</div>;

  const {
    label_distribution,
    threshold_analysis,
    confusion_matrix,
    sector_analysis,
    regime_analysis,
    calibration_quality,
    feature_diagnostics,
    error_analysis,
    improvement_recommendations
  } = report;

  // Format Threshold Data
  const thresholdData = threshold_analysis.thresholds.map(t => ({
    threshold: t.threshold,
    winRate: t.win_rate * 100,
    expectedTrades: t.expected_trades
  }));

  // Format Sector Data
  const sectorData = sector_analysis.all_sectors.slice(0, 15).map(s => ({
    name: s.sector.substring(0, 10),
    winRate: s.win_rate * 100,
    signals: s.signals_generated
  }));

  // Format Regime Data
  const regimeData = regime_analysis.map(r => ({
    name: r.regime,
    winRate: r.win_rate * 100,
    signals: r.signals_generated
  }));

  // Format Feature Data
  const featureData = feature_diagnostics.slice(0, 10).map(f => ({
    name: f.feature,
    gain: f.information_gain,
    stability: f.stability
  }));

  // Format Calibration Data
  const calibrationData = calibration_quality.buckets.map(b => ({
    bucket: b.bucket,
    actualRate: b.actual_win_rate * 100,
    samples: b.samples
  }));

  return (
    <div className="p-8 space-y-8 animate-fade-in text-slate-100 overflow-y-auto h-full pb-20">
      
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-500 flex items-center gap-3">
            <Beaker className="text-indigo-400" />
            Model Diagnostics & Research Lab
          </h1>
          <p className="text-slate-400 mt-2 text-sm">
            Quantitative analysis of Production Model ({report.model_version}) on Out-Of-Time Test Set ({report.test_samples} samples)
          </p>
        </div>
      </div>

      {/* Warnings & Recommendations */}
      {improvement_recommendations && improvement_recommendations.length > 0 && (
        <div className="bg-amber-950/30 border border-amber-500/30 rounded-xl p-6">
          <h3 className="text-amber-400 font-semibold mb-4 flex items-center gap-2">
            <ShieldAlert size={18} />
            Diagnostic Alerts & Recommendations
          </h3>
          <ul className="list-disc list-inside space-y-2 text-sm text-slate-300">
            {improvement_recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Top Level KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard title="Test Samples" value={report.test_samples} />
        <MetricCard title="Label Balance (BUY%)" value={`${label_distribution.buy_percentage}%`} />
        <MetricCard title="Optimal Threshold" value={`${threshold_analysis.recommendation.optimal_threshold}%`} />
        <MetricCard title="Best Sector" value={sector_analysis.best_sector?.sector || "N/A"} />
        <MetricCard title="Worst Sector" value={sector_analysis.worst_sector?.sector || "N/A"} />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Threshold Analysis */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <h2 className="text-xl font-bold mb-6 text-slate-200">Threshold Optimization (Win Rate vs Trades)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={thresholdData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="threshold" stroke="#64748b" label={{ value: 'Probability Threshold (%)', position: 'insideBottomRight', offset: -10 }}/>
                <YAxis yAxisId="left" stroke="#8b5cf6" label={{ value: 'Win Rate (%)', angle: -90, position: 'insideLeft' }}/>
                <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" label={{ value: 'Expected Trades', angle: 90, position: 'insideRight' }}/>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="winRate" stroke="#8b5cf6" strokeWidth={3} name="Win Rate %" />
                <Line yAxisId="right" type="monotone" dataKey="expectedTrades" stroke="#3b82f6" strokeWidth={2} name="Total Trades" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Performance */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <h2 className="text-xl font-bold mb-6 text-slate-200">Sector Accuracy Profile</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sectorData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" />
                <YAxis dataKey="name" type="category" stroke="#64748b" width={80} tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} cursor={{fill: '#1e293b'}} />
                <Bar dataKey="winRate" name="Win Rate %" radius={[0, 4, 4, 0]}>
                  {
                    sectorData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.winRate > 50 ? '#10b981' : '#ef4444'} />
                    ))
                  }
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Feature Diagnostics */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <h2 className="text-xl font-bold mb-6 text-slate-200">Top 10 Feature Ranking (Information Gain)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 10, angle: -45, textAnchor: 'end' }} height={60} />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} cursor={{fill: '#1e293b'}} />
                <Bar dataKey="gain" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Info Gain" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Calibration & Regime */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl grid grid-cols-2 gap-4">
            <div>
              <h2 className="text-sm font-bold mb-4 text-slate-200">Market Regime Accuracy</h2>
              <div className="h-60">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={regimeData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} cursor={{fill: '#1e293b'}} />
                    <Bar dataKey="winRate" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Win Rate %" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div>
              <h2 className="text-sm font-bold mb-4 text-slate-200">Calibration Profile</h2>
              <div className="h-60">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={calibrationData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="bucket" stroke="#64748b" tick={{ fontSize: 10, angle: -45, textAnchor: 'end' }} height={50} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                    <Line type="monotone" dataKey="actualRate" stroke="#10b981" strokeWidth={3} name="Actual Win Rate %" dot={{r: 4}} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
        </div>

      </div>
      
      {/* Error Clustering Table (False Positives) */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl overflow-x-auto">
          <h2 className="text-xl font-bold mb-6 text-slate-200">Top False Positives (Missed Signals)</h2>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400 text-sm">
                <th className="pb-3 px-4 font-medium">Symbol</th>
                <th className="pb-3 px-4 font-medium">Date</th>
                <th className="pb-3 px-4 font-medium">Predicted Prob</th>
                <th className="pb-3 px-4 font-medium">Actual Outcome</th>
              </tr>
            </thead>
            <tbody>
              {error_analysis.false_positives.slice(0, 10).map((fp, i) => (
                <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/50 transition-colors">
                  <td className="py-3 px-4 font-mono text-slate-300">{fp.symbol}</td>
                  <td className="py-3 px-4 text-slate-400">{fp.date}</td>
                  <td className="py-3 px-4 text-amber-400 font-semibold">{fp.predicted_prob.toFixed(1)}%</td>
                  <td className="py-3 px-4 text-red-400">Failed Breakout</td>
                </tr>
              ))}
            </tbody>
          </table>
      </div>

    </div>
  );
};

const MetricCard = ({ title, value }) => (
  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl relative overflow-hidden group">
    <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
    <div className="text-slate-400 text-xs font-medium mb-1 uppercase tracking-wider">{title}</div>
    <div className="text-2xl font-bold text-slate-100 tracking-tight">{value}</div>
  </div>
);

export default ResearchLab;
