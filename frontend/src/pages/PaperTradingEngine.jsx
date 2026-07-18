import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Target, TrendingUp, TrendingDown, DollarSign, Activity, Archive, BarChart2, PlayCircle, RefreshCw, AlertCircle } from 'lucide-react';

export default function PaperTradingEngine() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const runSimulation = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('http://localhost:8000/paper_trading/simulate', { method: 'POST' });
            if (!res.ok) throw new Error("Failed to run paper trading simulation");
            const result = await res.json();
            setData(result);
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
                        <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                            <Target className="text-emerald-500" size={36} /> Paper Trading Engine
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg">Institutional Simulator & Performance Attribution (Phase F4)</p>
                    </div>
                    <button 
                        onClick={runSimulation}
                        disabled={loading}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-emerald-900/50 transition-all flex items-center gap-2"
                    >
                        {loading ? <RefreshCw className="animate-spin" size={18} /> : <PlayCircle size={18} />}
                        {loading ? 'Simulating...' : 'Run Portfolio Simulation'}
                    </button>
                </div>

                {error && (
                    <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg flex items-center gap-3">
                        <AlertCircle /> {error}
                    </div>
                )}

                {data && (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        {/* Portfolio Summary Widgets */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium flex items-center gap-2"><DollarSign size={16}/> Portfolio NAV</p>
                                <p className="text-4xl font-black text-white mt-2 flex items-baseline gap-1">
                                    <span className="text-xl text-gray-500">₹</span>
                                    {data.portfolio_summary.nav.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                                </p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium flex items-center gap-2"><Activity size={16}/> Total Return</p>
                                <p className={`text-4xl font-black mt-2 flex items-center gap-2 ${data.portfolio_summary.total_return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {data.portfolio_summary.total_return_pct >= 0 ? <TrendingUp size={28} /> : <TrendingDown size={28} />}
                                    {data.portfolio_summary.total_return_pct.toFixed(2)}%
                                </p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Available Cash</p>
                                <p className="text-4xl font-black text-indigo-400 mt-2">
                                    ₹{data.portfolio_summary.cash.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                                </p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Trades Executed</p>
                                <p className="text-4xl font-black text-blue-400 mt-2">
                                    {data.portfolio_summary.open_positions_count + data.portfolio_summary.closed_positions_count}
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            {/* Open Positions */}
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md overflow-hidden">
                                <div className="p-4 border-b border-gray-700 bg-gray-900/50 flex justify-between items-center">
                                    <h2 className="text-lg font-bold text-white flex items-center gap-2"><BarChart2 size={18}/> Active Positions</h2>
                                    <span className="bg-indigo-900/50 text-indigo-400 px-2 py-1 rounded text-xs font-bold">{data.portfolio_summary.open_positions_count} Open</span>
                                </div>
                                <div className="p-4 space-y-4">
                                    {Object.values(data.open_positions).length === 0 && (
                                        <div className="text-center text-gray-500 py-8">No open positions.</div>
                                    )}
                                    {Object.values(data.open_positions).map((pos, idx) => (
                                        <div key={idx} className="bg-gray-900/50 p-4 rounded-lg border border-gray-700 flex justify-between items-center">
                                            <div>
                                                <div className="font-bold text-lg text-white">{pos.symbol}</div>
                                                <div className="text-sm text-gray-400 mt-1">Shares: {pos.shares.toFixed(2)}</div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-gray-400 text-sm">Entry: ₹{pos.entry_price.toFixed(2)}</div>
                                                <div className="text-indigo-400 font-bold">Current: ₹{pos.current_price.toFixed(2)}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Closed Trades / Journal */}
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md overflow-hidden">
                                <div className="p-4 border-b border-gray-700 bg-gray-900/50 flex justify-between items-center">
                                    <h2 className="text-lg font-bold text-white flex items-center gap-2"><Archive size={18}/> Trade Journal</h2>
                                    <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-xs font-bold">{data.portfolio_summary.closed_positions_count} Closed</span>
                                </div>
                                <div className="p-4 space-y-4">
                                    {data.closed_trades.length === 0 && (
                                        <div className="text-center text-gray-500 py-8">No closed trades yet.</div>
                                    )}
                                    {data.closed_trades.map((pos, idx) => (
                                        <div key={idx} className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                                            <div className="flex justify-between items-start mb-3">
                                                <div>
                                                    <div className="font-bold text-lg text-white flex items-center gap-2">
                                                        {pos.symbol}
                                                        <span className={`text-xs px-2 py-0.5 rounded font-bold ${pos.pnl > 0 ? 'bg-emerald-900/50 text-emerald-400 border border-emerald-800' : 'bg-red-900/50 text-red-400 border border-red-800'}`}>
                                                            {pos.exit_reason.replace(/_/g, ' ')}
                                                        </span>
                                                    </div>
                                                    <div className="text-sm text-gray-400 mt-1">Held for {pos.days_held} days</div>
                                                </div>
                                                <div className="text-right">
                                                    <div className={`text-xl font-black ${pos.pnl > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                        {pos.pnl > 0 ? '+' : ''}₹{pos.pnl.toFixed(2)}
                                                    </div>
                                                    <div className={`text-sm ${pos.return_pct > 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                                                        {(pos.return_pct * 100).toFixed(2)}%
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            {/* Attribution Snippet */}
                                            <div className="mt-3 pt-3 border-t border-gray-800">
                                                <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Performance Attribution (F5 Repository Link)</div>
                                                <div className="flex gap-2">
                                                    <span className={`text-xs px-2 py-1 rounded ${pos.pnl > 0 ? 'bg-indigo-900/30 text-indigo-400' : 'bg-gray-800 text-gray-400'}`}>Prediction Component: {pos.pnl > 0 ? '+Value' : '-Value'}</span>
                                                    <span className={`text-xs px-2 py-1 rounded ${pos.pnl > 0 ? 'bg-indigo-900/30 text-indigo-400' : 'bg-gray-800 text-gray-400'}`}>Execution Component: {pos.pnl > 0 ? '+Value' : '-Value'}</span>
                                                </div>
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
