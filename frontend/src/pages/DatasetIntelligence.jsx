import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function DatasetIntelligence() {
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [building, setBuilding] = useState(false);

  useEffect(() => {
    fetchDataset();
  }, []);

  const fetchDataset = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/datasets/current');
      if (!res.ok) {
        if (res.status === 404) {
           setError("No dataset V2 found. Please trigger a build.");
           setLoading(false);
           return;
        }
        throw new Error("Failed to fetch dataset info");
      }
      const data = await res.json();
      setDataset(data);
      setLoading(false);
    } catch (e) {
      setError(e.message);
      setLoading(false);
    }
  };

  const triggerBuild = async () => {
    setBuilding(true);
    try {
      const res = await fetch('http://localhost:8000/api/datasets/build', { method: 'POST' });
      if (!res.ok) throw new Error("Failed to start build");
      alert("Dataset V2 Build Started! Check backend logs.");
    } catch (e) {
      alert(e.message);
    }
    setBuilding(false);
  };

  return (
    <div className="p-8 text-white min-h-screen bg-gray-900 font-sans">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex justify-between items-center mb-10">
        <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-emerald-600 mb-2">Dataset Intelligence</h1>
            <p className="text-gray-400">Institutional Dataset V2 - Lineage & Schema Analytics</p>
        </div>
        <button 
          onClick={triggerBuild}
          disabled={building}
          className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-6 rounded shadow-lg transition-colors"
        >
          {building ? "Building..." : "Trigger V2 Build"}
        </button>
      </motion.div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
        </div>
      ) : error ? (
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 text-center">
            <p className="text-gray-400 mb-4">{error}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
                <h2 className="text-2xl font-bold mb-4 text-emerald-400">Canonical Dataset</h2>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <p className="text-gray-400 text-sm">Version</p>
                        <p className="text-xl font-bold font-mono text-emerald-300">{dataset.version_id}</p>
                    </div>
                    <div>
                        <p className="text-gray-400 text-sm">Created At</p>
                        <p className="text-sm font-bold">{new Date(dataset.created_at).toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-gray-400 text-sm">Total Records</p>
                        <p className="text-2xl font-bold">{dataset.statistics.Total_Rows.toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-gray-400 text-sm">Symbol Coverage</p>
                        <p className="text-2xl font-bold">{dataset.statistics.Total_Symbols}</p>
                    </div>
                </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
                <h2 className="text-2xl font-bold mb-4 text-blue-400">Institutional Lineage</h2>
                <div className="space-y-3">
                    <div className="flex justify-between border-b border-gray-700 pb-2">
                        <span className="text-gray-400">Feature Version</span>
                        <span className="font-mono text-sm text-blue-300">{dataset.lineage.feature_version}</span>
                    </div>
                    <div className="flex justify-between border-b border-gray-700 pb-2">
                        <span className="text-gray-400">Label Version</span>
                        <span className="font-mono text-sm text-blue-300">{dataset.lineage.label_version}</span>
                    </div>
                    <div className="flex justify-between pb-2">
                        <span className="text-gray-400">Trade Engine Version</span>
                        <span className="font-mono text-sm text-blue-300">{dataset.lineage.trade_engine_version}</span>
                    </div>
                </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
                <h2 className="text-2xl font-bold mb-4 text-purple-400">Trade Outcome Analytics</h2>
                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-gray-400 text-sm mb-1">Target Hits</p>
                        <p className="text-xl font-bold text-green-400">{dataset.statistics.Target_Hit_Pct}%</p>
                    </div>
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-gray-400 text-sm mb-1">Stop Loss Hits</p>
                        <p className="text-xl font-bold text-red-400">{dataset.statistics.Stop_Loss_Pct}%</p>
                    </div>
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-gray-400 text-sm mb-1">Timeouts</p>
                        <p className="text-xl font-bold text-yellow-400">{dataset.statistics.Timeout_Pct}%</p>
                    </div>
                </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
                <h2 className="text-2xl font-bold mb-4 text-orange-400">Label Balances</h2>
                <div className="space-y-4">
                    <div>
                        <div className="flex justify-between mb-1">
                            <span className="text-gray-300 text-sm">Baseline (Forward Return)</span>
                            <span className="text-gray-400 text-sm">{dataset.statistics.Label_Baseline_Positives} Positives</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                            <div className="bg-gray-500 h-2 rounded-full" style={{ width: `${(dataset.statistics.Label_Baseline_Positives / dataset.statistics.Total_Rows) * 100}%` }}></div>
                        </div>
                    </div>
                    <div>
                        <div className="flex justify-between mb-1">
                            <span className="text-gray-300 text-sm">Trade Success</span>
                            <span className="text-gray-400 text-sm">{dataset.statistics.Label_TradeSuccess_Positives} Positives</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                            <div className="bg-green-500 h-2 rounded-full" style={{ width: `${(dataset.statistics.Label_TradeSuccess_Positives / dataset.statistics.Total_Rows) * 100}%` }}></div>
                        </div>
                    </div>
                    <div>
                        <div className="flex justify-between mb-1">
                            <span className="text-gray-300 text-sm">Trade Quality Ranking (Top 5%)</span>
                            <span className="text-gray-400 text-sm">{dataset.statistics.Label_Ranking_Positives} Positives</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${(dataset.statistics.Label_Ranking_Positives / dataset.statistics.Total_Rows) * 100}%` }}></div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
      )}
    </div>
  );
}
