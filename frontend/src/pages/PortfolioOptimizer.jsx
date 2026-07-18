import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Calculator, Play, AlertCircle, TrendingDown, Target, Zap, PieChart } from 'lucide-react';

export default function PortfolioOptimizer() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [method, setMethod] = useState('hrp');

    // Mock candidates from the Multi-Strategy layer
    const mockCandidates = [
        { symbol: "RELIANCE.NS", confidence: 0.85, strategy: "Momentum" },
        { symbol: "HDFCBANK.NS", confidence: 0.75, strategy: "Mean Reversion" },
        { symbol: "TCS.NS", confidence: 0.82, strategy: "Breakout" },
        { symbol: "INFY.NS", confidence: 0.88, strategy: "Sector Rotation" },
        { symbol: "SBIN.NS", confidence: 0.65, strategy: "Volatility" },
        { symbol: "ITC.NS", confidence: 0.71, strategy: "Momentum" },
        { symbol: "LARSEN.NS", confidence: 0.79, strategy: "Breakout" }
    ];

    const runOptimization = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/optimizer/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    method: method,
                    opportunity_universe: mockCandidates
                })
            });
            const data = await res.json();
            setResult(data);
        } catch (err) {
            console.error(err);
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
                            <Calculator className="text-orange-500" size={36} /> Portfolio Optimization
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg">Institutional Risk Allocation & Digital Twin (Phase G3)</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <select 
                            value={method} 
                            onChange={e => setMethod(e.target.value)}
                            className="bg-gray-800 border border-gray-700 text-white text-sm rounded-lg p-2.5"
                        >
                            <option value="hrp">Hierarchical Risk Parity (HRP)</option>
                            <option value="mean_variance">Mean-Variance (Markowitz)</option>
                            <option value="risk_parity">Equal Risk Parity</option>
                            <option value="black_litterman">Black-Litterman</option>
                        </select>
                        <button 
                            onClick={runOptimization}
                            disabled={loading}
                            className="bg-orange-600 hover:bg-orange-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-orange-900/50 transition-all flex items-center gap-2"
                        >
                            {loading ? <Activity className="animate-spin" size={18} /> : <Play size={18} />}
                            {loading ? 'Solving...' : 'Run Optimizer'}
                        </button>
                    </div>
                </div>

                {result && (
                    <div className="space-y-6">
                        
                        {/* Digital Twin Recommendation */}
                        <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`p-6 rounded-xl border shadow-md flex items-start gap-4 ${
                                result.rebalance_decision.recommendation === 'ACCEPT_REBALANCE' 
                                    ? 'bg-emerald-900/20 border-emerald-500/50' 
                                    : result.rebalance_decision.recommendation === 'DELAY_REBALANCE'
                                    ? 'bg-yellow-900/20 border-yellow-500/50'
                                    : 'bg-red-900/20 border-red-500/50'
                            }`}
                        >
                            <div className="mt-1">
                                {result.rebalance_decision.recommendation === 'ACCEPT_REBALANCE' ? <Target className="text-emerald-400" size={24} /> : 
                                 result.rebalance_decision.recommendation === 'DELAY_REBALANCE' ? <AlertCircle className="text-yellow-400" size={24} /> : 
                                 <AlertCircle className="text-red-400" size={24} />}
                            </div>
                            <div className="flex-1">
                                <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
                                    Digital Twin Decision: {result.rebalance_decision.recommendation.replace('_', ' ')}
                                </h2>
                                <p className="text-gray-300 mb-4">{result.rebalance_decision.reason}</p>
                                
                                <div className="grid grid-cols-3 gap-4">
                                    <div className="bg-gray-900/50 p-3 rounded border border-gray-700/50">
                                        <div className="text-xs text-gray-500 uppercase">Est. Turnover</div>
                                        <div className="text-lg font-bold font-mono">{result.rebalance_decision.turnover_pct}%</div>
                                    </div>
                                    <div className="bg-gray-900/50 p-3 rounded border border-gray-700/50">
                                        <div className="text-xs text-gray-500 uppercase">Transaction Costs</div>
                                        <div className="text-lg font-bold font-mono">{result.rebalance_decision.estimated_transaction_costs_pct}%</div>
                                    </div>
                                    <div className="bg-gray-900/50 p-3 rounded border border-gray-700/50">
                                        <div className="text-xs text-gray-500 uppercase">Marginal Return (Est)</div>
                                        <div className="text-lg font-bold font-mono text-emerald-400">+{result.rebalance_decision.expected_marginal_return_pct}%</div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            
                            {/* Optimal Weights */}
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <PieChart size={18} className="text-orange-400"/> Optimal Weights ({result.method.toUpperCase()})
                                </h2>
                                <div className="space-y-4">
                                    {Object.entries(result.weights).sort((a,b)=>b[1]-a[1]).map(([sym, w]) => (
                                        <div key={sym}>
                                            <div className="flex justify-between text-sm mb-1">
                                                <span className="font-bold text-gray-300">{sym}</span>
                                                <span className="text-orange-400 font-bold">{w.toFixed(2)}%</span>
                                            </div>
                                            <div className="w-full bg-gray-900 rounded-full h-2">
                                                <div className="h-2 rounded-full bg-orange-500" style={{ width: `${w}%` }}></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Risk & Stress Tests */}
                            <div className="space-y-6">
                                <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                    <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                        <Zap size={18} className="text-blue-400"/> Risk Estimate
                                    </h2>
                                    <div className="grid grid-cols-3 gap-4">
                                        <div>
                                            <div className="text-xs text-gray-500 uppercase">Est. Volatility</div>
                                            <div className="text-lg font-bold font-mono">{result.risk_metrics.estimated_volatility}</div>
                                        </div>
                                        <div>
                                            <div className="text-xs text-gray-500 uppercase">CVaR (95%)</div>
                                            <div className="text-lg font-bold font-mono text-red-400">{result.risk_metrics.estimated_cvar}</div>
                                        </div>
                                        <div>
                                            <div className="text-xs text-gray-500 uppercase">Div. Ratio</div>
                                            <div className="text-lg font-bold font-mono">{result.risk_metrics.diversification_ratio}</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                    <div className="flex justify-between items-center mb-4">
                                        <h2 className="text-lg font-bold text-white flex items-center gap-2">
                                            <TrendingDown size={18} className="text-red-400"/> Scenario Analysis
                                        </h2>
                                        <span className="px-2 py-1 bg-gray-900 rounded text-xs font-bold border border-gray-700">
                                            Resilience Score: <span className={result.stress_tests.portfolio_resilience_score > 70 ? 'text-emerald-400' : 'text-red-400'}>{result.stress_tests.portfolio_resilience_score}/100</span>
                                        </span>
                                    </div>
                                    <div className="space-y-3">
                                        {result.stress_tests.stress_tests.map((s, idx) => (
                                            <div key={idx} className="flex justify-between items-center border-b border-gray-700 pb-2">
                                                <span className="text-sm text-gray-300">{s.scenario_name}</span>
                                                <span className="font-mono text-red-400 font-bold">{s.simulated_drawdown_pct}%</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                )}
            </div>
        </div>
    );
}
