import React from 'react';
import { TrendingUp, Target, ShieldAlert, Clock, CheckCircle2, XCircle } from 'lucide-react';
import GlassCard from '../components/GlassCard';

function PredictionRow({ symbol, action, confidence, holding, target, currentReturn, prob, status }) {
  const getStatusIcon = () => {
    switch (status) {
      case 'Win': return <CheckCircle2 size={16} className="text-green-400" />;
      case 'Loss': return <XCircle size={16} className="text-red-400" />;
      case 'Active': return <TrendingUp size={16} className="text-blue-400" />;
      default: return <Clock size={16} className="text-gray-400" />;
    }
  };

  return (
    <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
      <td className="py-3 px-4 font-medium text-white">{symbol}</td>
      <td className="py-3 px-4">
        <span className={`text-xs px-2 py-1 rounded font-bold ${action === 'BUY' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
          {action}
        </span>
      </td>
      <td className="py-3 px-4 text-gray-300">{confidence}%</td>
      <td className="py-3 px-4 text-gray-400">{holding}d</td>
      <td className="py-3 px-4 text-gray-300">₹{target}</td>
      <td className={`py-3 px-4 font-semibold ${currentReturn > 0 ? 'text-green-400' : 'text-red-400'}`}>
        {currentReturn > 0 ? '+' : ''}{currentReturn}%
      </td>
      <td className="py-3 px-4">
        <div className="w-16 bg-gray-800 rounded-full h-1.5 inline-block mr-2">
          <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${prob}%` }}></div>
        </div>
        <span className="text-xs text-gray-400">{prob}%</span>
      </td>
      <td className="py-3 px-4 flex items-center gap-1 text-sm text-gray-300">
        {getStatusIcon()} {status}
      </td>
    </tr>
  );
}

export default function PredictionIntelligence() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="text-green-400" /> Prediction Intelligence
          </h1>
          <p className="text-sm text-gray-400 mt-1">Lifecycle Tracking & Outcome Evaluation (D6)</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <GlassCard className="p-4 text-center">
          <div className="text-xl font-bold text-white">4,217</div>
          <div className="text-xs text-gray-500 mt-1">Total Predictions</div>
        </GlassCard>
        <GlassCard className="p-4 text-center border border-green-500/30">
          <div className="text-xl font-bold text-green-400">71%</div>
          <div className="text-xs text-gray-500 mt-1">Win Rate</div>
        </GlassCard>
        <GlassCard className="p-4 text-center">
          <div className="text-xl font-bold text-white">63%</div>
          <div className="text-xs text-gray-500 mt-1">Target Hits</div>
        </GlassCard>
        <GlassCard className="p-4 text-center">
          <div className="text-xl font-bold text-white">19%</div>
          <div className="text-xs text-gray-500 mt-1">Stop Losses</div>
        </GlassCard>
        <GlassCard className="p-4 text-center">
          <div className="text-xl font-bold text-green-400">+6.4%</div>
          <div className="text-xs text-gray-500 mt-1">Avg Return</div>
        </GlassCard>
        <GlassCard className="p-4 text-center">
          <div className="text-xl font-bold text-white">5.8 Days</div>
          <div className="text-xs text-gray-500 mt-1">Avg Holding</div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="p-5 lg:col-span-2">
          <h2 className="text-lg font-semibold text-white mb-4">Active & Evaluated Predictions</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-gray-400 border-b border-white/10 uppercase text-xs">
                <tr>
                  <th className="py-2 px-4">Symbol</th>
                  <th className="py-2 px-4">Action</th>
                  <th className="py-2 px-4">Conf.</th>
                  <th className="py-2 px-4">Hold</th>
                  <th className="py-2 px-4">Target</th>
                  <th className="py-2 px-4">Return</th>
                  <th className="py-2 px-4">Prob.</th>
                  <th className="py-2 px-4">Status</th>
                </tr>
              </thead>
              <tbody>
                <PredictionRow symbol="BEL" action="BUY" confidence={94} holding={2} target={310} currentReturn={4.2} prob={89} status="Active" />
                <PredictionRow symbol="TCS" action="BUY" confidence={88} holding={7} target={4150} currentReturn={6.8} prob={78} status="Win" />
                <PredictionRow symbol="HDFCBANK" action="SELL" confidence={82} holding={4} target={1420} currentReturn={-2.1} prob={75} status="Loss" />
                <PredictionRow symbol="TATAMOTORS" action="BUY" confidence={91} holding={1} target={980} currentReturn={0.5} prob={84} status="Active" />
                <PredictionRow symbol="RELIANCE" action="BUY" confidence={95} holding={6} target={3050} currentReturn={8.2} prob={91} status="Win" />
              </tbody>
            </table>
          </div>
        </GlassCard>

        <div className="space-y-6">
          <GlassCard className="p-5">
            <h3 className="text-md font-semibold text-white mb-3">Lifecycle Pipeline</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3"><div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs">1</div><span className="text-gray-300 text-sm">Generated (42)</span></div>
              <div className="flex items-center gap-3"><div className="w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center text-xs">2</div><span className="text-gray-300 text-sm">Active (15)</span></div>
              <div className="flex items-center gap-3"><div className="w-6 h-6 rounded-full bg-yellow-500/20 text-yellow-400 flex items-center justify-center text-xs">3</div><span className="text-gray-300 text-sm">Completed (27)</span></div>
              <div className="flex items-center gap-3"><div className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs">4</div><span className="text-gray-300 text-sm">Evaluated (4,217)</span></div>
              <div className="flex items-center gap-3"><div className="w-6 h-6 rounded-full bg-gray-500/20 text-gray-400 flex items-center justify-center text-xs">5</div><span className="text-gray-300 text-sm">Learning DB (4,217)</span></div>
            </div>
          </GlassCard>
          
          <GlassCard className="p-5">
            <h3 className="text-md font-semibold text-white mb-3 flex items-center gap-2"><Target size={16} className="text-purple-400" /> Confidence Calibration</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between text-gray-400"><span>90-100% Bucket</span><span className="text-green-400">89% Actual</span></div>
              <div className="flex justify-between text-gray-400"><span>80-90% Bucket</span><span className="text-yellow-400">76% Actual</span></div>
              <div className="flex justify-between text-gray-400"><span>70-80% Bucket</span><span className="text-red-400">58% Actual</span></div>
            </div>
            <p className="text-xs text-gray-500 mt-4 leading-relaxed">
              *The Meta Decision engine uses Isotonic Regression to map raw model probabilities to these actual historical win-rates.
            </p>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
