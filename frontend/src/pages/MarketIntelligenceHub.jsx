import React, { useState } from 'react';
import { Globe, Rss, Factory, TrendingUp, AlertTriangle, Newspaper } from 'lucide-react';
import GlassCard from '../components/GlassCard';

function NewsItem({ title, source, sentiment, impact, company }) {
  const sentimentColor = sentiment > 0 ? 'text-green-400' : sentiment < 0 ? 'text-red-400' : 'text-gray-400';
  
  return (
    <div className="p-4 bg-white/5 rounded-lg border border-white/10 flex flex-col gap-2 hover:bg-white/10 transition-colors cursor-pointer">
      <div className="flex justify-between items-start gap-4">
        <h4 className="text-white font-medium text-sm leading-snug">{title}</h4>
        <span className={`text-xs font-bold px-2 py-1 rounded bg-black/30 ${sentimentColor}`}>
          {sentiment > 0 ? '+' : ''}{sentiment}
        </span>
      </div>
      <div className="flex items-center gap-3 text-xs text-gray-500">
        <span className="text-blue-400 font-semibold">{company}</span>
        <span>•</span>
        <span>{source}</span>
        <span>•</span>
        <span className="flex items-center gap-1"><AlertTriangle size={12} className={impact > 70 ? 'text-yellow-400' : 'text-gray-500'} /> Impact: {impact}</span>
      </div>
    </div>
  );
}

export default function MarketIntelligenceHub() {
  const [activeTab, setActiveTab] = useState('news');
  
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Globe className="text-blue-400" /> Market Intelligence Hub
          </h1>
          <p className="text-sm text-gray-400 mt-1">Real-time NLP News, Sentiment, and Corporate Actions (D4)</p>
        </div>
      </div>

      <div className="flex gap-4 border-b border-white/10 pb-2">
        <button onClick={() => setActiveTab('news')} className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'news' ? 'bg-blue-500/20 text-blue-400' : 'text-gray-400 hover:text-gray-200'}`}>News Sentiment</button>
        <button onClick={() => setActiveTab('corporate')} className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'corporate' ? 'bg-purple-500/20 text-purple-400' : 'text-gray-400 hover:text-gray-200'}`}>Corporate Actions</button>
        <button onClick={() => setActiveTab('sectors')} className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'sectors' ? 'bg-green-500/20 text-green-400' : 'text-gray-400 hover:text-gray-200'}`}>Sector Rotation</button>
      </div>

      {activeTab === 'news' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2"><Rss size={18}/> Latest Processed Feed</h2>
            <div className="space-y-3">
              <NewsItem title="Reliance Industries secures massive offshore drilling contract" source="Reuters" sentiment={85} impact={92} company="RELIANCE.NS" />
              <NewsItem title="TCS reports margin pressure due to wage hikes in Q3" source="Bloomberg" sentiment={-45} impact={78} company="TCS.NS" />
              <NewsItem title="HDFC Bank credit growth stabilizes, asset quality remains strong" source="Mint" sentiment={60} impact={65} company="HDFCBANK.NS" />
              <NewsItem title="Tata Motors EV sales drop by 12% MoM" source="MoneyControl" sentiment={-65} impact={80} company="TATAMOTORS.NS" />
            </div>
          </div>
          
          <div className="space-y-6">
            <GlassCard className="p-5">
              <h3 className="text-md font-semibold text-white mb-3">Trending Companies</h3>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30">RELIANCE (+85)</span>
                <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-xs border border-red-500/30">TATAMOTORS (-65)</span>
                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30">HDFCBANK (+60)</span>
                <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-xs border border-red-500/30">TCS (-45)</span>
              </div>
            </GlassCard>
            
            <GlassCard className="p-5">
              <h3 className="text-md font-semibold text-white mb-3">NLP Pipeline Status</h3>
              <div className="space-y-2 text-sm text-gray-400">
                <div className="flex justify-between"><span>Articles Ingested Today:</span> <span className="text-white font-mono">1,402</span></div>
                <div className="flex justify-between"><span>Deduplicated:</span> <span className="text-white font-mono">312</span></div>
                <div className="flex justify-between"><span>Tagged Companies:</span> <span className="text-white font-mono">84</span></div>
                <div className="flex justify-between"><span>FinBERT Inferences:</span> <span className="text-white font-mono">1,090</span></div>
              </div>
            </GlassCard>
          </div>
        </div>
      )}
      
      {activeTab !== 'news' && (
        <GlassCard className="p-10 flex flex-col items-center justify-center text-center">
          <Factory className="text-gray-500 mb-4 opacity-50" size={48} />
          <h2 className="text-xl font-bold text-white mb-2">Module Under Construction</h2>
          <p className="text-gray-400 max-w-md">The {activeTab} view is currently being integrated with the D4 Market Intelligence pipeline.</p>
        </GlassCard>
      )}

    </div>
  );
}
