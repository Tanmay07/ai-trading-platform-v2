import React, { useState } from 'react';
import { Sparkles, X } from 'lucide-react';

export default function AIInsightsDrawer() {
  const [isOpen, setIsOpen] = useState(false);

  const insights = [
    "BEL has highest breakout probability today.",
    "Portfolio overexposed to Banking.",
    "Consider reducing HDFC by 12%.",
    "Market Breadth improving.",
    "Momentum stocks outperforming.",
    "Weekly Target achievable using only 3 positions.",
    "Risk currently below normal.",
    "Historical probability of success 86%."
  ];

  return (
    <>
      {/* Floating Action Button */}
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-40 btn btn-primary rounded-full shadow-xl shadow-[rgba(88,166,255,0.3)] hover:scale-105 transition-transform flex items-center gap-2 pr-5"
      >
        <Sparkles size={18} />
        ✨ AI Insights
      </button>

      {/* Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 animate-fade-in"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Drawer */}
      <div 
        className={`fixed top-0 right-0 h-full w-80 bg-[var(--bg-surface-elevated)] border-l border-[var(--glass-border)] shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : 'translate-x-full'} flex flex-col`}
      >
        <div className="p-5 border-b border-[var(--glass-border)] flex justify-between items-center bg-[rgba(88,166,255,0.05)]">
          <h2 className="text-lg font-bold flex items-center gap-2 text-[var(--accent-primary)]">
            <Sparkles size={20} /> Today's Insights
          </h2>
          <button 
            onClick={() => setIsOpen(false)}
            className="text-[var(--text-secondary)] hover:text-white transition-colors p-1"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {insights.map((insight, idx) => (
            <div key={idx} className="glass-panel p-4 text-sm text-[#cbd5e1] border-l-[3px] border-l-[var(--accent-primary)] hover:translate-y-[-2px] hover:shadow-md transition-all">
              {insight}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
