import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function ModelArena() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);

  const fetchReport = () => {
    fetch('http://localhost:8000/api/benchmark/report')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const triggerBenchmark = () => {
    setRunning(true);
    fetch('http://localhost:8000/api/benchmark/run', { method: 'POST' })
      .then(() => {
          setTimeout(() => {
              setRunning(false);
              fetchReport();
          }, 3000); // Simulate wait for demo
      });
  };

  return (
    <div className="p-8 text-white min-h-screen bg-gray-900 font-sans">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex justify-between items-center mb-10">
        <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-600 mb-2">Champion-Challenger Arena</h1>
            <p className="text-gray-400">Institutional Feature Benchmarking & Promotion Engine</p>
        </div>
        <button 
            onClick={triggerBenchmark}
            disabled={running}
            className={`px-6 py-3 rounded-lg font-bold ${running ? 'bg-gray-700 text-gray-500' : 'bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-400 hover:to-red-500 text-white shadow-lg'}`}
        >
            {running ? 'Benchmarking...' : 'Run Benchmark'}
        </button>
      </motion.div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
        </div>
      ) : data?.status === 'not_run_yet' ? (
        <div className="bg-gray-800 p-12 rounded-xl border border-gray-700 text-center flex flex-col items-center">
            <h2 className="text-2xl font-bold mb-4">Arena is Empty</h2>
            <p className="text-gray-400 mb-8 max-w-lg">The benchmark has not been run yet. Click 'Run Benchmark' to train identical LightGBM models on Raw, Factor, and Hybrid feature sets, and evaluate them through the Promotion Engine.</p>
        </div>
      ) : error ? (
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 text-center text-red-400">
            {error}
        </div>
      ) : data ? (
        <div className="space-y-8">
            
            {/* Promotion Decision */}
            <div className={`p-6 rounded-xl border shadow-xl ${data.promotion_recommendation.promote ? 'bg-green-900/20 border-green-700' : 'bg-red-900/20 border-red-700'}`}>
                <h2 className="text-2xl font-bold mb-2">Promotion Decision: {data.promotion_recommendation.promote ? 'ACCEPTED' : 'REJECTED'}</h2>
                <p className="text-lg text-gray-300">{data.promotion_recommendation.reason}</p>
                <p className="text-sm text-gray-400 mt-2">Challenger Evaluated: {data.promotion_recommendation.challenger.toUpperCase()}</p>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                
                {/* Models Leaderboard */}
                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl col-span-1 xl:col-span-3">
                    <h2 className="text-2xl font-bold mb-4 text-orange-400">Model Leaderboard</h2>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-gray-400 border-b border-gray-700">
                                    <th className="pb-3">Feature Set</th>
                                    <th className="pb-3">ROC-AUC</th>
                                    <th className="pb-3">Precision@20</th>
                                    <th className="pb-3">Profit Factor</th>
                                    <th className="pb-3">Win Rate</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(data.models).map(([name, metrics]) => (
                                    <tr key={name} className="border-b border-gray-750 hover:bg-gray-750">
                                        <td className="py-4 font-bold text-white capitalize">
                                            {name} {name === data.champion ? '🏆 (Champ)' : ''}
                                        </td>
                                        <td className="py-4">{(metrics.cv_roc_auc || 0).toFixed(4)}</td>
                                        <td className="py-4">{(metrics.test_precision_20 || 0).toFixed(2)}</td>
                                        <td className="py-4">{(metrics.test_profit_factor || 0).toFixed(2)}</td>
                                        <td className="py-4">{(metrics.test_win_rate || 0).toFixed(2)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Ablation */}
                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl col-span-1 xl:col-span-2">
                    <h2 className="text-xl font-bold mb-4 text-blue-400">Feature Ablation (Drop-One)</h2>
                    <div className="space-y-3">
                        {data.feature_intelligence.ablation.map((f, i) => (
                            <div key={i} className="flex justify-between items-center p-3 bg-gray-750 rounded border border-gray-600">
                                <div>
                                    <p className="font-bold">{f.factor.replace(/_/g, ' ')}</p>
                                    <p className={`text-xs ${f.classification === 'Essential' ? 'text-green-400' : 'text-gray-400'}`}>{f.classification}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-bold text-red-400">ROC Impact: {f.performance_impact.toFixed(4)}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
                
                {/* Redundancies */}
                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl col-span-1">
                    <h2 className="text-xl font-bold mb-4 text-yellow-400">Redundancy Warnings</h2>
                    <div className="space-y-3">
                        {data.feature_intelligence.redundancies.length === 0 ? (
                            <p className="text-gray-400 italic">No highly correlated redundancies found.</p>
                        ) : (
                            data.feature_intelligence.redundancies.map((r, i) => (
                                <div key={i} className="p-3 bg-gray-750 rounded border border-yellow-900/50">
                                    <p className="font-bold text-sm">{r.raw_feature}</p>
                                    <p className="text-xs text-gray-400 mt-1">Captured by: {r.covered_by_factor}</p>
                                    <p className="text-xs text-yellow-500 mt-1">Corr: {r.correlation.toFixed(2)}</p>
                                </div>
                            ))
                        )}
                    </div>
                </div>

            </div>
        </div>
      ) : null}
    </div>
  );
}
