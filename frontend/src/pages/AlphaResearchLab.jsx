import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FlaskConical, Beaker, Zap, Activity, ArrowUpCircle, CheckCircle, Clock } from 'lucide-react';

export default function AlphaResearchLab() {
    const [signals, setSignals] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchSignals = async () => {
        try {
            const res = await fetch('http://localhost:8000/research/features');
            const data = await res.json();
            setSignals(data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchSignals();
    }, []);

    const runExperiment = async () => {
        setLoading(true);
        try {
            await fetch('http://localhost:8000/research/run-experiment', { method: 'POST' });
            setTimeout(fetchSignals, 1000); // Give the backend a second to write the JSONs
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score) => {
        if (!score) return 'text-gray-500';
        if (score >= 75) return 'text-emerald-400';
        if (score >= 50) return 'text-yellow-400';
        return 'text-red-400';
    };

    const getStatusBadge = (status) => {
        if (status === 'Candidate') return <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded border border-purple-500/50 flex items-center gap-1"><ArrowUpCircle size={12}/> Candidate</span>;
        if (status === 'Production') return <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded border border-emerald-500/50 flex items-center gap-1"><CheckCircle size={12}/> Production</span>;
        return <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded border border-gray-500/50 flex items-center gap-1"><Clock size={12}/> Experimental</span>;
    };

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-gray-100 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                
                {/* Header */}
                <div className="flex justify-between items-end border-b border-gray-700 pb-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                            <FlaskConical className="text-purple-500" size={36} /> Alpha Research Lab
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg">Institutional Signal Discovery & Marketplace (Phase G1)</p>
                    </div>
                    <button 
                        onClick={runExperiment}
                        disabled={loading}
                        className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-purple-900/50 transition-all flex items-center gap-2"
                    >
                        {loading ? <Activity className="animate-spin" size={18} /> : <Beaker size={18} />}
                        {loading ? 'Running Discovery...' : 'Run New Experiment'}
                    </button>
                </div>

                {/* Marketplace Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    
                    {/* Catalog List */}
                    <div className="lg:col-span-3 bg-gray-800 rounded-xl border border-gray-700 shadow-md overflow-hidden">
                        <div className="p-4 border-b border-gray-700 bg-gray-900/50 flex justify-between items-center">
                            <h2 className="text-lg font-bold text-white flex items-center gap-2"><Zap size={18}/> Alpha Signal Marketplace</h2>
                            <span className="text-sm text-gray-400">{signals.length} Signals Registered</span>
                        </div>
                        
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm text-gray-300">
                                <thead className="text-xs text-gray-400 uppercase bg-gray-900/50">
                                    <tr>
                                        <th className="px-6 py-3">Signal Name</th>
                                        <th className="px-6 py-3">Source</th>
                                        <th className="px-6 py-3">Alpha Score</th>
                                        <th className="px-6 py-3">IC</th>
                                        <th className="px-6 py-3">Profit Factor</th>
                                        <th className="px-6 py-3">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {signals.length === 0 && (
                                        <tr>
                                            <td colSpan="6" className="text-center py-8 text-gray-500">
                                                No signals in marketplace. Run an experiment to generate candidates.
                                            </td>
                                        </tr>
                                    )}
                                    {signals.map((sig, idx) => {
                                        const lastEval = sig.evaluations && sig.evaluations.length > 0 ? sig.evaluations[sig.evaluations.length - 1] : null;
                                        return (
                                            <motion.tr 
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                transition={{ delay: idx * 0.1 }}
                                                key={sig.signal_id} 
                                                className="border-b border-gray-700 hover:bg-gray-700/50 transition-colors"
                                            >
                                                <td className="px-6 py-4 font-bold text-white">{sig.name}</td>
                                                <td className="px-6 py-4">
                                                    <span className="bg-gray-900 px-2 py-1 rounded text-xs border border-gray-700">{sig.source}</span>
                                                </td>
                                                <td className={`px-6 py-4 font-black ${getScoreColor(sig.alpha_score)}`}>
                                                    {sig.alpha_score ? sig.alpha_score : '-'}
                                                </td>
                                                <td className="px-6 py-4 font-mono">
                                                    {lastEval ? lastEval.statistical.ic.toFixed(3) : '-'}
                                                </td>
                                                <td className="px-6 py-4 font-mono">
                                                    {lastEval ? lastEval.trading.profit_factor.toFixed(2) : '-'}
                                                </td>
                                                <td className="px-6 py-4">
                                                    {getStatusBadge(sig.lifecycle_state)}
                                                </td>
                                            </motion.tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    );
}
