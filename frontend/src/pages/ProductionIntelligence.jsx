import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function ProductionIntelligence() {
  const [model, setModel] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  
  // Demonstration Prediction State
  const [demoTicker, setDemoTicker] = useState('RELIANCE.NS');
  const [prediction, setPrediction] = useState(null);
  const [demoLoading, setDemoLoading] = useState(false);

  const fetchProductionState = () => {
    fetch('http://localhost:8000/api/production/model')
      .then(res => res.json())
      .then(d => setModel(d.status === 'no_active_model' ? null : d));

    fetch('http://localhost:8000/api/production/history')
      .then(res => res.json())
      .then(d => {
          setHistory(d.history || []);
          setLoading(false);
      });
  };

  useEffect(() => {
    fetchProductionState();
  }, []);

  const triggerTraining = () => {
    setTraining(true);
    fetch('http://localhost:8000/api/production/retrain', { method: 'POST' })
      .then(() => {
          // Poll every 3 seconds for demo purposes
          const interval = setInterval(() => {
              fetch('http://localhost:8000/api/production/model')
                  .then(res => res.json())
                  .then(d => {
                      if (d.status !== 'no_active_model') {
                          fetchProductionState();
                          setTraining(false);
                          clearInterval(interval);
                      }
                  })
          }, 3000);
      });
  };

  const rollback = () => {
    fetch('http://localhost:8000/api/production/rollback', { method: 'POST' })
        .then(() => fetchProductionState());
  };

  const fetchPrediction = () => {
      setDemoLoading(true);
      fetch(`http://localhost:8000/api/production/predict/${demoTicker}`)
          .then(res => {
              if (!res.ok) throw new Error("Could not fetch prediction. Ensure ticker exists in Dataset V3.");
              return res.json();
          })
          .then(d => {
              setPrediction(d);
              setDemoLoading(false);
          })
          .catch(e => {
              alert(e.message);
              setDemoLoading(false);
          });
  };

  return (
    <div className="p-8 text-white min-h-screen bg-gray-900 font-sans">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex justify-between items-center mb-10">
        <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-600 mb-2">Production Intelligence</h1>
            <p className="text-gray-400">Champion Model Serving & Prediction Explainability</p>
        </div>
        <button 
            onClick={triggerTraining}
            disabled={training}
            className={`px-6 py-3 rounded-lg font-bold ${training ? 'bg-gray-700 text-gray-500' : 'bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white shadow-lg'}`}
        >
            {training ? 'Training Production Model...' : 'Train & Deploy Champion'}
        </button>
      </motion.div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
        </div>
      ) : !model ? (
        <div className="bg-gray-800 p-12 rounded-xl border border-gray-700 text-center flex flex-col items-center">
            <h2 className="text-2xl font-bold mb-4">No Production Model Deployed</h2>
            <p className="text-gray-400 mb-8 max-w-lg">Click 'Train & Deploy Champion' to pull the winning configuration from the Model Arena and build the final production artifact.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            
            {/* Active Model Overview */}
            <div className="bg-gray-800 p-6 rounded-xl border border-emerald-900 shadow-xl col-span-1 xl:col-span-2">
                <div className="flex justify-between items-start mb-6">
                    <div>
                        <h2 className="text-2xl font-bold text-emerald-400 flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
                            Active Production Model
                        </h2>
                        <p className="text-gray-400">Version: {model.version} | Dataset: {model.dataset_version}</p>
                    </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-sm text-gray-400">ROC-AUC</p>
                        <p className="text-xl font-bold">{(model.metrics.cv_roc_auc || 0).toFixed(4)}</p>
                    </div>
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-sm text-gray-400">Profit Factor</p>
                        <p className="text-xl font-bold">{(model.metrics.Profit_Factor || 0).toFixed(2)}</p>
                    </div>
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-sm text-gray-400">Precision@20</p>
                        <p className="text-xl font-bold">{(model.metrics["Precision@20"] || 0).toFixed(2)}</p>
                    </div>
                    <div className="bg-gray-750 p-4 rounded border border-gray-600">
                        <p className="text-sm text-gray-400">Calibration</p>
                        <p className="text-xl font-bold capitalize">{model.calibration}</p>
                    </div>
                </div>
            </div>
            
            {/* Regression Research (E4.1) */}
            <div className="bg-gray-800 p-6 rounded-xl border border-blue-900 shadow-xl col-span-1 xl:col-span-3">
                <div className="flex items-center gap-3 mb-4">
                    <h2 className="text-2xl font-bold text-blue-400">Research Regressor</h2>
                    <span className="px-3 py-1 bg-blue-900/50 text-blue-300 text-xs font-bold rounded-full border border-blue-700">EXPERIMENTAL</span>
                </div>
                <p className="text-sm text-gray-400 mb-6">Parallel LightGBM model trained to predict Trade_Quality_Score directly. This model is evaluated alongside production but does not gate recommendations yet.</p>
                
                {model.regression_metrics ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                            <p className="text-sm text-gray-400">RMSE</p>
                            <p className="text-2xl font-bold text-white">{model.regression_metrics.rmse.toFixed(2)}</p>
                        </div>
                        <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                            <p className="text-sm text-gray-400">R² Score</p>
                            <p className="text-2xl font-bold text-white">{model.regression_metrics.r2.toFixed(3)}</p>
                        </div>
                        <div className="bg-gray-900 p-4 rounded-lg border border-gray-700 col-span-2">
                            <p className="text-sm text-gray-400">Recommendation Status</p>
                            <p className="text-lg font-bold text-yellow-400 mt-1">Research Data Only</p>
                            <p className="text-xs text-gray-500 mt-1">Prediction outputs are merged seamlessly via PredictionService.</p>
                        </div>
                    </div>
                ) : (
                    <p className="text-gray-500 italic">No regression metrics available for this version.</p>
                )}
            </div>

            {/* Model History & Rollback */}
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl col-span-1">
                <h2 className="text-xl font-bold mb-4 text-gray-300">Model History</h2>
                <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2">
                    {history.map((h, i) => (
                        <div key={i} className={`p-3 rounded border ${h.version === model.version ? 'bg-emerald-900/20 border-emerald-700' : 'bg-gray-750 border-gray-600'}`}>
                            <div className="flex justify-between items-center">
                                <p className="font-bold">{h.version} {h.version === model.version && '(Active)'}</p>
                            </div>
                            <p className="text-xs text-gray-400 mt-1">Feature Mode: {h.feature_mode}</p>
                        </div>
                    ))}
                </div>
                {history.length > 1 && (
                    <button onClick={rollback} className="mt-4 w-full py-2 bg-gray-700 hover:bg-gray-600 text-white rounded font-bold transition">
                        Rollback to Previous Version
                    </button>
                )}
            </div>
            
            {/* Live Prediction & SHAP Explainability */}
            <div className="bg-gray-800 p-6 rounded-xl border border-indigo-900 shadow-xl col-span-1 xl:col-span-3">
                <h2 className="text-2xl font-bold mb-4 text-indigo-400">Live Prediction Service (SHAP Explainability)</h2>
                <p className="text-sm text-gray-400 mb-6">Test the PredictionService abstraction which returns standardized outputs and SHAP reasoning regardless of the underlying ML algorithm.</p>
                
                <div className="flex gap-4 mb-8">
                    <input 
                        type="text" 
                        value={demoTicker} 
                        onChange={(e) => setDemoTicker(e.target.value)}
                        className="bg-gray-900 border border-gray-700 rounded px-4 py-2 w-64 text-white focus:outline-none focus:border-indigo-500"
                        placeholder="Enter Ticker (e.g., RELIANCE.NS)"
                    />
                    <button 
                        onClick={fetchPrediction}
                        disabled={demoLoading}
                        className="bg-indigo-600 hover:bg-indigo-500 px-6 py-2 rounded font-bold transition"
                    >
                        {demoLoading ? 'Predicting...' : 'Generate Prediction'}
                    </button>
                </div>

                {prediction && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="bg-gray-900 p-6 rounded-xl border border-gray-700">
                            <h3 className="text-xl font-bold mb-4 border-b border-gray-700 pb-2">Prediction Engine Output</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Trade Quality Prediction</span>
                                    <span className="font-bold text-lg text-emerald-400">{prediction.trade_quality_prediction.toFixed(1)} / 100</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Model Confidence</span>
                                    <span className="font-bold text-lg text-blue-400">{(prediction.confidence * 100).toFixed(1)}%</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Expected Hold Time</span>
                                    <span className="font-bold text-lg">{prediction.expected_holding_days} Days</span>
                                </div>
                                <div className="flex justify-between border-t border-gray-800 pt-4 mt-4">
                                    <span className="text-gray-400">Engine Version</span>
                                    <span className="font-mono text-xs text-gray-500">{prediction.model_version} ({prediction.feature_mode})</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-900 p-6 rounded-xl border border-gray-700">
                            <h3 className="text-xl font-bold mb-4 border-b border-gray-700 pb-2 flex items-center gap-2">
                                SHAP Reasoning
                                <span className="text-xs bg-indigo-900/50 text-indigo-300 px-2 py-1 rounded">Why this recommendation?</span>
                            </h3>
                            <ul className="space-y-3">
                                {prediction.explanations.top_factors.map((factor, idx) => (
                                    <li key={idx} className="flex items-center gap-3 p-2 bg-gray-800 rounded">
                                        <div className="w-6 h-6 rounded-full bg-emerald-900/50 text-emerald-400 flex items-center justify-center font-bold text-sm">
                                            {idx + 1}
                                        </div>
                                        <span className="font-mono text-sm text-gray-300">{factor.replace(/_/g, ' ')}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </motion.div>
                )}
            </div>

        </div>
      )}
    </div>
  );
}
