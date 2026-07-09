import React from 'react';
import { BrainCircuit, Cpu, Zap, Target, LineChart, Table2, LayoutList } from 'lucide-react';
import GlassCard from '../components/GlassCard';

function ModelCard({ title, type, accuracy, winRate, precision, recall }) {
  return (
    <div className="p-4 bg-white/5 rounded-lg border border-white/10 flex flex-col gap-3">
      <div className="flex justify-between items-center">
        <h3 className="text-white font-semibold">{title}</h3>
        <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full">{type}</span>
      </div>
      <div className="grid grid-cols-2 gap-4 mt-2">
        <div>
          <div className="text-xs text-gray-500">Accuracy</div>
          <div className="text-lg font-bold text-green-400">{accuracy}%</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">Win Rate</div>
          <div className="text-lg font-bold text-green-400">{winRate}%</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">Precision</div>
          <div className="text-sm font-medium text-gray-300">{precision}%</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">Recall</div>
          <div className="text-sm font-medium text-gray-300">{recall}%</div>
        </div>
      </div>
    </div>
  );
}

export default function ModelIntelligence() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <BrainCircuit className="text-purple-500" /> Model Intelligence
          </h1>
          <p className="text-sm text-gray-400 mt-1">Feature Store & Prediction Models (D2)</p>
        </div>
        <div className="px-3 py-1 bg-green-500/10 border border-green-500/20 text-green-400 rounded-lg text-sm font-medium flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
          Meta Ensemble v8.4 Active
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassCard className="p-4 flex flex-col items-center justify-center text-center">
          <DatabaseIcon className="text-gray-400 mb-2" size={24} />
          <div className="text-2xl font-bold text-white">148</div>
          <div className="text-xs text-gray-500 mt-1">Engineered Features</div>
        </GlassCard>
        <GlassCard className="p-4 flex flex-col items-center justify-center text-center">
          <Cpu className="text-purple-400 mb-2" size={24} />
          <div className="text-2xl font-bold text-white">5</div>
          <div className="text-xs text-gray-500 mt-1">Active Models</div>
        </GlassCard>
        <GlassCard className="p-4 flex flex-col items-center justify-center text-center">
          <Target className="text-green-400 mb-2" size={24} />
          <div className="text-2xl font-bold text-white">74.2%</div>
          <div className="text-xs text-gray-500 mt-1">Ensemble Accuracy</div>
        </GlassCard>
        <GlassCard className="p-4 flex flex-col items-center justify-center text-center">
          <Zap className="text-yellow-400 mb-2" size={24} />
          <div className="text-lg font-bold text-white">Yesterday, 23:00</div>
          <div className="text-xs text-gray-500 mt-1">Last Training Run</div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard className="p-5 col-span-2">
          <h2 className="text-lg font-semibold text-white mb-4">Model Registry</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ModelCard title="XGBoost Classifier" type="Tree" accuracy="72.4" winRate="69.1" precision="68" recall="74" />
            <ModelCard title="LightGBM Classifier" type="Tree" accuracy="73.1" winRate="70.5" precision="71" recall="72" />
            <ModelCard title="CatBoost Classifier" type="Tree" accuracy="71.8" winRate="68.9" precision="70" recall="70" />
            <ModelCard title="Meta Ensemble" type="Apex" accuracy="74.2" winRate="72.0" precision="73" recall="75" />
          </div>
        </GlassCard>

        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-white mb-4">Top 5 Feature Importances</h2>
          <div className="space-y-4">
            {['RSI_14', 'Relative_Volume_5d', 'FinBERT_Sentiment', 'MACD_Hist', 'ATR_Pct'].map((feature, idx) => (
              <div key={feature}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">{feature}</span>
                  <span className="text-gray-500">{100 - (idx * 15)}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${100 - (idx * 15)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <GlassCard className="p-5 h-64 flex flex-col">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <LineChart size={18} className="text-blue-400" /> Training Loss / Accuracy Curve
          </h2>
          <div className="flex-1 flex items-center justify-center border border-white/5 bg-white/5 rounded-lg border-dashed">
            <span className="text-gray-500 text-sm">Chart rendering pending ML integration</span>
          </div>
        </GlassCard>
        
        <GlassCard className="p-5 h-64 flex flex-col">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Table2 size={18} className="text-green-400" /> Confusion Matrix (Meta Ensemble)
          </h2>
          <div className="flex-1 flex items-center justify-center border border-white/5 bg-white/5 rounded-lg border-dashed">
            <span className="text-gray-500 text-sm">Heatmap rendering pending ML integration</span>
          </div>
        </GlassCard>
      </div>

    </div>
  );
}

const DatabaseIcon = ({size, className}) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
);
