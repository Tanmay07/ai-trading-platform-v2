import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import PortfolioDashboard from '../components/portfolio/PortfolioDashboard';
import HoldingsTable from '../components/portfolio/HoldingsTable';
import AIInsightsPanel from '../components/portfolio/AIInsightsPanel';
import { RefreshCw } from 'lucide-react';

export default function AIPortfolioManager() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchPortfolio = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('http://localhost:8000/api/ai-portfolio/dashboard');
            if (!res.ok) throw new Error("Failed to load portfolio analysis");
            const result = await res.json();
            setData(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPortfolio();
    }, []);

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-gray-100 font-sans">
            <div className="max-w-[1600px] mx-auto space-y-6">
                
                {/* Header */}
                <div className="flex justify-between items-end border-b border-gray-700 pb-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tight">AI Portfolio Manager</h1>
                        <p className="text-gray-400 mt-2 text-lg">Institutional-grade portfolio monitoring and recommendations</p>
                    </div>
                    <button 
                        onClick={fetchPortfolio}
                        disabled={loading}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg font-semibold shadow-lg shadow-indigo-900/50 transition-all flex items-center gap-2 disabled:opacity-50"
                    >
                        <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
                        {loading ? 'Analyzing...' : 'Refresh Analysis'}
                    </button>
                </div>

                {error && (
                    <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg">
                        {error}
                    </div>
                )}

                {!loading && data && (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-6"
                    >
                        <PortfolioDashboard dashboard={data.dashboard} />
                        
                        <HoldingsTable holdings={data.holdings} />
                        
                        <AIInsightsPanel analysis={data} />

                    </motion.div>
                )}

                {loading && !data && (
                    <div className="flex items-center justify-center py-20">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
                    </div>
                )}
            </div>
        </div>
    );
}
