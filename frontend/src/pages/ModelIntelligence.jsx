import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { Activity, Beaker, Cpu, Settings, Target } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

const ModelIntelligence = () => {
  const [modelData, setModelData] = useState(null);
  const [trainingData, setTrainingData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [modelRes, bestTrainRes, allTrainRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/model/current`).catch(() => ({ data: null })),
          axios.get(`${API_BASE_URL}/training/best`).catch(() => ({ data: null })),
          axios.get(`${API_BASE_URL}/training/experiments`).catch(() => ({ data: [] }))
        ]);
        
        setModelData(modelRes.data);
        setTrainingData({
            best: bestTrainRes.data,
            all: allTrainRes.data
        });
      } catch (error) {
        console.error("Failed to fetch intelligence data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleRetrain = async () => {
      alert("Initiating Institutional Training Cycle in the background...");
      await axios.post(`${API_BASE_URL}/training/retrain`);
  };

  if (loading) return <div className="p-8 text-slate-300">Loading AI Model Metrics...</div>;

  return (
    <div className="p-8 space-y-8 animate-fade-in text-slate-100 overflow-y-auto h-full pb-20">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
            Model Intelligence & Institutional Training
          </h1>
          <p className="text-slate-400 mt-2 text-sm">
            Production Engine Status & Experiment Tracking
          </p>
        </div>
        <div className="flex items-center gap-4">
            <button onClick={handleRetrain} className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-lg shadow-indigo-500/20">
                Run Randomized Search
            </button>
            <div className="bg-emerald-900/40 border border-emerald-500/30 text-emerald-400 px-4 py-2 rounded-lg text-sm font-semibold flex items-center shadow-[0_0_15px_rgba(16,185,129,0.1)]">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
            Active Model Engine
            </div>
        </div>
      </div>

      {trainingData && trainingData.best && Object.keys(trainingData.best).length > 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-8">
             <div className="flex items-center gap-3 mb-6">
                 <Activity className="text-indigo-400" />
                 <h2 className="text-xl font-bold text-slate-200">Institutional Training Framework</h2>
             </div>
             
             <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
                <MetricCard title="Experiments" value={trainingData.all.length} />
                <MetricCard title="Best Win Rate" value={`${(trainingData.best.test_metrics?.win_rate * 100 || 0).toFixed(1)}%`} />
                <MetricCard title="Best Profit Factor" value={trainingData.best.test_metrics?.profit_factor || "N/A"} />
                <MetricCard title="Calibration" value={trainingData.best.calibration_method || "N/A"} />
                <MetricCard title="Opt Threshold" value={`${trainingData.best.optimal_threshold}%`} />
                <MetricCard title="Search Time" value={`${trainingData.best.training_time_seconds}s`} />
             </div>

             <div className="bg-slate-800/50 rounded-lg p-4 mb-6 text-sm flex flex-col md:flex-row gap-8">
                 <div>
                     <span className="text-slate-400 block mb-1">Validation Strategy</span>
                     <span className="text-emerald-400 font-mono">{trainingData.best.validation_strategy}</span>
                 </div>
                 <div>
                     <span className="text-slate-400 block mb-1">Training Method</span>
                     <span className="text-emerald-400 font-mono">RandomizedSearchCV (25 iter)</span>
                 </div>
                 <div>
                     <span className="text-slate-400 block mb-1">Model Architecture</span>
                     <span className="text-emerald-400 font-mono">{trainingData.best.model_version}</span>
                 </div>
             </div>

             <h3 className="text-lg font-semibold text-slate-300 mb-4">Best Hyperparameters</h3>
             <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                 {Object.entries(trainingData.best.hyperparameters || {}).map(([key, val]) => (
                     <div key={key} className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                         <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">{key.replace('_', ' ')}</div>
                         <div className="text-sm text-slate-200 font-mono">{String(val)}</div>
                     </div>
                 ))}
             </div>
          </div>
      )}

      {modelData && modelData.metadata && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl"></div>
            <h2 className="text-xl font-bold mb-6 text-slate-200">Global Feature Impact (SHAP)</h2>
            <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                <BarChart layout="vertical" data={modelData.metadata.shap_summary.slice(0, 10).map(item => ({name: item.feature, impact: parseFloat(item.mean_abs_shap.toFixed(4))}))} margin={{ top: 10, right: 30, left: 40, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis type="number" stroke="#64748b" />
                    <YAxis dataKey="name" type="category" stroke="#64748b" width={120} tick={{ fontSize: 12 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} itemStyle={{ color: '#60a5fa' }} />
                    <Bar dataKey="impact" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
                </ResponsiveContainer>
            </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl"></div>
            <h2 className="text-xl font-bold mb-6 text-slate-200">Production Model Performance</h2>
            <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={[
                    { metric: 'ROC-AUC', value: modelData.metadata.metrics.ml.roc_auc, fullMark: 1.0 },
                    { metric: 'Precision', value: modelData.metadata.metrics.ml.precision, fullMark: 1.0 },
                    { metric: 'Win Rate', value: modelData.metadata.metrics.trading.win_rate, fullMark: 1.0 },
                    { metric: 'Target Hit', value: modelData.metadata.metrics.trading.target_hit_rate, fullMark: 1.0 },
                    { metric: 'PR-AUC', value: modelData.metadata.metrics.ml.pr_auc, fullMark: 1.0 }
                ]}>
                    <PolarGrid stroke="#1e293b" />
                    <PolarAngleAxis dataKey="metric" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 1]} stroke="#334155" />
                    <Radar name="Performance" dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.4} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                </RadarChart>
                </ResponsiveContainer>
            </div>
            </div>
          </div>
      )}
    </div>
  );
};

const MetricCard = ({ title, value }) => (
  <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 relative overflow-hidden group">
    <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
    <div className="text-slate-400 text-xs font-medium mb-1 uppercase tracking-wider">{title}</div>
    <div className="text-xl font-bold text-slate-100 font-mono tracking-tight">{value}</div>
  </div>
);

export default ModelIntelligence;
