import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function PortfolioIntelligence() {
    const [portfolioData, setPortfolioData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const buildPortfolio = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('http://localhost:8000/portfolio/build', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ available_cash: 100000 })
            });
            if (!res.ok) throw new Error("Failed to build portfolio");
            const data = await res.json();
            setPortfolioData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-gray-100 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                
                {/* Header */}
                <div className="flex justify-between items-end border-b border-gray-700 pb-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight">Institutional Portfolio Engine</h1>
                        <p className="text-gray-400 mt-2 text-lg">Constraint-Based Optimization Framework (Phase F1)</p>
                    </div>
                    <button 
                        onClick={buildPortfolio}
                        disabled={loading}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-indigo-900/50 transition-all disabled:opacity-50"
                    >
                        {loading ? 'Optimizing...' : 'Build Optimal Portfolio'}
                    </button>
                </div>

                {error && (
                    <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg">
                        {error}
                    </div>
                )}

                {portfolioData && (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        {/* Metrics Overview */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Portfolio Health Score</p>
                                <p className="text-4xl font-black text-emerald-400 mt-2">{portfolioData.metrics.health_score}/100</p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Positions Allocated</p>
                                <p className="text-4xl font-black text-white mt-2">{portfolioData.metrics.positions_count}</p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Capital Deployed</p>
                                <p className="text-4xl font-black text-blue-400 mt-2">
                                    ${portfolioData.metrics.total_allocated.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                                </p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Cash Reserves</p>
                                <p className="text-4xl font-black text-gray-300 mt-2">
                                    ${portfolioData.metrics.cash_remaining.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            {/* Recommended Allocations */}
                            <div className="lg:col-span-2 bg-gray-800 rounded-xl border border-gray-700 shadow-md overflow-hidden">
                                <div className="p-6 border-b border-gray-700 bg-gray-800/50">
                                    <h2 className="text-xl font-bold text-white">Recommended Allocations</h2>
                                </div>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left border-collapse">
                                        <thead>
                                            <tr className="bg-gray-900/50 text-gray-400 text-xs uppercase tracking-wider">
                                                <th className="p-4 font-semibold">Symbol</th>
                                                <th className="p-4 font-semibold">Sector</th>
                                                <th className="p-4 font-semibold">AI Quality</th>
                                                <th className="p-4 font-semibold text-right">Target Weight</th>
                                                <th className="p-4 font-semibold text-right">Allocation</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-700">
                                            {portfolioData.portfolio.map((pos, idx) => (
                                                <tr key={idx} className="hover:bg-gray-750 transition-colors">
                                                    <td className="p-4 font-bold text-indigo-300">{pos.symbol}</td>
                                                    <td className="p-4 text-gray-300 text-sm">{pos.sector}</td>
                                                    <td className="p-4">
                                                        <span className="bg-emerald-900/30 text-emerald-400 px-2 py-1 rounded font-mono text-sm">
                                                            {pos.trade_quality_prediction.toFixed(1)}
                                                        </span>
                                                    </td>
                                                    <td className="p-4 text-right font-mono text-gray-300">
                                                        {(pos.weight * 100).toFixed(1)}%
                                                    </td>
                                                    <td className="p-4 text-right font-mono text-green-400">
                                                        ${pos.capital_allocated.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            {/* Sidebar Analytics */}
                            <div className="space-y-8">
                                {/* Sector Exposure */}
                                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                    <h2 className="text-xl font-bold text-white mb-4">Sector Exposure</h2>
                                    <div className="space-y-4">
                                        {Object.entries(portfolioData.metrics.sector_exposure)
                                            .sort(([,a], [,b]) => b - a)
                                            .map(([sector, weight], idx) => (
                                            <div key={idx}>
                                                <div className="flex justify-between text-sm mb-1">
                                                    <span className="text-gray-300">{sector}</span>
                                                    <span className="text-gray-400 font-mono">{(weight * 100).toFixed(1)}%</span>
                                                </div>
                                                <div className="w-full bg-gray-700 rounded-full h-2">
                                                    <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${weight * 100}%` }}></div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Rejections */}
                                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                    <h2 className="text-xl font-bold text-white mb-1">Constraint Rejections</h2>
                                    <p className="text-sm text-gray-400 mb-4">{portfolioData.rejected_candidates.length} opportunities blocked</p>
                                    <div className="space-y-3 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
                                        {portfolioData.rejected_candidates.slice(0, 10).map((rej, idx) => (
                                            <div key={idx} className="bg-gray-900 p-3 rounded border border-red-900/30">
                                                <div className="flex justify-between items-center mb-1">
                                                    <span className="font-bold text-gray-300 text-sm">{rej.symbol}</span>
                                                    <span className="text-xs text-red-400 bg-red-900/20 px-2 py-0.5 rounded">Rejected</span>
                                                </div>
                                                <ul className="text-xs text-gray-500 list-disc pl-4 space-y-0.5">
                                                    {rej.rejection_reasons.map((reason, ridx) => (
                                                        <li key={ridx}>{reason}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
