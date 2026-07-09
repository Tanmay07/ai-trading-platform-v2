import React from 'react';
import { Database, GitCommit, RefreshCcw, ArrowRight } from 'lucide-react';
import GlassCard from '../components/GlassCard';

export default function ContinuousLearning() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <RefreshCcw className="text-blue-500" /> Continuous Learning
          </h1>
          <p className="text-sm text-gray-400 mt-1">Feedback Loops & Retraining Pipeline (D6 -> D2)</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <GlassCard className="p-4 text-center">
          <div className="text-2xl font-bold text-white">12,450</div>
          <div className="text-xs text-gray-500 mt-1">Feedback Records</div>
        </GlassCard>
        <GlassCard className="p-4 text-center border border-yellow-500/30">
          <div className="text-2xl font-bold text-yellow-400">148</div>
          <div className="text-xs text-gray-500 mt-1">In Retraining Queue</div>
        </GlassCard>
        <GlassCard className="p-4 text-center">
          <div className="text-2xl font-bold text-green-400">None</div>
          <div className="text-xs text-gray-500 mt-1">Feature Drift</div>
        </GlassCard>
        <GlassCard className="p-4 text-center">
          <div className="text-xl font-bold text-blue-400">+2.4%</div>
          <div className="text-xs text-gray-500 mt-1">Calibration Improv.</div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Database size={18} className="text-purple-400"/> Recent Analyzed Learnings</h2>
          <div className="space-y-4">
            <div className="p-3 bg-white/5 border border-white/10 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-semibold text-white">IT Sector Reversal Patterns</span>
                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">Success</span>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed">
                The ensemble identified strong momentum divergence in TCS and INFY. Evaluated predictions showed an 84% win rate when FinBERT sentiment &gt; 60 alongside RSI &lt; 40.
              </p>
            </div>
            
            <div className="p-3 bg-white/5 border border-white/10 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-semibold text-white">PSU Bank False Breakouts</span>
                <span className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded">Failure</span>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed">
                Recent 14 predictions in PSU Banks hit stop-loss within 2 days. Feature drift detected in `Relative_Volume_5d`. Recommendation: Downweight volume signals for this sector in current regime.
              </p>
            </div>
          </div>
        </GlassCard>

        <div className="space-y-6">
          <GlassCard className="p-5">
            <h2 className="text-lg font-semibold text-white mb-4">Feature Effectiveness Drift</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">MACD_Hist</span>
                <span className="text-green-400 flex items-center gap-1">+12% Alpha <TrendingUp size={12}/></span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">FinBERT_Sentiment</span>
                <span className="text-green-400 flex items-center gap-1">+8% Alpha <TrendingUp size={12}/></span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-300">SMA_200_Cross</span>
                <span className="text-red-400 flex items-center gap-1">-14% Alpha <TrendingUp size={12} className="rotate-180"/></span>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="p-5">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><GitCommit size={18} className="text-blue-400"/> Model Evolution</h2>
            <div className="flex items-center justify-between">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-gray-800 border border-gray-600 flex items-center justify-center text-gray-400 font-mono text-sm mx-auto mb-2">v7</div>
                <div className="text-xs text-gray-500">68% Acc</div>
              </div>
              <ArrowRight className="text-gray-600" />
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-gray-800 border border-purple-500/50 flex items-center justify-center text-purple-400 font-mono text-sm mx-auto mb-2">v8</div>
                <div className="text-xs text-gray-500">72% Acc</div>
              </div>
              <ArrowRight className="text-gray-600" />
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-blue-500/20 border border-blue-500 flex items-center justify-center text-blue-400 font-mono font-bold text-sm mx-auto mb-2 relative">
                  v8.4
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-[#121212]"></div>
                </div>
                <div className="text-xs text-green-400 font-bold">74% Acc</div>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
