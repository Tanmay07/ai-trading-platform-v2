import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Crosshair, ShieldAlert, Target, TrendingUp, AlertOctagon, ArrowRight, Zap, List } from 'lucide-react';

export default function ExecutionIntelligence() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [viewMode, setViewMode] = useState('list'); // 'list' or 'detailed'
    const [selectedPlan, setSelectedPlan] = useState(null);

    const generatePlans = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('http://localhost:8000/execution/mock');
            if (!res.ok) throw new Error("Failed to generate execution plans");
            const result = await res.json();
            setData(result);
            if (result.execution_plans.length > 0) {
                setSelectedPlan(result.execution_plans[0]);
            }
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
                        <h1 className="text-4xl font-black text-white tracking-tight">Institutional Execution Engine</h1>
                        <p className="text-gray-400 mt-2 text-lg">Execution Strategy Framework (Phase F2)</p>
                    </div>
                    <button 
                        onClick={generatePlans}
                        disabled={loading}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-indigo-900/50 transition-all flex items-center gap-2"
                    >
                        <Zap size={18} />
                        {loading ? 'Planning...' : 'Generate Trade Plans'}
                    </button>
                </div>

                {error && (
                    <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg flex items-center gap-3">
                        <AlertOctagon /> {error}
                    </div>
                )}

                {data && (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        {/* Risk & Analytics Dashboard */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium flex items-center gap-2"><Target size={16}/> Execution Quality</p>
                                <p className="text-4xl font-black text-emerald-400 mt-2">
                                    {(data.analytics.avg_risk_reward).toFixed(2)}x
                                </p>
                                <p className="text-xs text-gray-500 mt-1">Avg Risk/Reward Ratio</p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium flex items-center gap-2"><ShieldAlert size={16}/> Total Portfolio Risk</p>
                                <p className="text-4xl font-black text-white mt-2">
                                    {(data.analytics.portfolio_risk_pct * 100).toFixed(2)}%
                                </p>
                                <p className="text-xs text-gray-500 mt-1">Budget utilization</p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Risk Exposure ($)</p>
                                <p className="text-4xl font-black text-orange-400 mt-2">
                                    ${data.analytics.total_risk_dollars.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">Max potential loss</p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Plans Generated</p>
                                <p className="text-4xl font-black text-indigo-400 mt-2">{data.analytics.total_plans}</p>
                                <p className="text-xs text-gray-500 mt-1">{data.rejected_plans.length} rejected</p>
                            </div>
                        </div>

                        {/* Master Detail View */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            
                            {/* List of Plans */}
                            <div className="lg:col-span-1 bg-gray-800 rounded-xl border border-gray-700 shadow-md overflow-hidden flex flex-col">
                                <div className="p-4 border-b border-gray-700 bg-gray-800/50 flex justify-between items-center">
                                    <h2 className="text-lg font-bold text-white flex items-center gap-2"><List size={18}/> Trade Queue</h2>
                                </div>
                                <div className="overflow-y-auto max-h-[600px]">
                                    {data.execution_plans.map((plan, idx) => (
                                        <div 
                                            key={idx} 
                                            onClick={() => setSelectedPlan(plan)}
                                            className={`p-4 border-b border-gray-700 cursor-pointer transition-colors ${selectedPlan?.symbol === plan.symbol ? 'bg-indigo-900/30 border-l-4 border-l-indigo-500' : 'hover:bg-gray-750'}`}
                                        >
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <span className="font-bold text-xl text-white">{plan.symbol}</span>
                                                    <div className="flex items-center gap-2 mt-1">
                                                        <span className="bg-green-900/30 text-green-400 px-2 py-0.5 rounded text-xs font-bold border border-green-800">{plan.action}</span>
                                                        <span className="text-xs text-gray-400">{plan.entry_strategy}</span>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <div className="text-emerald-400 font-mono text-sm">{plan.risk_reward.toFixed(1)} R/R</div>
                                                    <div className="text-gray-500 text-xs mt-1">Risk: ${(plan.risk_dollars).toFixed(0)}</div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Detailed Execution Plan */}
                            {selectedPlan && (
                                <div className="lg:col-span-2 space-y-6">
                                    
                                    {/* Blueprint */}
                                    <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                        <div className="flex justify-between items-center mb-6">
                                            <div>
                                                <h2 className="text-2xl font-black text-white flex items-center gap-3">
                                                    {selectedPlan.symbol} <span className="bg-green-900/30 text-green-400 px-3 py-1 rounded text-sm font-bold border border-green-800 uppercase tracking-widest">{selectedPlan.action}</span>
                                                </h2>
                                                <p className="text-gray-400 mt-1">Capital Allocated: <span className="text-white font-mono">${selectedPlan.capital_allocated.toLocaleString()}</span></p>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-3xl font-black text-indigo-400">{selectedPlan.risk_reward.toFixed(2)}x</div>
                                                <div className="text-gray-500 text-sm">Risk/Reward</div>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                            <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                                                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1 flex items-center gap-1"><Crosshair size={12}/> Entry</div>
                                                <div className="text-xl font-mono text-white">${selectedPlan.entry_price.toFixed(2)}</div>
                                                <div className="text-xs text-indigo-400 mt-1 truncate">{selectedPlan.entry_strategy}</div>
                                            </div>
                                            <div className="bg-red-900/10 p-4 rounded-lg border border-red-900/30">
                                                <div className="text-xs text-red-500 uppercase tracking-wider mb-1 flex items-center gap-1"><ShieldAlert size={12}/> Stop Loss</div>
                                                <div className="text-xl font-mono text-red-400">${selectedPlan.stop_loss.toFixed(2)}</div>
                                                <div className="text-xs text-gray-500 mt-1">Risking ${(selectedPlan.risk_dollars).toFixed(0)}</div>
                                            </div>
                                            <div className="bg-green-900/10 p-4 rounded-lg border border-green-900/30">
                                                <div className="text-xs text-green-500 uppercase tracking-wider mb-1 flex items-center gap-1"><Target size={12}/> Target 1</div>
                                                <div className="text-xl font-mono text-green-400">${selectedPlan.target_1.toFixed(2)}</div>
                                                <div className="text-xs text-gray-500 mt-1">Partial Exit (50%)</div>
                                            </div>
                                            <div className="bg-emerald-900/10 p-4 rounded-lg border border-emerald-900/30">
                                                <div className="text-xs text-emerald-500 uppercase tracking-wider mb-1 flex items-center gap-1"><TrendingUp size={12}/> Stretch</div>
                                                <div className="text-xl font-mono text-emerald-400">${selectedPlan.stretch_target.toFixed(2)}</div>
                                                <div className="text-xs text-gray-500 mt-1">Max Potential</div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Trade Lifecycle Visual */}
                                    <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                        <h3 className="text-lg font-bold text-white mb-6">Trade Lifecycle Plan</h3>
                                        
                                        <div className="flex items-center justify-between text-sm relative">
                                            {/* Connecting Line */}
                                            <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-700 -translate-y-1/2 z-0"></div>
                                            
                                            <div className="relative z-10 flex flex-col items-center gap-2 bg-gray-800 px-2">
                                                <div className="w-8 h-8 rounded-full bg-blue-900 text-blue-400 flex items-center justify-center font-bold border-2 border-blue-500">1</div>
                                                <span className="text-gray-300 font-medium">Entry</span>
                                                <span className="text-gray-500 text-xs">${selectedPlan.entry_price.toFixed(2)}</span>
                                            </div>
                                            
                                            <div className="relative z-10 flex flex-col items-center gap-2 bg-gray-800 px-2">
                                                <div className="w-8 h-8 rounded-full bg-green-900 text-green-400 flex items-center justify-center font-bold border-2 border-green-500">2</div>
                                                <span className="text-gray-300 font-medium">Target 1</span>
                                                <span className="text-gray-500 text-xs">Sell 50%</span>
                                            </div>
                                            
                                            <div className="relative z-10 flex flex-col items-center gap-2 bg-gray-800 px-2">
                                                <div className="w-8 h-8 rounded-full bg-indigo-900 text-indigo-400 flex items-center justify-center font-bold border-2 border-indigo-500">3</div>
                                                <span className="text-gray-300 font-medium">Trailing Stop</span>
                                                <span className="text-gray-500 text-xs">{selectedPlan.trailing_stop}</span>
                                            </div>

                                            <div className="relative z-10 flex flex-col items-center gap-2 bg-gray-800 px-2">
                                                <div className="w-8 h-8 rounded-full bg-emerald-900 text-emerald-400 flex items-center justify-center font-bold border-2 border-emerald-500">4</div>
                                                <span className="text-gray-300 font-medium">Exit</span>
                                                <span className="text-gray-500 text-xs">{selectedPlan.holding_period} Days Max</span>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    {/* Alternative Strategies */}
                                    {selectedPlan.alternative_entries && selectedPlan.alternative_entries.length > 0 && (
                                        <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2"><Layers size={18}/> Alternative Entry Strategies</h3>
                                            <div className="space-y-3">
                                                {selectedPlan.alternative_entries.map((alt, aidx) => (
                                                    <div key={aidx} className="flex justify-between items-center bg-gray-900/50 p-3 rounded border border-gray-700">
                                                        <div>
                                                            <div className="text-sm font-medium text-gray-300">{alt.name}</div>
                                                            <div className="text-xs text-gray-500 mt-0.5">Entry: ${alt.entry_price.toFixed(2)} • Validity: {alt.validity_window.replace('_', ' ')}</div>
                                                        </div>
                                                        <div className="text-right">
                                                            <div className="text-sm font-bold text-indigo-400">{alt.score}/100</div>
                                                            <div className="text-xs text-gray-500 mt-0.5">Strategy Score</div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
