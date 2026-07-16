import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function FactorIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/factors/')
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch factor intelligence");
        return res.json();
      })
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-8 text-white min-h-screen bg-gray-900 font-sans">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-600 mb-2">Institutional Factor Engine</h1>
        <p className="text-gray-400">Feature Store V2 Validation & Surrogate Feature Selection</p>
      </motion.div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
      ) : error ? (
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 text-center text-gray-400">
            {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl col-span-1 xl:col-span-2">
                <h2 className="text-2xl font-bold mb-4 text-blue-400">Factor Intelligence Overview</h2>
                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-sm text-gray-400">Total Factors</p>
                        <p className="text-2xl font-bold">{data.Total_Factors}</p>
                    </div>
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-sm text-gray-400">Strongest Factor (SHAP)</p>
                        <p className="text-xl font-bold text-green-400">{data.Strongest_Factor.replace(/_/g, ' ')}</p>
                    </div>
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-sm text-gray-400">Weakest Factor</p>
                        <p className="text-xl font-bold text-red-400">{data.Weakest_Factor.replace(/_/g, ' ')}</p>
                    </div>
                </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl col-span-1 xl:col-span-2">
                <h2 className="text-2xl font-bold mb-4 text-indigo-400">Factor Importance Rankings (Surrogate RF)</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {data.Factor_Rankings.map((factor, idx) => (
                        <div key={idx} className="bg-gray-750 p-4 rounded border border-gray-600 flex justify-between items-center">
                            <div>
                                <p className="font-bold">{factor.Factor.replace(/_/g, ' ')}</p>
                                <p className="text-xs text-gray-400">Average Score: {factor.Average_Score.toFixed(1)}</p>
                            </div>
                            <div className="text-right">
                                <p className="text-sm font-bold text-indigo-300">SHAP: {factor.SHAP_Proxy_Importance.toFixed(4)}</p>
                                <p className="text-xs text-gray-400">MI: {factor.Mutual_Information.toFixed(4)}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            
        </div>
      )}
    </div>
  );
}
