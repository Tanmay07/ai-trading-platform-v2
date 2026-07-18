import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit, Activity, ShieldAlert, Zap, BookOpen, AlertTriangle, CheckCircle, Flame } from 'lucide-react';

export default function AdaptiveIntelligence() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchHealth = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('http://localhost:8000/adaptive/health');
            if (!res.ok) throw new Error("Failed to fetch adaptive intelligence data");
            const result = await res.json();
            setData(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHealth();
    }, []);

    const getHealthColor = (score) => {
        if (score >= 80) return 'text-emerald-400';
        if (score >= 50) return 'text-yellow-400';
        return 'text-red-400';
    };

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-gray-100 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                
                {/* Header */}
                <div className="flex justify-between items-end border-b border-gray-700 pb-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                            <BrainCircuit className="text-pink-500" size={36} /> Adaptive Intelligence
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg">Continuous Learning & AI-CIO Orchestration (Phase F5)</p>
                    </div>
                    <button 
                        onClick={fetchHealth}
                        disabled={loading}
                        className="bg-pink-600 hover:bg-pink-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-pink-900/50 transition-all flex items-center gap-2"
                    >
                        {loading ? <Activity className="animate-spin" size={18} /> : <Zap size={18} />}
                        {loading ? 'Analyzing...' : 'Run Diagnostics'}
                    </button>
                </div>

                {error && (
                    <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg flex items-center gap-3">
                        <AlertTriangle /> {error}
                    </div>
                )}

                {data && (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        {/* Top Line Health */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium flex items-center gap-2"><Activity size={16}/> Overall AI Health</p>
                                <p className={`text-5xl font-black mt-2 ${getHealthColor(data.health_score)}`}>
                                    {data.health_score}/100
                                </p>
                                <p className="text-xs text-gray-500 mt-1">Based on Phase F4 feedback repository</p>
                            </div>
                            
                            <div className="md:col-span-2 bg-gradient-to-r from-gray-800 to-indigo-900/30 p-6 rounded-xl border border-indigo-900/50 shadow-md flex flex-col justify-center">
                                <h3 className="text-sm font-bold text-indigo-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                                    <BookOpen size={16}/> AI-CIO Executive Briefing
                                </h3>
                                <p className="text-gray-200 leading-relaxed">
                                    {data.ai_cio_briefing}
                                </p>
                            </div>
                        </div>

                        {/* Diagnostics & Drift Grid */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            
                            {/* Performance Attribution */}
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md overflow-hidden">
                                <div className="p-4 border-b border-gray-700 bg-gray-900/50 flex justify-between items-center">
                                    <h2 className="text-lg font-bold text-white flex items-center gap-2"><Flame size={18}/> Subsystem Attribution</h2>
                                </div>
                                <div className="p-6">
                                    {data.performance.status === "NO_DATA" ? (
                                        <div className="text-gray-500 text-center py-8">No feedback data available. Run Paper Trading first.</div>
                                    ) : (
                                        <div className="space-y-6">
                                            <div>
                                                <div className="flex justify-between text-sm mb-1">
                                                    <span className="font-bold text-gray-300">Prediction Layer</span>
                                                    <span className={data.performance.subsystem_attribution.prediction >= 0 ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold'}>
                                                        {data.performance.subsystem_attribution.prediction >= 0 ? '+' : ''}{data.performance.subsystem_attribution.prediction} Value Add
                                                    </span>
                                                </div>
                                                <div className="w-full bg-gray-900 rounded-full h-2">
                                                    <div className={`h-2 rounded-full ${data.performance.subsystem_attribution.prediction >= 0 ? 'bg-emerald-500' : 'bg-red-500'}`} style={{ width: '100%' }}></div>
                                                </div>
                                            </div>
                                            <div>
                                                <div className="flex justify-between text-sm mb-1">
                                                    <span className="font-bold text-gray-300">Portfolio Engine</span>
                                                    <span className={data.performance.subsystem_attribution.portfolio >= 0 ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold'}>
                                                        {data.performance.subsystem_attribution.portfolio >= 0 ? '+' : ''}{data.performance.subsystem_attribution.portfolio} Value Add
                                                    </span>
                                                </div>
                                                <div className="w-full bg-gray-900 rounded-full h-2">
                                                    <div className={`h-2 rounded-full ${data.performance.subsystem_attribution.portfolio >= 0 ? 'bg-emerald-500' : 'bg-red-500'}`} style={{ width: '100%' }}></div>
                                                </div>
                                            </div>
                                            <div>
                                                <div className="flex justify-between text-sm mb-1">
                                                    <span className="font-bold text-gray-300">Execution Planning</span>
                                                    <span className={data.performance.subsystem_attribution.execution >= 0 ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold'}>
                                                        {data.performance.subsystem_attribution.execution >= 0 ? '+' : ''}{data.performance.subsystem_attribution.execution} Value Add
                                                    </span>
                                                </div>
                                                <div className="w-full bg-gray-900 rounded-full h-2">
                                                    <div className={`h-2 rounded-full ${data.performance.subsystem_attribution.execution >= 0 ? 'bg-emerald-500' : 'bg-red-500'}`} style={{ width: '100%' }}></div>
                                                </div>
                                            </div>
                                            
                                            <div className="pt-4 border-t border-gray-700 flex justify-between items-center text-sm">
                                                <span className="text-gray-400">Total Analyzed</span>
                                                <span className="font-bold text-white">{data.performance.total_trades_analyzed} Trades</span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Recommendations Queue */}
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md overflow-hidden">
                                <div className="p-4 border-b border-gray-700 bg-gray-900/50 flex justify-between items-center">
                                    <h2 className="text-lg font-bold text-white flex items-center gap-2"><ShieldAlert size={18}/> Recommendations</h2>
                                </div>
                                <div className="p-4 space-y-4">
                                    {data.recommendations.length === 0 && (
                                        <div className="text-gray-500 text-center py-8">No recommendations generated.</div>
                                    )}
                                    {data.recommendations.map((rec, idx) => (
                                        <div key={idx} className={`p-4 rounded-lg border ${rec.priority === 'HIGH' ? 'bg-red-900/20 border-red-900/50' : rec.priority === 'MEDIUM' ? 'bg-yellow-900/20 border-yellow-900/50' : 'bg-emerald-900/20 border-emerald-900/50'}`}>
                                            <div className="flex justify-between items-start mb-2">
                                                <span className={`text-xs font-bold px-2 py-0.5 rounded uppercase tracking-wider ${rec.priority === 'HIGH' ? 'bg-red-500/20 text-red-400' : rec.priority === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                                                    {rec.priority} Priority
                                                </span>
                                                <span className="text-xs text-gray-500 font-mono">{rec.owner}</span>
                                            </div>
                                            <h3 className="font-bold text-white text-lg mb-1">{rec.recommendation}</h3>
                                            <p className="text-sm text-gray-400 mb-2">{rec.evidence}</p>
                                            <div className="text-xs text-indigo-300 bg-indigo-900/30 inline-block px-2 py-1 rounded">
                                                Impact: {rec.expected_impact}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
