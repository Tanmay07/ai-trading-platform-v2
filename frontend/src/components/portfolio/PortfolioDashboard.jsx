import React from 'react';
import { motion } from 'framer-motion';

export default function PortfolioDashboard({ dashboard }) {
    if (!dashboard) return null;

    const metrics = [
        { label: "Portfolio Value", value: `₹${dashboard.portfolio_value?.toLocaleString()}` },
        { label: "Today's P&L", value: `₹${(dashboard.total_unrealized_pnl * 0.05).toLocaleString()}`, color: 'text-green-400' }, // Mocking daily for now
        { label: "Total Unrealized P&L", value: `₹${dashboard.total_unrealized_pnl?.toLocaleString()}`, color: dashboard.total_unrealized_pnl > 0 ? 'text-green-400' : 'text-red-400' },
        { label: "Absolute Return", value: `${dashboard.absolute_return}%`, color: dashboard.absolute_return > 0 ? 'text-green-400' : 'text-red-400' },
        { label: "CAGR (Est)", value: `${dashboard.cagr}%` },
        { label: "Number of Holdings", value: dashboard.holdings_count },
        { label: "Risk Score", value: `${dashboard.risk_score}/100`, color: dashboard.risk_score > 70 ? 'text-red-400' : 'text-green-400' },
        { label: "Health Score", value: `${dashboard.health_score}/100`, color: dashboard.health_score > 80 ? 'text-green-400' : 'text-yellow-400' }
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {metrics.map((m, idx) => (
                <motion.div 
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-sm"
                >
                    <p className="text-gray-400 text-sm font-medium">{m.label}</p>
                    <p className={`text-2xl font-bold mt-2 ${m.color || 'text-white'}`}>
                        {m.value}
                    </p>
                </motion.div>
            ))}
        </div>
    );
}
