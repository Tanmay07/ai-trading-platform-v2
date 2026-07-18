import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Layers, Activity, Zap, ShieldCheck, ArrowUpRight, BarChart2 } from 'lucide-react';

export default function StrategyIntelligence() {
    const [strategies, setStrategies] = useState([]);
    const [correlation, setCorrelation] = useState(null);
    const [loading, setLoading] = useState(false);
    const [rebalanceResult, setRebalanceResult] = useState(null);

    const fetchData = async () => {
        try {
            const [regRes, corRes] = await Promise.all([
                fetch('http://localhost:8000/strategies/registry'),
                fetch('http://localhost:8000/strategies/correlation')
            ]);
            setStrategies(await regRes.json());
            setCorrelation(await corRes.json());
        } catch (err) {
            console.error("Failed to fetch strategy data", err);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const triggerRebalance = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/strategies/rebalance', { method: 'POST' });
            const data = await res.json();
            setRebalanceResult(data.allocations);
            fetchData();
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status) => {
        if (status === 'Production') return <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded border border-emerald-500/50 flex items-center gap-1"><ShieldCheck size={12}/> Production</span>;
        if (status === 'Candidate') return <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded border border-purple-500/50 flex items-center gap-1"><ArrowUpRight size={12}/> Candidate</span>;
        return <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded border border-gray-500/50">Experimental</span>;
    };

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-gray-100 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                
                {/* Header */}
                <div className="flex justify-between items-end border-b border-gray-700 pb-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                            <Layers className="text-blue-500" size={36} /> Multi-Strategy Framework
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg">Hierarchical Decision Architecture (Phase G2)</p>
                    </div>
                    <button 
                        onClick={triggerRebalance}
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-blue-900/50 transition-all flex items-center gap-2"
                    >
                        {loading ? <Activity className="animate-spin" size={18} /> : <Zap size={18} />}
                        {loading ? 'Rebalancing...' : 'Rebalance Portfolio'}
                    </button>
                </div>

                {/* Capital Allocation & Matrix */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    
                    {/* Capital Allocation Banner */}
                    <div className="lg:col-span-1 bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2"><BarChart2 size={18}/> Strategy Capital Allocation</h2>
                        {rebalanceResult ? (
                            <div className="space-y-4">
                                {Object.entries(rebalanceResult).sort((a, b) => b[1] - a[1]).map(([strat, alloc]) => (
                                    <div key={strat}>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="font-bold text-gray-300 capitalize">{strat.replace('_', ' ')}</span>
                                            <span className="text-blue-400 font-bold">{alloc.toFixed(1)}%</span>
                                        </div>
                                        <div className="w-full bg-gray-900 rounded-full h-2">
                                            <div className="h-2 rounded-full bg-blue-500" style={{ width: `${alloc}%` }}></div>
                                        </div>
                                    </div>
                                ))}
                                <p className="text-xs text-gray-500 mt-4 text-center">Allocations based on Risk-Adjusted Performance</p>
                            </div>
                        ) : (
                            <div className="text-center text-gray-500 py-8">
                                <p>No active allocation.</p>
                                <button onClick={triggerRebalance} className="mt-2 text-blue-400 text-sm hover:underline">Trigger Rebalance</button>
                            </div>
                        )}
                    </div>

                    {/* Correlation Matrix */}
                    <div className="lg:col-span-2 bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6 overflow-hidden">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2"><Activity size={18}/> Cross-Strategy Correlation</h2>
                        {correlation ? (
                            <div className="overflow-x-auto">
                                <table className="w-full text-center text-xs">
                                    <thead>
                                        <tr>
                                            <th className="p-2 text-gray-500"></th>
                                            {Object.keys(correlation).map(s => <th key={s} className="p-2 text-gray-400 font-bold capitalize">{s.substring(0,4)}</th>)}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {Object.keys(correlation).map(s1 => (
                                            <tr key={s1}>
                                                <td className="p-2 text-gray-400 font-bold text-left capitalize">{s1.replace('_', ' ')}</td>
                                                {Object.keys(correlation[s1]).map(s2 => {
                                                    const val = correlation[s1][s2];
                                                    // Color coding based on correlation value
                                                    let bgColor = 'bg-gray-900';
                                                    if (s1 !== s2) {
                                                        if (val > 0.5) bgColor = 'bg-red-900/50 text-red-300'; // High correlation = bad for div
                                                        else if (val < 0) bgColor = 'bg-emerald-900/50 text-emerald-300'; // Neg correlation = great
                                                        else bgColor = 'bg-yellow-900/30 text-yellow-300'; // Mildly positive
                                                    } else {
                                                        bgColor = 'bg-gray-700 text-gray-500'; // Diagonal
                                                    }
                                                    return (
                                                        <td key={s2} className={`p-2 border border-gray-800 ${bgColor}`}>
                                                            {val.toFixed(2)}
                                                        </td>
                                                    );
                                                })}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div className="text-center text-gray-500 py-8">No correlation data available.</div>
                        )}
                    </div>
                </div>

                {/* Strategy Registry Table */}
                <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md overflow-hidden">
                    <div className="p-4 border-b border-gray-700 bg-gray-900/50">
                        <h2 className="text-lg font-bold text-white flex items-center gap-2"><Layers size={18}/> Strategy Registry</h2>
                    </div>
                    
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-300">
                            <thead className="text-xs text-gray-400 uppercase bg-gray-900/50">
                                <tr>
                                    <th className="px-6 py-3">Strategy Type</th>
                                    <th className="px-6 py-3">Description</th>
                                    <th className="px-6 py-3">Sharpe Ratio</th>
                                    <th className="px-6 py-3">Win Rate</th>
                                    <th className="px-6 py-3">Drawdown</th>
                                    <th className="px-6 py-3">Governance State</th>
                                </tr>
                            </thead>
                            <tbody>
                                {strategies.length === 0 && (
                                    <tr>
                                        <td colSpan="6" className="text-center py-8 text-gray-500">
                                            No strategies registered. Rebalance portfolio to evaluate active plugins.
                                        </td>
                                    </tr>
                                )}
                                {strategies.map((strat, idx) => {
                                    const metrics = strat.latest_metrics;
                                    return (
                                        <motion.tr 
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: idx * 0.1 }}
                                            key={strat.strategy_id} 
                                            className="border-b border-gray-700 hover:bg-gray-700/50 transition-colors"
                                        >
                                            <td className="px-6 py-4 font-bold text-white capitalize">{strat.name}</td>
                                            <td className="px-6 py-4 text-xs text-gray-400 max-w-xs truncate" title={strat.description}>
                                                {strat.description}
                                            </td>
                                            <td className={`px-6 py-4 font-mono font-bold ${metrics && metrics.sharpe_ratio >= 1.25 ? 'text-emerald-400' : 'text-gray-400'}`}>
                                                {metrics ? metrics.sharpe_ratio.toFixed(2) : '-'}
                                            </td>
                                            <td className="px-6 py-4 font-mono">
                                                {metrics ? (metrics.win_rate * 100).toFixed(1) + '%' : '-'}
                                            </td>
                                            <td className="px-6 py-4 font-mono text-red-400">
                                                {metrics ? metrics.max_drawdown_pct.toFixed(2) + '%' : '-'}
                                            </td>
                                            <td className="px-6 py-4">
                                                {getStatusBadge(strat.lifecycle_state)}
                                            </td>
                                        </motion.tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    );
}
