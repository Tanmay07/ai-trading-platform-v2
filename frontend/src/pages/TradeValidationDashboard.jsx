import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function TradeValidationDashboard() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchReport() {
      try {
        const res = await fetch('http://localhost:8000/api/validation/report');
        if (!res.ok) throw new Error("Report not generated. Run validation_report.py first.");
        const data = await res.json();
        setReport(data);
        setLoading(false);
      } catch (e) {
        setError(e.message);
        setLoading(false);
      }
    }
    fetchReport();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-white min-h-screen bg-gray-900">
        <div className="bg-red-900/30 text-red-400 p-6 rounded-lg border border-red-700">
          <h2 className="text-xl font-bold mb-2">Validation Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const { Baseline_Label_Audit, Trade_Success_Audit, Quality_Distribution_Audit, Ranking_Correlation_Audit, Leakage_Audit, Edge_Case_Audit } = report;

  return (
    <div className="p-8 text-white min-h-screen bg-gray-900 font-sans">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-emerald-600 mb-2">Trade Validation Engine</h1>
        <p className="text-gray-400">Institutional validation report of the Trade Outcome and Label Engines.</p>
      </motion.div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        
        {/* Baseline Audit */}
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
          <h2 className="text-2xl font-bold mb-4 text-emerald-400">Validation 1: Baseline Label Fix</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="bg-gray-750 p-4 rounded border border-gray-600">
              <p className="text-gray-400 mb-1">Total Observations</p>
              <p className="text-2xl font-bold">{Baseline_Label_Audit.Total_Observations.toLocaleString()}</p>
            </div>
            <div className="bg-gray-750 p-4 rounded border border-gray-600">
              <p className="text-gray-400 mb-1">Corrected Positive %</p>
              <p className="text-2xl font-bold text-green-400">{Baseline_Label_Audit.Positive_Pct}%</p>
            </div>
            <div className="bg-gray-750 p-4 rounded border border-gray-600">
              <p className="text-gray-400 mb-1">Median Fwd Return</p>
              <p className="text-xl font-bold">{Baseline_Label_Audit.Median_Forward_Return}%</p>
            </div>
            <div className="bg-gray-750 p-4 rounded border border-gray-600">
              <p className="text-gray-400 mb-1">Min Fwd Return (Positives)</p>
              <p className="text-xl font-bold">{Baseline_Label_Audit.Min_Forward_Return}%</p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-4">Fix applied: Handled IEEE 754 floating point arithmetic precision error in comparison threshold.</p>
        </div>

        {/* Trade Success Audit */}
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
          <h2 className="text-2xl font-bold mb-4 text-emerald-400">Validation 2: Trade Success Audit</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="bg-gray-750 p-4 rounded border border-gray-600">
              <p className="text-gray-400 mb-1">True Target Hit Rate</p>
              <p className="text-2xl font-bold text-green-400">{Trade_Success_Audit.Target_Hit_Pct}%</p>
            </div>
            <div className="bg-gray-750 p-4 rounded border border-gray-600">
              <p className="text-gray-400 mb-1">True Stop Loss Rate</p>
              <p className="text-2xl font-bold text-red-400">{Trade_Success_Audit.Stop_Loss_Pct}%</p>
            </div>
            <div className="bg-gray-750 p-4 rounded border border-gray-600">
              <p className="text-gray-400 mb-1">Timeout Rate (No Hit)</p>
              <p className="text-2xl font-bold text-yellow-400">{Trade_Success_Audit.Timeout_Pct}%</p>
            </div>
            <div className="bg-gray-750 p-4 rounded border border-gray-600">
              <p className="text-gray-400 mb-1">Invalid (End of Dataset)</p>
              <p className="text-2xl font-bold text-gray-500">{Trade_Success_Audit.Invalid_Pct}%</p>
            </div>
          </div>
        </div>

        {/* Quality Score & Ranking */}
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
          <h2 className="text-2xl font-bold mb-4 text-blue-400">Validation 4, 8: Quality & Ranking</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
             <div>
                <p className="text-gray-400 text-sm">Mean Quality Score</p>
                <p className="text-xl font-bold">{Quality_Distribution_Audit.Mean}</p>
             </div>
             <div>
                <p className="text-gray-400 text-sm">Standard Dev</p>
                <p className="text-xl font-bold">{Quality_Distribution_Audit.Standard_Deviation}</p>
             </div>
             <div>
                <p className="text-gray-400 text-sm">Spearman Rank Corr</p>
                <p className="text-xl font-bold text-blue-300">{Ranking_Correlation_Audit.Spearman_Correlation}</p>
             </div>
             <div>
                <p className="text-gray-400 text-sm">Top-50 Quality Overlap</p>
                <p className="text-xl font-bold text-blue-300">{Ranking_Correlation_Audit.Top_50_Overlap_Pct}%</p>
             </div>
          </div>
          {Quality_Distribution_Audit.Flag_Collapsed && (
             <div className="p-3 bg-red-900/40 border border-red-500 rounded text-red-400 text-sm">
               Warning: Trade Quality Score distribution is extremely collapsed (StdDev &lt; 5.0).
             </div>
          )}
        </div>

        {/* Security & Edge Cases */}
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
          <h2 className="text-2xl font-bold mb-4 text-purple-400">Validation 9, 10: Leakage & Edge Cases</h2>
          <div className="mb-6">
            <h3 className="text-gray-400 mb-2 font-semibold">Data Leakage Audit</h3>
            {Leakage_Audit.Audit_Status === "PASSED" ? (
              <span className="px-3 py-1 bg-green-900 text-green-300 rounded font-bold text-sm">PASSED: No Leakage Detected</span>
            ) : (
              <span className="px-3 py-1 bg-red-900 text-red-300 rounded font-bold text-sm">FAILED: {Leakage_Audit.Leakage_Events_Found} Leaks</span>
            )}
          </div>
          <div>
            <h3 className="text-gray-400 mb-2 font-semibold">Edge Cases Found</h3>
            <div className="grid grid-cols-2 gap-y-2 text-sm">
              <span className="text-gray-500">Missing OHLCV:</span>
              <span className="font-bold">{Edge_Case_Audit.Missing_OHLCV_Values}</span>
              <span className="text-gray-500">Zero Volume Days:</span>
              <span className="font-bold">{Edge_Case_Audit.Zero_Volume_Days}</span>
              <span className="text-gray-500">Gap Down Stop-Outs:</span>
              <span className="font-bold">{Edge_Case_Audit.Gap_Down_Stop_Outs}</span>
              <span className="text-gray-500">Gap Up Target Hits:</span>
              <span className="font-bold">{Edge_Case_Audit.Gap_Up_Target_Hits}</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
