import React from 'react';
import { Database, DownloadCloud, HardDrive, ShieldCheck, AlertCircle, TrendingUp } from 'lucide-react';
import GlassCard from '../components/GlassCard';

function MetricCard({ title, value, subValue, icon: Icon, colorClass }) {
  return (
    <GlassCard className="p-4 flex flex-col gap-2">
      <div className="flex justify-between items-start">
        <span className="text-sm text-gray-400 font-medium">{title}</span>
        <div className={`p-2 rounded-lg ${colorClass} bg-opacity-10`}>
          <Icon size={18} className={colorClass.replace('bg-', 'text-')} />
        </div>
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        {subValue && <div className="text-xs text-gray-500 mt-1">{subValue}</div>}
      </div>
    </GlassCard>
  );
}

export default function DataIntelligence() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Database className="text-blue-500" /> Data Intelligence
          </h1>
          <p className="text-sm text-gray-400 mt-1">Monitoring Historical Data Lake (D1)</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard title="Health Score" value="98%" subValue="All systems operational" icon={ShieldCheck} colorClass="bg-green-500 text-green-500" />
        <MetricCard title="Universe" value="2,348" subValue="NSE Stocks Tracked" icon={Globe} colorClass="bg-blue-500 text-blue-500" />
        <MetricCard title="Coverage" value="99.7%" subValue="Data Completeness" icon={TrendingUp} colorClass="bg-purple-500 text-purple-500" />
        <MetricCard title="Storage" value="824 MB" subValue="Parquet Format" icon={HardDrive} colorClass="bg-yellow-500 text-yellow-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <DownloadCloud size={18} className="text-blue-400"/> Historical Download Status
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg border border-white/10">
              <span className="text-sm text-gray-300">Downloaded</span>
              <span className="font-mono text-green-400">2,344</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg border border-white/10">
              <span className="text-sm text-gray-300">Pending</span>
              <span className="font-mono text-yellow-400">4</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg border border-white/10">
              <span className="text-sm text-gray-300">Failed / Retries</span>
              <span className="font-mono text-red-400">0 / 0</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg border border-white/10">
              <span className="text-sm text-gray-300">Primary Provider</span>
              <span className="font-mono text-blue-400">Yahoo Finance</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-5">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Database size={18} className="text-purple-400"/> Storage Systems
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-white/5 rounded-lg border border-white/10">
              <div className="text-sm text-gray-400 mb-1">Parquet Files</div>
              <div className="text-xl font-bold text-white">2,344</div>
              <div className="text-xs text-green-400 mt-1 flex items-center gap-1"><ShieldCheck size={12}/> Synced</div>
            </div>
            <div className="p-4 bg-white/5 rounded-lg border border-white/10">
              <div className="text-sm text-gray-400 mb-1">SQLite DB</div>
              <div className="text-xl font-bold text-white">Healthy</div>
              <div className="text-xs text-green-400 mt-1 flex items-center gap-1"><ShieldCheck size={12}/> Connected</div>
            </div>
            <div className="p-4 bg-white/5 rounded-lg border border-white/10">
              <div className="text-sm text-gray-400 mb-1">S3 Sync</div>
              <div className="text-xl font-bold text-white">Pending</div>
              <div className="text-xs text-yellow-400 mt-1 flex items-center gap-1"><AlertCircle size={12}/> Scheduled</div>
            </div>
            <div className="p-4 bg-white/5 rounded-lg border border-white/10">
              <div className="text-sm text-gray-400 mb-1">Metadata DB</div>
              <div className="text-xl font-bold text-white">Healthy</div>
              <div className="text-xs text-green-400 mt-1 flex items-center gap-1"><ShieldCheck size={12}/> Updated Today</div>
            </div>
          </div>
        </GlassCard>
      </div>

      <GlassCard className="p-5 h-64 flex items-center justify-center">
        <div className="text-center">
          <TrendingUp className="mx-auto text-gray-500 mb-2 opacity-50" size={32} />
          <p className="text-gray-400">Storage Growth & Quality Charts will render here</p>
          <p className="text-xs text-gray-500 mt-1">Awaiting real data integration</p>
        </div>
      </GlassCard>
    </div>
  );
}

const Globe = ({size, className}) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
);
