import React, { useState, useEffect } from 'react';
import { ShieldAlert, TrendingUp, TrendingDown, Target, AlertTriangle, Eye, CheckCircle } from 'lucide-react';

const PortfolioRecommendationWorkspace = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedRec, setSelectedRec] = useState(null);

  useEffect(() => {
    // In a real scenario, this would fetch from /api/v2/decision/recommendations/1
    // For now we use some mock states reflecting Phase P3 capabilities
    setRecommendations([
      { symbol: "HDFCBANK", decision: "Strong Buy", confidence: 92.5, current_price: 1650, target_price_1: 1850, stop_loss: 1550, tech_score: 85, val_score: 95, risk_score: 80, weight: 8.5 },
      { symbol: "TCS", decision: "Hold", confidence: 65.0, current_price: 3800, target_price_1: 4100, stop_loss: 3600, tech_score: 60, val_score: 55, risk_score: 90, weight: 12.0 },
      { symbol: "RELIANCE", decision: "Trim Position", confidence: 45.0, current_price: 2950, target_price_1: 3100, stop_loss: 2800, tech_score: 40, val_score: 30, risk_score: 60, weight: 22.0 }
    ]);
  }, []);

  return (
    <div className="h-full flex flex-col p-6 animate-fade-in bg-[#0B0E14] text-white overflow-y-auto">
      
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Investment Decision Engine</h1>
        <p className="text-gray-400">Institutional-grade recommendations powered by Technical, Valuation, Context, and Risk intelligence.</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 p-4 rounded border border-gray-700 shadow flex flex-col">
          <span className="text-gray-400 text-sm">Strong Buy Candidates</span>
          <span className="text-3xl font-semibold text-green-400">4</span>
        </div>
        <div className="bg-gray-800 p-4 rounded border border-gray-700 shadow flex flex-col">
          <span className="text-gray-400 text-sm">Positions to Trim/Sell</span>
          <span className="text-3xl font-semibold text-red-400">2</span>
        </div>
        <div className="bg-gray-800 p-4 rounded border border-gray-700 shadow flex flex-col">
          <span className="text-gray-400 text-sm">High Risk Exposure</span>
          <span className="text-3xl font-semibold text-orange-400">1</span>
        </div>
        <div className="bg-gray-800 p-4 rounded border border-gray-700 shadow flex flex-col">
          <span className="text-gray-400 text-sm">Pending Alerts</span>
          <span className="text-3xl font-semibold text-blue-400">3</span>
        </div>
      </div>

      <div className="flex gap-6 h-full min-h-[500px]">
        {/* Holdings Grid */}
        <div className="w-2/3 bg-gray-900 border border-gray-800 rounded p-4 overflow-y-auto">
          <h2 className="text-xl font-semibold mb-4">Portfolio Recommendations</h2>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-700 text-gray-400 text-sm">
                <th className="p-2">Symbol</th>
                <th className="p-2">Weight</th>
                <th className="p-2">Decision</th>
                <th className="p-2">Confidence</th>
                <th className="p-2">Target</th>
                <th className="p-2">Stop Loss</th>
                <th className="p-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {recommendations.map(r => (
                <tr key={r.symbol} className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors">
                  <td className="p-2 font-medium">{r.symbol}</td>
                  <td className="p-2">{r.weight}%</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      r.decision.includes('Buy') ? 'bg-green-900 text-green-400' :
                      r.decision.includes('Sell') || r.decision.includes('Trim') ? 'bg-red-900 text-red-400' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {r.decision}
                    </span>
                  </td>
                  <td className="p-2">{r.confidence}%</td>
                  <td className="p-2 text-green-400">₹{r.target_price_1}</td>
                  <td className="p-2 text-red-400">₹{r.stop_loss}</td>
                  <td className="p-2">
                    <button 
                      onClick={() => setSelectedRec(r)}
                      className="text-blue-400 hover:text-blue-300 text-sm font-semibold flex items-center gap-1"
                    >
                      <Eye size={14} /> Analyze
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Details Panel */}
        <div className="w-1/3 bg-gray-900 border border-gray-800 rounded p-4 flex flex-col">
          <h2 className="text-xl font-semibold mb-4">Intelligence Panel</h2>
          
          {selectedRec ? (
            <div className="flex flex-col gap-4">
              <div className="flex justify-between items-center pb-2 border-b border-gray-800">
                <span className="text-2xl font-bold">{selectedRec.symbol}</span>
                <span className="text-sm px-2 py-1 bg-gray-700 rounded text-gray-300">{selectedRec.decision}</span>
              </div>
              
              <div>
                <h3 className="text-sm text-gray-400 font-semibold uppercase mb-1">Sub-Scores</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex justify-between bg-gray-800 p-2 rounded"><span>Technical</span> <span className="text-blue-400">{selectedRec.tech_score}/100</span></div>
                  <div className="flex justify-between bg-gray-800 p-2 rounded"><span>Valuation</span> <span className="text-blue-400">{selectedRec.val_score}/100</span></div>
                  <div className="flex justify-between bg-gray-800 p-2 rounded"><span>Risk Profile</span> <span className="text-blue-400">{selectedRec.risk_score}/100</span></div>
                  <div className="flex justify-between bg-gray-800 p-2 rounded"><span>Context</span> <span className="text-blue-400">100/100</span></div>
                </div>
              </div>

              <div>
                <h3 className="text-sm text-gray-400 font-semibold uppercase mb-1">Explanation</h3>
                <div className="bg-gray-800 p-3 rounded text-sm text-gray-300 leading-relaxed border border-gray-700">
                  <p className="mb-2"><strong className="text-white">Why?</strong> Strong bullish momentum. Attractive valuation with PE at 15.5x and EPS growth of 18%.</p>
                  <p className="mb-2"><strong className="text-white">Why Now?</strong> Stock is currently in oversold territory, presenting a tactical entry point.</p>
                  <p><strong className="text-white">Invalidation:</strong> A close below Stop Loss (₹{selectedRec.stop_loss}) would invalidate this thesis.</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500 flex-col gap-2">
              <ShieldAlert size={48} className="opacity-20" />
              <p>Select a holding to view intelligence breakdown</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PortfolioRecommendationWorkspace;
