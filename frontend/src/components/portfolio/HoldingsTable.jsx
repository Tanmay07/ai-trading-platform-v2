import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronUp, Plus, Edit2, Trash2 } from 'lucide-react';

export default function HoldingsTable({ holdings }) {
    const [expandedRow, setExpandedRow] = useState(null);

    if (!holdings || holdings.length === 0) return <div className="text-gray-400">No holdings found.</div>;

    const getRecColor = (rec) => {
        if (!rec) return 'text-gray-400';
        if (rec.includes('Buy')) return 'text-green-400 bg-green-400/10';
        if (rec.includes('Hold') || rec.includes('Accumulate')) return 'text-yellow-400 bg-yellow-400/10';
        return 'text-red-400 bg-red-400/10';
    };

    return (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden shadow-sm mt-8">
            <div className="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-800/50">
                <h2 className="text-xl font-bold text-white">Portfolio Holdings</h2>
                <div className="flex gap-2">
                    <button className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-1.5 rounded flex items-center gap-1 text-sm">
                        <Plus size={16}/> Add Holding
                    </button>
                </div>
            </div>
            
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead className="bg-gray-900/50 text-gray-400 uppercase text-xs">
                        <tr>
                            <th className="px-4 py-3 font-medium">Symbol</th>
                            <th className="px-4 py-3 font-medium text-right">Qty</th>
                            <th className="px-4 py-3 font-medium text-right">Avg Price</th>
                            <th className="px-4 py-3 font-medium text-right">Current</th>
                            <th className="px-4 py-3 font-medium text-right">Unrealized P&L</th>
                            <th className="px-4 py-3 font-medium text-right">Weight %</th>
                            <th className="px-4 py-3 font-medium text-center">Recommendation</th>
                            <th className="px-4 py-3 font-medium text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                        {holdings.map((h, idx) => {
                            const isExpanded = expandedRow === idx;
                            const rec = h.recommendation?.recommendation || 'N/A';
                            
                            return (
                                <React.Fragment key={idx}>
                                    <tr className="hover:bg-gray-700/30 transition-colors">
                                        <td className="px-4 py-4 font-medium text-blue-400 cursor-pointer" onClick={() => setExpandedRow(isExpanded ? null : idx)}>
                                            <div className="flex items-center gap-2">
                                                {h.symbol}
                                                {isExpanded ? <ChevronUp size={14}/> : <ChevronDown size={14}/>}
                                            </div>
                                            <div className="text-xs text-gray-500 font-normal">{h.sector}</div>
                                        </td>
                                        <td className="px-4 py-4 text-right text-gray-300">{h.quantity}</td>
                                        <td className="px-4 py-4 text-right text-gray-300">₹{h.avg_buy_price?.toFixed(2)}</td>
                                        <td className="px-4 py-4 text-right text-white">₹{h.current_price?.toFixed(2)}</td>
                                        <td className={`px-4 py-4 text-right font-medium ${h.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                            ₹{h.unrealized_pnl?.toFixed(2)} <br/>
                                            <span className="text-xs">({h.unrealized_pnl_pct?.toFixed(2)}%)</span>
                                        </td>
                                        <td className="px-4 py-4 text-right text-gray-300">{h.weight}%</td>
                                        <td className="px-4 py-4 text-center">
                                            <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${getRecColor(rec)}`}>
                                                {rec}
                                            </span>
                                        </td>
                                        <td className="px-4 py-4">
                                            <div className="flex justify-center gap-2 text-gray-400">
                                                <button className="hover:text-white"><Edit2 size={16}/></button>
                                                <button className="hover:text-red-400"><Trash2 size={16}/></button>
                                            </div>
                                        </td>
                                    </tr>
                                    
                                    {isExpanded && (
                                        <tr className="bg-gray-900/40">
                                            <td colSpan={8} className="px-6 py-4">
                                                <div className="grid grid-cols-3 gap-6 text-sm">
                                                    <div>
                                                        <h4 className="font-semibold text-gray-300 mb-2 border-b border-gray-700 pb-1">AI Reasoning</h4>
                                                        <p className="text-gray-400 italic mb-3">"{h.recommendation?.reasoning}"</p>
                                                        <div className="flex gap-4">
                                                            <div>
                                                                <span className="text-gray-500 block text-xs">Target Price</span>
                                                                <span className="text-green-400 font-medium">₹{h.recommendation?.target_price}</span>
                                                            </div>
                                                            <div>
                                                                <span className="text-gray-500 block text-xs">Stop Loss</span>
                                                                <span className="text-red-400 font-medium">₹{h.recommendation?.stop_loss}</span>
                                                            </div>
                                                            <div>
                                                                <span className="text-gray-500 block text-xs">Confidence</span>
                                                                <span className="text-blue-400 font-medium">{h.recommendation?.confidence}%</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div>
                                                        <h4 className="font-semibold text-gray-300 mb-2 border-b border-gray-700 pb-1">Fundamentals</h4>
                                                        <div className="grid grid-cols-2 gap-2 text-xs">
                                                            <div className="text-gray-500">Score: <span className="text-white">{h.fundamental_analysis?.fundamental_score}</span></div>
                                                            <div className="text-gray-500">Rev Growth: <span className="text-white">{h.fundamental_analysis?.revenue_growth}%</span></div>
                                                            <div className="text-gray-500">ROE: <span className="text-white">{h.fundamental_analysis?.roe}%</span></div>
                                                            <div className="text-gray-500">PE: <span className="text-white">{h.fundamental_analysis?.pe}x</span></div>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <h4 className="font-semibold text-gray-300 mb-2 border-b border-gray-700 pb-1">Technicals</h4>
                                                        <div className="grid grid-cols-2 gap-2 text-xs">
                                                            <div className="text-gray-500">Score: <span className="text-white">{h.technical_analysis?.technical_score}</span></div>
                                                            <div className="text-gray-500">Trend: <span className="text-white">{h.technical_analysis?.trend}</span></div>
                                                            <div className="text-gray-500">RSI: <span className="text-white">{h.technical_analysis?.rsi}</span></div>
                                                            <div className="text-gray-500">Support: <span className="text-white">₹{h.technical_analysis?.support}</span></div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            )
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
