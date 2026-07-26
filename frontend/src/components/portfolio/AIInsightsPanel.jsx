import React from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, AlertTriangle, ArrowRight } from 'lucide-react';

export default function AIInsightsPanel({ analysis }) {
    if (!analysis) return null;

    const { opportunities, alerts } = analysis;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            {/* AI Portfolio Review / Opportunities */}
            <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-sm"
            >
                <div className="flex items-center gap-2 mb-4 border-b border-gray-700 pb-3">
                    <Lightbulb className="text-yellow-400" size={20}/>
                    <h3 className="text-lg font-bold text-white">Opportunity Scanner</h3>
                </div>
                
                {opportunities && opportunities.length > 0 ? (
                    <div className="space-y-4">
                        {opportunities.map((opp, idx) => (
                            <div key={idx} className="bg-gray-700/30 p-4 rounded-lg border border-gray-600/50">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="text-red-400 font-semibold">{opp.replace}</span>
                                    <ArrowRight size={16} className="text-gray-400"/>
                                    <span className="text-green-400 font-semibold">{opp.consider}</span>
                                </div>
                                <p className="text-sm text-gray-300 mb-2">
                                    {opp.reason}
                                </p>
                                <div className="text-xs font-medium text-blue-400">
                                    Expected Return Difference: {opp.expected_return_diff}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-gray-400 text-sm">No new opportunities identified at this time.</p>
                )}
            </motion.div>

            {/* Dynamic Alerts */}
            <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-sm"
            >
                <div className="flex items-center gap-2 mb-4 border-b border-gray-700 pb-3">
                    <AlertTriangle className="text-orange-400" size={20}/>
                    <h3 className="text-lg font-bold text-white">Dynamic Price Alerts</h3>
                </div>
                
                {alerts && alerts.length > 0 ? (
                    <div className="space-y-3">
                        {alerts.map((alert, idx) => (
                            <div key={idx} className={`p-3 rounded-lg border flex items-start gap-3 ${
                                alert.type === 'warning' ? 'bg-orange-500/10 border-orange-500/30 text-orange-200' :
                                alert.type === 'success' ? 'bg-green-500/10 border-green-500/30 text-green-200' :
                                'bg-blue-500/10 border-blue-500/30 text-blue-200'
                            }`}>
                                <div className="mt-0.5">
                                    <div className={`w-2 h-2 rounded-full ${
                                        alert.type === 'warning' ? 'bg-orange-400' :
                                        alert.type === 'success' ? 'bg-green-400' :
                                        'bg-blue-400'
                                    }`}></div>
                                </div>
                                <p className="text-sm">{alert.message}</p>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-gray-400 text-sm">No new alerts generated today.</p>
                )}
            </motion.div>
        </div>
    );
}
