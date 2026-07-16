import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function TradeOutcomeIntelligence() {
  const [mfeMaeDist, setMfeMaeDist] = useState(null);
  const [comparisons, setComparisons] = useState(null);
  const [qualityData, setQualityData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const distRes = await fetch('http://localhost:8000/api/trade-outcomes/mfe-mae-dist');
        const distData = await distRes.json();
        
        const compRes = await fetch('http://localhost:8000/api/trade-outcomes/labels/comparison');
        const compData = await compRes.json();
        
        const qualRes = await fetch('http://localhost:8000/api/trade-outcomes/quality-distribution');
        if (qualRes.ok) {
            const qualData = await qualRes.json();
            setQualityData(qualData);
        }
        
        setMfeMaeDist(distData);
        setComparisons(compData);
        setLoading(false);
      } catch (e) {
        console.error("Failed to fetch trade outcomes:", e);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="p-8 text-white min-h-screen bg-gray-900 font-sans">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-600 mb-2">Trade Outcome Intelligence</h1>
        <p className="text-gray-400">Institutional evaluation of Maximum Favorable Excursion and generated target labels.</p>
      </motion.div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="space-y-8">
          
          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
            <h2 className="text-2xl font-bold mb-6 text-gray-100">Label Strategy Comparison</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {comparisons && comparisons.metrics && Object.entries(comparisons.metrics).map(([strategy, metrics]) => (
                <div key={strategy} className="bg-gray-750 p-5 rounded-lg border border-gray-600 bg-gray-800 transition transform hover:-translate-y-1 hover:shadow-2xl">
                  <h3 className="text-xl font-bold text-blue-400 mb-4 uppercase tracking-wider">{strategy.replace('_label', '').replace('_', ' ')}</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between border-b border-gray-700 pb-2">
                      <span className="text-gray-400">Class Balance</span>
                      <span className="font-semibold text-gray-100">{metrics.class_balance_pct}%</span>
                    </div>
                    <div className="flex justify-between border-b border-gray-700 pb-2">
                      <span className="text-gray-400">Avg Return</span>
                      <span className="font-semibold text-green-400">+{metrics.average_return_pct}%</span>
                    </div>
                    <div className="flex justify-between border-b border-gray-700 pb-2">
                      <span className="text-gray-400">Target Hit Rate</span>
                      <span className="font-semibold text-gray-100">{metrics.target_hit_rate_pct}%</span>
                    </div>
                    <div className="flex justify-between border-b border-gray-700 pb-2">
                      <span className="text-gray-400">Stop Loss Rate</span>
                      <span className="font-semibold text-red-400">{metrics.stop_loss_rate_pct}%</span>
                    </div>
                    <div className="flex justify-between pt-1">
                      <span className="text-gray-400">Hold Period</span>
                      <span className="font-semibold text-gray-100">{metrics.average_holding_period} Days</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
            <h2 className="text-2xl font-bold mb-6 text-gray-100">Trade Quality Scoring</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              <div className="bg-gray-750 p-5 rounded-lg border border-gray-600">
                 <h3 className="text-xl font-bold text-indigo-400 mb-2 tracking-wider">Average Quality Score</h3>
                 <p className="text-5xl font-extrabold text-white mb-4">
                    {qualityData ? qualityData.average_score : 'N/A'} <span className="text-xl text-gray-400">/ 100</span>
                 </p>
                 <p className="text-sm text-gray-400">Calculated over all historically simulated trades based on execution realism rules (T+1 Open entry).</p>
              </div>

              <div className="bg-gray-750 p-5 rounded-lg border border-gray-600">
                 <h3 className="text-xl font-bold text-indigo-400 mb-2 tracking-wider">Quality Distribution</h3>
                 {qualityData && qualityData.distribution ? (
                    <div className="space-y-2 mt-4">
                      {Object.entries(qualityData.distribution).map(([cat, count]) => (
                        <div key={cat} className="flex justify-between items-center text-sm">
                           <span className={`font-medium ${cat === 'Exceptional Breakout' ? 'text-green-400' : cat === 'Avoid' ? 'text-red-400' : 'text-gray-300'}`}>{cat}</span>
                           <span className="text-gray-100">{count.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                 ) : (
                    <div className="text-gray-500">No distribution data</div>
                 )}
              </div>

            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
            <h2 className="text-2xl font-bold mb-2 text-gray-100">MFE vs MAE Scatter</h2>
            <p className="text-gray-400 mb-6 text-sm">Visualizing the excursion path of sampled trades.</p>
            {mfeMaeDist && mfeMaeDist.mfe ? (
              <div className="h-64 flex items-center justify-center border border-gray-700 rounded bg-gray-900">
                <p className="text-gray-500 italic">Scatter plot visualization placeholder (Integration with Recharts/Plotly required)</p>
              </div>
            ) : (
              <div className="text-red-400 bg-red-900/20 p-4 rounded">No MFE/MAE data available. Please run the trade replay engine.</div>
            )}
          </div>
          
        </div>
      )}
    </div>
  );
}
