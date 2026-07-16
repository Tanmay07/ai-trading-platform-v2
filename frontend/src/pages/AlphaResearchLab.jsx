import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function AlphaResearchLab() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchReport();
  }, []);

  const fetchReport = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/research/overview');
      if (!res.ok) {
        if (res.status === 404) {
           setError("No Alpha Research Report found. Please trigger a research run.");
           setLoading(false);
           return;
        }
        throw new Error("Failed to fetch report");
      }
      
      const featuresRes = await fetch('http://localhost:8000/api/research/features');
      const featuresData = await featuresRes.json();
      
      const alphaRes = await fetch('http://localhost:8000/api/research/alpha');
      const alphaData = await alphaRes.json();
      
      const recRes = await fetch('http://localhost:8000/api/research/recommendations');
      const recData = await recRes.json();
      
      setReport({
          overview: await res.json(),
          features: featuresData.Feature_Intelligence,
          correlations: featuresData.Feature_Correlation,
          discoveries: alphaData,
          recommendations: recData
      });
      setLoading(false);
    } catch (e) {
      setError(e.message);
      setLoading(false);
    }
  };

  const triggerRun = async () => {
    setRunning(true);
    try {
      const res = await fetch('http://localhost:8000/api/research/run', { method: 'POST' });
      if (!res.ok) throw new Error("Failed to start research");
      alert("Alpha Research Engine Started! This may take a few minutes. Check backend logs.");
    } catch (e) {
      alert(e.message);
    }
    setRunning(false);
  };

  return (
    <div className="p-8 text-white min-h-screen bg-gray-900 font-sans">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex justify-between items-center mb-10">
        <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-600 mb-2">Alpha Research Lab</h1>
            <p className="text-gray-400">Institutional Quantitative Discovery & Roadmap Generation</p>
        </div>
        <button 
          onClick={triggerRun}
          disabled={running}
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-6 rounded shadow-lg transition-colors"
        >
          {running ? "Running..." : "Trigger Research Run"}
        </button>
      </motion.div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
      ) : error ? (
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 text-center">
            <p className="text-gray-400 mb-4">{error}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            
            {/* Discoveries */}
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl col-span-1 xl:col-span-2">
                <h2 className="text-2xl font-bold mb-4 text-pink-400">Top Alpha Discoveries</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {report.discoveries.map((disc, idx) => (
                        <div key={idx} className="bg-gray-750 p-4 rounded border border-gray-600 shadow-inner">
                            <span className="text-xs font-bold text-pink-500 mb-2 block tracking-widest uppercase">Discovery {idx + 1}</span>
                            <p className="text-sm font-medium mb-2">{disc.Insight}</p>
                            <p className="text-xs text-gray-400 break-words mb-2">{disc.Evidence}</p>
                            <span className={`text-xs px-2 py-1 rounded font-bold ${disc.Confidence === 'High' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}`}>
                                {disc.Confidence} Confidence
                            </span>
                        </div>
                    ))}
                    {report.discoveries.length === 0 && (
                        <div className="col-span-3 text-center py-8 text-gray-500">No statistically significant discoveries found.</div>
                    )}
                </div>
            </div>

            {/* Feature Expansion Roadmap */}
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
                <h2 className="text-2xl font-bold mb-4 text-green-400">Feature Expansion Roadmap (E3.6)</h2>
                <div className="space-y-4">
                    {report.recommendations.Feature_Expansion_Ideas?.map((idea, idx) => (
                        <div key={idx} className="flex flex-col bg-gray-750 p-3 rounded border border-gray-600">
                            <div className="flex justify-between items-center mb-1">
                                <span className="font-bold text-green-300">Priority {idea.Priority}: {idea.Idea}</span>
                                <span className="text-xs bg-gray-700 px-2 py-1 rounded">{idea.Expected_Impact} Impact</span>
                            </div>
                            <span className="text-xs text-gray-400">{idea.Rationale}</span>
                        </div>
                    ))}
                </div>
                
                <h3 className="font-bold text-red-400 mt-6 mb-2">Features to Deprecate</h3>
                <div className="flex flex-wrap gap-2">
                    {report.recommendations.Features_To_Remove?.slice(0, 10).map((f, idx) => (
                        <span key={idx} className="bg-red-900 text-red-300 text-xs px-2 py-1 rounded">{f}</span>
                    ))}
                    {report.recommendations.Features_To_Remove?.length === 0 && <span className="text-gray-500 text-sm">None</span>}
                </div>
            </div>

            {/* Feature Importance */}
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
                <h2 className="text-2xl font-bold mb-4 text-indigo-400">Surrogate SHAP Importance</h2>
                <div className="space-y-3 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
                    {report.features.Feature_Rankings?.slice(0, 15).map((feat, idx) => (
                        <div key={idx}>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-300">{feat.Feature}</span>
                                <span className="text-indigo-300">{feat.SHAP_Proxy_Importance.toFixed(4)}</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-1.5">
                                <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${(feat.SHAP_Proxy_Importance / report.features.Feature_Rankings[0].SHAP_Proxy_Importance) * 100}%` }}></div>
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
