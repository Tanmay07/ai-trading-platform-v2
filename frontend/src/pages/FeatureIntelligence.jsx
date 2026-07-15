import React, { useState, useEffect } from 'react';
import axios from 'axios';

const FeatureIntelligence = () => {
    const [status, setStatus] = useState(null);
    const [quality, setQuality] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [generating, setGenerating] = useState(false);

    const API_BASE = 'http://localhost:8000/api/features';

    const fetchData = async () => {
        try {
            setLoading(true);
            const statusRes = await axios.get(`${API_BASE}/status`);
            const qualityRes = await axios.get(`${API_BASE}/quality`);
            
            setStatus(statusRes.data);
            setQuality(qualityRes.data);
            setError(null);
        } catch (err) {
            console.error("Error fetching feature intelligence", err);
            setError("Failed to load feature metrics. Ensure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // refresh every 10s
        return () => clearInterval(interval);
    }, []);

    const handleGenerateAll = async () => {
        if (!window.confirm("Are you sure you want to trigger a full recalculation? This may take several minutes.")) return;
        
        try {
            setGenerating(true);
            await axios.post(`${API_BASE}/recalculate`);
            alert("Feature recalculation started in the background!");
        } catch (err) {
            console.error(err);
            alert("Failed to start recalculation.");
        } finally {
            setGenerating(false);
        }
    };

    if (loading && !status) return <div className="p-8 text-white">Loading Feature Intelligence...</div>;
    if (error) return <div className="p-8 text-red-500">{error}</div>;

    return (
        <div className="p-8 text-white min-h-screen" style={{ backgroundColor: '#0f172a' }}>
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
                        Feature Intelligence
                    </h1>
                    <p className="text-gray-400 mt-2">Core ML Feature Engineering Platform (Phase E2)</p>
                </div>
                <button 
                    onClick={handleGenerateAll}
                    disabled={generating}
                    className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg shadow-lg transition duration-200 disabled:opacity-50"
                >
                    {generating ? 'Starting...' : 'Recalculate All'}
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
                    <h3 className="text-slate-400 text-sm font-semibold uppercase tracking-wider mb-2">Total Features</h3>
                    <div className="text-4xl font-bold text-white">{status?.total_features || 0}</div>
                    <div className="text-sm text-emerald-400 mt-2">Across 6 categories</div>
                </div>
                
                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
                    <h3 className="text-slate-400 text-sm font-semibold uppercase tracking-wider mb-2">Universe Coverage</h3>
                    <div className="text-4xl font-bold text-white">{status?.coverage_percent}%</div>
                    <div className="text-sm text-slate-400 mt-2">{status?.generated_symbols} / {status?.total_universe} Symbols</div>
                </div>

                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
                    <h3 className="text-slate-400 text-sm font-semibold uppercase tracking-wider mb-2">Quality Score</h3>
                    <div className="text-4xl font-bold text-emerald-400">{quality?.overall_quality_score}/100</div>
                    <div className="text-sm text-slate-400 mt-2">From sample of {quality?.sample_size}</div>
                </div>

                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
                    <h3 className="text-slate-400 text-sm font-semibold uppercase tracking-wider mb-2">Latest Version</h3>
                    <div className="text-4xl font-bold text-indigo-400">{status?.latest_version}</div>
                    <div className="text-sm text-emerald-400 mt-2">Active in Store</div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
                    <h2 className="text-xl font-bold text-white mb-4">Feature Categories</h2>
                    <ul className="space-y-4">
                        <li className="flex justify-between items-center pb-2 border-b border-slate-700">
                            <span className="text-slate-300">📈 Trend Features (EMA, SMA, Slopes)</span>
                            <span className="bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs font-semibold">Active</span>
                        </li>
                        <li className="flex justify-between items-center pb-2 border-b border-slate-700">
                            <span className="text-slate-300">⚡ Momentum Features (RSI, MACD)</span>
                            <span className="bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs font-semibold">Active</span>
                        </li>
                        <li className="flex justify-between items-center pb-2 border-b border-slate-700">
                            <span className="text-slate-300">📊 Volume Features (OBV, VWAP)</span>
                            <span className="bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs font-semibold">Active</span>
                        </li>
                        <li className="flex justify-between items-center pb-2 border-b border-slate-700">
                            <span className="text-slate-300">📉 Volatility Features (ATR, BBands)</span>
                            <span className="bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs font-semibold">Active</span>
                        </li>
                        <li className="flex justify-between items-center pb-2 border-b border-slate-700">
                            <span className="text-slate-300">🚀 Breakout Features (NR7, Distances)</span>
                            <span className="bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs font-semibold">Active</span>
                        </li>
                        <li className="flex justify-between items-center pb-2">
                            <span className="text-slate-300">💧 Liquidity Features (Avg Val, Score)</span>
                            <span className="bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs font-semibold">Active</span>
                        </li>
                    </ul>
                </div>

                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl">
                    <h2 className="text-xl font-bold text-white mb-4">Pipeline Status</h2>
                    <div className="space-y-6">
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-slate-400">Data Extraction</span>
                                <span className="text-emerald-400">100%</span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-2">
                                <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '100%' }}></div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-slate-400">Vectorized Transformation</span>
                                <span className="text-indigo-400">{status?.coverage_percent}%</span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-2">
                                <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${status?.coverage_percent}%` }}></div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-slate-400">Quality Validation</span>
                                <span className="text-indigo-400">{status?.coverage_percent}%</span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-2">
                                <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${status?.coverage_percent}%` }}></div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-slate-400">Dataset Labeling (Reg/Class/Binary)</span>
                                <span className="text-slate-500">Pending Run</span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-2">
                                <div className="bg-slate-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FeatureIntelligence;
