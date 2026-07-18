import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Network, Activity, PlayCircle, Clock, CheckCircle2, AlertCircle, RotateCw } from 'lucide-react';

export default function OperationsCenter() {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchStatus = async () => {
        try {
            const res = await fetch('http://localhost:8000/operations/status');
            const data = await res.json();
            setStatus(data);
        } catch (err) {
            console.error("Failed to fetch status", err);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 2000); // Poll every 2s for real-time updates
        return () => clearInterval(interval);
    }, []);

    const triggerWorkflow = async () => {
        setLoading(true);
        try {
            await fetch('http://localhost:8000/operations/run', { method: 'POST' });
            fetchStatus();
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getStageColor = (stageStatus) => {
        if (stageStatus === 'COMPLETED') return 'text-emerald-400 border-emerald-500 bg-emerald-900/20';
        if (stageStatus === 'RUNNING') return 'text-blue-400 border-blue-500 bg-blue-900/20 animate-pulse';
        if (stageStatus === 'FAILED') return 'text-red-400 border-red-500 bg-red-900/20';
        return 'text-gray-500 border-gray-700 bg-gray-800'; // PENDING
    };

    const getStageIcon = (stageStatus) => {
        if (stageStatus === 'COMPLETED') return <CheckCircle2 size={24} />;
        if (stageStatus === 'RUNNING') return <RotateCw className="animate-spin" size={24} />;
        if (stageStatus === 'FAILED') return <AlertCircle size={24} />;
        return <Clock size={24} />;
    };

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-gray-100 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                
                {/* Header */}
                <div className="flex justify-between items-end border-b border-gray-700 pb-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                            <Network className="text-cyan-500" size={36} /> Operations Center
                        </h1>
                        <p className="text-gray-400 mt-2 text-lg">Autonomous Orchestration Engine (Phase F6)</p>
                    </div>
                    <button 
                        onClick={triggerWorkflow}
                        disabled={loading || (status && status.status === 'RUNNING')}
                        className={`px-6 py-3 rounded-lg font-bold shadow-lg transition-all flex items-center gap-2 ${
                            (status && status.status === 'RUNNING') 
                                ? 'bg-gray-700 text-gray-400 cursor-not-allowed' 
                                : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-cyan-900/50'
                        }`}
                    >
                        {loading ? <RotateCw className="animate-spin" size={18} /> : <PlayCircle size={18} />}
                        {(status && status.status === 'RUNNING') ? 'Workflow Running...' : 'Trigger Daily Workflow'}
                    </button>
                </div>

                {status && (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        {/* Overall Status Banner */}
                        <div className={`p-6 rounded-xl border flex items-center gap-4 ${
                            status.status === 'COMPLETED' ? 'bg-emerald-900/30 border-emerald-500/50' :
                            status.status === 'RUNNING' ? 'bg-blue-900/30 border-blue-500/50' :
                            status.status === 'FAILED' ? 'bg-red-900/30 border-red-500/50' :
                            'bg-gray-800 border-gray-700'
                        }`}>
                            {status.status === 'RUNNING' && <RotateCw className="animate-spin text-blue-400" size={32} />}
                            {status.status === 'COMPLETED' && <CheckCircle2 className="text-emerald-400" size={32} />}
                            {status.status === 'IDLE' && <Clock className="text-gray-400" size={32} />}
                            <div>
                                <p className="text-sm text-gray-400 font-bold uppercase tracking-wider">System Status</p>
                                <p className="text-2xl font-black text-white">{status.status}</p>
                            </div>
                        </div>

                        {/* Workflow Timeline */}
                        <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-8">
                            <h2 className="text-xl font-bold text-white mb-8 flex items-center gap-2"><Activity size={20}/> Event-Driven Workflow Sequence</h2>
                            
                            <div className="flex flex-col md:flex-row justify-between items-center relative">
                                {/* Connecting Line Background */}
                                <div className="hidden md:block absolute top-1/2 left-0 w-full h-1 bg-gray-700 -translate-y-1/2 z-0"></div>
                                
                                {Object.entries(status.stages).map(([stageName, stageStatus], idx) => (
                                    <div key={idx} className="relative z-10 flex flex-col items-center mb-6 md:mb-0 bg-gray-800 px-2">
                                        <div className={`w-16 h-16 rounded-full border-4 flex items-center justify-center transition-colors duration-500 ${getStageColor(stageStatus)}`}>
                                            {getStageIcon(stageStatus)}
                                        </div>
                                        <p className={`mt-4 font-bold text-sm ${stageStatus === 'PENDING' ? 'text-gray-500' : 'text-white'}`}>
                                            {stageName.replace(/([A-Z])/g, ' $1').trim()}
                                        </p>
                                        <p className="text-xs text-gray-500 font-mono mt-1">{stageStatus}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Diagnostics Snippet */}
                        <div className="bg-gray-800 rounded-xl border border-gray-700 shadow-md p-6">
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Operations Telemetry</h3>
                            <div className="grid grid-cols-3 gap-4">
                                <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                                    <div className="text-gray-500 text-xs">Event Bus Engine</div>
                                    <div className="text-cyan-400 font-bold">ONLINE</div>
                                </div>
                                <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                                    <div className="text-gray-500 text-xs">Retry Manager</div>
                                    <div className="text-cyan-400 font-bold">ACTIVE (Max: 3)</div>
                                </div>
                                <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                                    <div className="text-gray-500 text-xs">Daily Schedule</div>
                                    <div className="text-gray-300 font-bold">08:20 IST</div>
                                </div>
                            </div>
                        </div>

                    </motion.div>
                )}
            </div>
        </div>
    );
}
