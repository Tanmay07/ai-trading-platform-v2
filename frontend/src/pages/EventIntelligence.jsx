import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Newspaper, Radio, Network, GitPullRequest, Zap, Target, Activity } from 'lucide-react';

export default function EventIntelligence() {
    const [eventsData, setEventsData] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchEvents = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/events/live');
            const data = await res.json();
            setEventsData(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEvents();
    }, []);

    const getSignificanceColor = (score) => {
        if (score >= 80) return 'text-red-400';
        if (score >= 60) return 'text-orange-400';
        return 'text-blue-400';
    };

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-gray-100 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                
                {/* Header */}
                <div className="flex justify-between items-end border-b border-gray-700 pb-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                            <Radio className="text-purple-500" size={36} /> Event Intelligence & Graph
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg">Causal Memory & Knowledge Graph Reasoning (Phase G4)</p>
                    </div>
                    <button 
                        onClick={fetchEvents}
                        disabled={loading}
                        className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-purple-900/50 transition-all flex items-center gap-2"
                    >
                        {loading ? <Activity className="animate-spin" size={18} /> : <Newspaper size={18} />}
                        {loading ? 'Ingesting...' : 'Ingest Live News'}
                    </button>
                </div>

                {eventsData && (
                    <div className="space-y-8">
                        
                        {/* Events Feed */}
                        <div className="grid grid-cols-1 gap-6">
                            {eventsData.events.map((event, idx) => (
                                <motion.div 
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: idx * 0.1 }}
                                    key={idx} 
                                    className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6"
                                >
                                    <div className="flex justify-between items-start mb-6">
                                        <div>
                                            <div className="flex items-center gap-3 mb-2">
                                                <span className="px-2 py-1 bg-gray-900 text-purple-400 text-xs font-bold rounded border border-purple-900/50 uppercase">
                                                    {event.event_type}
                                                </span>
                                                <span className="text-gray-500 text-sm">{new Date(event.timestamp).toLocaleString()}</span>
                                            </div>
                                            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                                                {event.company} <span className="text-gray-500 text-lg">({event.industry})</span>
                                            </h2>
                                            <div className="text-gray-400 mt-1">Impact Value: <span className="font-mono text-white">{event.value}</span></div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-xs text-gray-500 uppercase mb-1">Significance Score</div>
                                            <div className={`text-4xl font-black font-mono ${getSignificanceColor(event.significance_score)}`}>
                                                {event.significance_score}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        {/* Knowledge Graph Impact */}
                                        <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                                            <h3 className="text-sm font-bold text-gray-300 uppercase flex items-center gap-2 mb-3">
                                                <Network size={16} className="text-blue-400"/> Knowledge Graph Propagation
                                            </h3>
                                            <div className="space-y-3">
                                                <div className="flex items-center justify-between">
                                                    <span className="text-white font-bold">{event.estimated_impact.primary_impact.entity}</span>
                                                    <span className={`text-xs px-2 py-1 rounded ${event.estimated_impact.primary_impact.sentiment === 'Positive' ? 'bg-emerald-900/30 text-emerald-400' : 'bg-red-900/30 text-red-400'}`}>
                                                        Primary Impact ({event.estimated_impact.primary_impact.magnitude})
                                                    </span>
                                                </div>
                                                {event.estimated_impact.secondary_impact.map((sec, i) => (
                                                    <div key={i} className="flex items-center justify-between text-sm pl-4 border-l-2 border-gray-700 ml-2">
                                                        <div className="flex items-center gap-2">
                                                            <GitPullRequest size={14} className="text-gray-500"/>
                                                            <span className="text-gray-400">{sec.relation_path} &rarr;</span>
                                                            <span className="text-gray-200">{sec.entity}</span>
                                                        </div>
                                                        <span className={sec.sentiment === 'Positive' ? 'text-emerald-400' : sec.sentiment === 'Negative' ? 'text-red-400' : 'text-gray-500'}>
                                                            {sec.magnitude}
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Causal Memory */}
                                        <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                                            <h3 className="text-sm font-bold text-gray-300 uppercase flex items-center gap-2 mb-3">
                                                <Zap size={16} className="text-orange-400"/> Causal Learning Memory
                                            </h3>
                                            <p className="text-sm text-gray-300 italic mb-4">
                                                "{event.causal_expectations.causal_explanation}"
                                            </p>
                                            <div className="grid grid-cols-2 gap-4 mt-auto">
                                                <div className="bg-gray-800 p-3 rounded">
                                                    <div className="text-xs text-gray-500 mb-1">Expected 60d Return</div>
                                                    <div className={`text-xl font-bold font-mono ${event.causal_expectations.expected_return_60d >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                        {event.causal_expectations.expected_return_60d >= 0 ? '+' : ''}{event.causal_expectations.expected_return_60d}%
                                                    </div>
                                                </div>
                                                <div className="bg-gray-800 p-3 rounded">
                                                    <div className="text-xs text-gray-500 mb-1">Historical Win Rate</div>
                                                    <div className="text-xl font-bold font-mono text-white">
                                                        {(event.causal_expectations.historical_win_rate * 100).toFixed(0)}%
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        {/* Alpha Candidates Generated */}
                        {eventsData.new_alpha_candidates.length > 0 && (
                            <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                                    <Target size={20} className="text-emerald-400"/> Alpha Signals Generated
                                </h2>
                                <div className="space-y-3">
                                    {eventsData.new_alpha_candidates.map((alpha, idx) => (
                                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-900 rounded border border-gray-700">
                                            <div>
                                                <span className="font-mono text-emerald-400 font-bold">{alpha.factor_name}</span>
                                                <p className="text-sm text-gray-400 mt-1">{alpha.description}</p>
                                            </div>
                                            <span className="px-3 py-1 bg-gray-800 text-gray-300 text-xs rounded-full border border-gray-600">
                                                Sent to Alpha Registry
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                    </div>
                )}
            </div>
        </div>
    );
}
