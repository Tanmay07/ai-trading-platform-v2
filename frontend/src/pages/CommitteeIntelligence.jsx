import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Gavel, CheckCircle, XCircle, AlertTriangle, Scale, History, User, FileText } from 'lucide-react';

export default function CommitteeIntelligence() {
    const [evaluations, setEvaluations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const conveneCommittee = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('http://localhost:8000/committee/mock');
            if (!res.ok) throw new Error("Failed to convene committee");
            const data = await res.json();
            setEvaluations(data.evaluations);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getDecisionColor = (decision) => {
        switch(decision) {
            case 'BUY': return 'text-emerald-400 bg-emerald-900/30 border-emerald-500';
            case 'REVIEW': return 'text-yellow-400 bg-yellow-900/30 border-yellow-500';
            case 'REJECT': return 'text-red-400 bg-red-900/30 border-red-500';
            default: return 'text-gray-400 bg-gray-900 border-gray-700';
        }
    };
    
    const getVoteIcon = (vote) => {
        switch(vote) {
            case 'APPROVE': return <CheckCircle size={16} className="text-emerald-400" />;
            case 'REVIEW': return <AlertTriangle size={16} className="text-yellow-400" />;
            case 'REJECT': return <XCircle size={16} className="text-red-400" />;
            default: return null;
        }
    };

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-gray-100 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                
                {/* Header */}
                <div className="flex justify-between items-end border-b border-gray-700 pb-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                            <Gavel className="text-indigo-500" size={36} /> Investment Committee
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg">Plugin-Based Decision Orchestration (Phase F3)</p>
                    </div>
                    <button 
                        onClick={conveneCommittee}
                        disabled={loading}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg shadow-indigo-900/50 transition-all flex items-center gap-2"
                    >
                        <Scale size={18} />
                        {loading ? 'Evaluating...' : 'Convene Committee'}
                    </button>
                </div>

                {error && (
                    <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg flex items-center gap-3">
                        <AlertTriangle /> {error}
                    </div>
                )}

                {evaluations.length > 0 && (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        {/* Summary Analytics */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Decisions Evaluated</p>
                                <p className="text-4xl font-black text-white mt-2">{evaluations.length}</p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Approval Rate</p>
                                <p className="text-4xl font-black text-emerald-400 mt-2">
                                    {Math.round((evaluations.filter(e => e.final_decision === 'BUY').length / evaluations.length) * 100)}%
                                </p>
                            </div>
                            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
                                <p className="text-gray-400 text-sm font-medium">Average Committee Score</p>
                                <p className="text-4xl font-black text-indigo-400 mt-2">
                                    {(evaluations.reduce((acc, e) => acc + e.committee_score, 0) / evaluations.length).toFixed(1)}
                                </p>
                            </div>
                        </div>

                        {/* Decisions Grid */}
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold text-white flex items-center gap-2"><History size={24}/> Decision Audit Trail</h2>
                            
                            {evaluations.map((evalData, idx) => (
                                <div key={idx} className="bg-gray-800 rounded-xl border border-gray-700 shadow-md overflow-hidden">
                                    {/* Header */}
                                    <div className="p-5 border-b border-gray-700 bg-gray-900/50 flex justify-between items-center">
                                        <div className="flex items-center gap-4">
                                            <span className="text-2xl font-black text-white">{evalData.symbol}</span>
                                            <span className={`px-3 py-1 rounded text-sm font-bold border tracking-widest ${getDecisionColor(evalData.final_decision)}`}>
                                                {evalData.final_decision}
                                            </span>
                                        </div>
                                        <div className="text-right flex items-center gap-6">
                                            <div>
                                                <div className="text-gray-500 text-xs uppercase tracking-wider mb-1">Committee Score</div>
                                                <div className="text-2xl font-black text-indigo-400">{evalData.committee_score.toFixed(1)}/100</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-500 text-xs uppercase tracking-wider mb-1"><FileText size={12} className="inline mr-1"/> Audit ID</div>
                                                <div className="text-sm font-mono text-gray-400">{evalData.decision_id.split('-')[0]}...</div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Voting Breakdown */}
                                    <div className="p-5">
                                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Plugin Member Votes</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            {evalData.votes.map((vote, vidx) => (
                                                <div key={vidx} className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                                                    <div className="flex justify-between items-center mb-2">
                                                        <span className="font-bold text-gray-200 flex items-center gap-2"><User size={14} className="text-indigo-400"/> {vote.member_name}</span>
                                                        <span className="flex items-center gap-1 font-mono text-sm">
                                                            {getVoteIcon(vote.vote)} {vote.vote}
                                                        </span>
                                                    </div>
                                                    <div className="text-xs text-gray-500">
                                                        Confidence: {vote.confidence.toFixed(1)}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                        
                                        <div className="mt-6 p-4 bg-gray-900 rounded-lg border border-gray-800">
                                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Decision Explanation</h3>
                                            <pre className="text-gray-300 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                                                {evalData.explanation}
                                            </pre>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                    </motion.div>
                )}
            </div>
        </div>
    );
}
