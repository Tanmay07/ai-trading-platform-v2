import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, ShieldAlert, Cpu, Layers, Maximize2, Split, Clock, ActivitySquare } from 'lucide-react';

export default function MarketRegime() {
    const [regimeData, setRegimeData] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [twinData, setTwinData] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [regRes, recRes, twinRes] = await Promise.all([
                fetch('http://localhost:8000/regime/current'),
                fetch('http://localhost:8000/regime/recommendations'),
                fetch('http://localhost:8000/regime/digital_twin')
            ]);
            setRegimeData(await regRes.json());
            setRecommendations(await recRes.json());
            setTwinData(await twinRes.json());
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const formatRegimeLabel = (str) => {
        return str.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    };

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-gray-100 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                
                {/* Header */}
                <div className="flex justify-between items-end border-b border-gray-700 pb-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                            <ActivitySquare className="text-pink-500" size={36} /> Market Regime & Digital Twin
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg">Adaptive Macro Intelligence Engine (Phase G5)</p>
                    </div>
                    <button 
                        onClick={fetchData}
                        disabled={loading}
                        className="bg-pink-600 hover:bg-pink-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-pink-900/50 transition-all flex items-center gap-2"
                    >
                        {loading ? <Activity className="animate-spin" size={18} /> : <Cpu size={18} />}
                        {loading ? 'Detecting...' : 'Detect Regime'}
                    </button>
                </div>

                {regimeData && recommendations && twinData && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        
                        {/* Current Regime */}
                        <div className="lg:col-span-1 space-y-8">
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6 relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-4 opacity-10">
                                    <Activity size={100} />
                                </div>
                                <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-2">Current Regime</h2>
                                <div className="text-3xl font-black text-white text-pink-400 mb-4">
                                    {formatRegimeLabel(regimeData.regime)}
                                </div>
                                
                                <div className="flex items-end justify-between mb-6">
                                    <div>
                                        <div className="text-xs text-gray-500">Ensemble Confidence</div>
                                        <div className="text-2xl font-mono text-white">{regimeData.confidence}%</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xs text-gray-500">Models Active</div>
                                        <div className="text-lg font-bold text-gray-300">{Object.keys(regimeData.model_votes).length}</div>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <h3 className="text-xs font-bold text-gray-400 uppercase">Detection Evidence</h3>
                                    {regimeData.evidence.map((ev, i) => (
                                        <div key={i} className="bg-gray-900 text-gray-300 text-sm p-2 rounded border border-gray-700">
                                            • {ev}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Risk Budgets */}
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                                    <ShieldAlert size={16} /> Dynamic Risk Budget
                                </h2>
                                {recommendations.risk_recommendation.digital_twin_volatility_override && (
                                    <div className="bg-red-900/30 text-red-400 text-xs p-2 rounded mb-4 border border-red-900/50">
                                        ⚠️ Target Volatility reduced due to Digital Twin tail-risk forecast.
                                    </div>
                                )}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-gray-900 p-3 rounded">
                                        <div className="text-xs text-gray-500">Target Vol</div>
                                        <div className="text-xl font-mono text-white">{(recommendations.risk_recommendation.risk_budgets.target_volatility * 100).toFixed(1)}%</div>
                                    </div>
                                    <div className="bg-gray-900 p-3 rounded">
                                        <div className="text-xs text-gray-500">Max Exposure</div>
                                        <div className="text-xl font-mono text-white">{(recommendations.risk_recommendation.risk_budgets.max_exposure * 100).toFixed(0)}%</div>
                                    </div>
                                    <div className="bg-gray-900 p-3 rounded">
                                        <div className="text-xs text-gray-500">Stop Loss Mult</div>
                                        <div className="text-xl font-mono text-white">{recommendations.risk_recommendation.risk_budgets.stop_loss_multiplier.toFixed(1)}x</div>
                                    </div>
                                    <div className="bg-gray-900 p-3 rounded">
                                        <div className="text-xs text-gray-500">Sector Limit</div>
                                        <div className="text-xl font-mono text-white">{(recommendations.risk_recommendation.risk_budgets.sector_concentration * 100).toFixed(0)}%</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Middle & Right Column */}
                        <div className="lg:col-span-2 space-y-8">
                            
                            {/* Market Digital Twin */}
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                    <Split className="text-blue-400" size={24} /> Market Digital Twin (Simulated Paths)
                                </h2>
                                <p className="text-gray-400 text-sm mb-6">
                                    Simulating {twinData.paths_simulated} probabilistic market paths across multiple horizons to forecast regime transitions and expected risk/return.
                                </p>
                                
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    {['5d', '20d', '60d'].map((horizon) => {
                                        const proj = twinData.projections[horizon];
                                        return (
                                            <div key={horizon} className="bg-gray-900 rounded-lg p-4 border border-gray-700 relative overflow-hidden">
                                                <div className="flex justify-between items-center mb-4">
                                                    <span className="text-blue-400 font-bold flex items-center gap-1">
                                                        <Clock size={14}/> {horizon} Horizon
                                                    </span>
                                                    {proj.tail_risk_probability > 0.15 && (
                                                        <span className="text-xs bg-red-900/50 text-red-400 px-2 py-0.5 rounded">High Tail Risk</span>
                                                    )}
                                                </div>
                                                
                                                <div className="space-y-4">
                                                    <div>
                                                        <div className="text-xs text-gray-500 uppercase mb-1">Expected Return</div>
                                                        <div className={`text-2xl font-black font-mono ${proj.expected_return >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                            {proj.expected_return > 0 ? '+' : ''}{proj.expected_return.toFixed(1)}%
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <div className="text-xs text-gray-500 uppercase mb-1">Expected Volatility</div>
                                                        <div className="text-lg font-mono text-gray-200">
                                                            {proj.expected_volatility.toFixed(1)}%
                                                        </div>
                                                    </div>
                                                    <div className="pt-2 border-t border-gray-800">
                                                        <div className="text-xs text-gray-500 uppercase mb-2">Probable Transition</div>
                                                        <div className="space-y-1">
                                                            {Object.entries(proj.regime_distribution)
                                                                .sort((a,b) => b[1] - a[1])
                                                                .slice(0,2).map(([r, prob]) => (
                                                                <div key={r} className="flex justify-between text-xs">
                                                                    <span className="text-gray-400 truncate pr-2">{formatRegimeLabel(r)}</span>
                                                                    <span className="text-white font-mono">{(prob*100).toFixed(0)}%</span>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            </div>

                            {/* Strategy Adaptation */}
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                        <Layers className="text-emerald-400" size={24} /> Recommended Strategy Allocation
                                    </h2>
                                </div>
                                {recommendations.digital_twin_adjustment_applied && (
                                    <div className="bg-orange-900/30 text-orange-400 text-sm p-3 rounded mb-6 border border-orange-900/50">
                                        💡 Cash allocation automatically increased due to elevated 20-day panic probability in the Digital Twin forecast.
                                    </div>
                                )}
                                
                                <div className="space-y-4">
                                    {Object.entries(recommendations.strategy_recommendation.recommended_weights)
                                        .sort((a,b) => b[1] - a[1]).map(([strat, weight]) => (
                                        <div key={strat}>
                                            <div className="flex justify-between text-sm mb-1">
                                                <span className="text-gray-300 font-bold">{strat}</span>
                                                <span className="text-white font-mono">{weight.toFixed(1)}%</span>
                                            </div>
                                            <div className="h-3 bg-gray-900 rounded-full overflow-hidden border border-gray-700">
                                                <motion.div 
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${weight}%` }}
                                                    className={`h-full ${strat === 'Cash' ? 'bg-orange-500' : 'bg-emerald-500'}`}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
