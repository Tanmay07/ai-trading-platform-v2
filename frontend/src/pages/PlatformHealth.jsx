import React from 'react';
import { ActivitySquare, Database, Server, Cpu, Globe, Zap, Network, ShieldCheck } from 'lucide-react';
import GlassCard from '../components/GlassCard';

function HealthItem({ label, status }) {
  const isHealthy = status === 'Healthy';
  return (
    <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg border border-white/10">
      <span className="text-sm text-gray-300 font-medium">{label}</span>
      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${isHealthy ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'}`}>
        <div className={`w-1.5 h-1.5 rounded-full ${isHealthy ? 'bg-green-400' : 'bg-yellow-400'}`}></div>
        {status}
      </div>
    </div>
  );
}

export default function PlatformHealth() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <ActivitySquare className="text-green-500" /> Platform Mission Control
          </h1>
          <p className="text-sm text-gray-400 mt-1">Monitoring the health of all AI trading infrastructure.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Core Infrastructure */}
        <GlassCard className="p-5">
          <h2 className="text-md font-semibold text-white mb-4 flex items-center gap-2">
            <Server size={18} className="text-blue-400"/> Core Infrastructure
          </h2>
          <div className="space-y-3">
            <HealthItem label="Historical Data Platform" status="Healthy" />
            <HealthItem label="Market Data Engine" status="Healthy" />
            <HealthItem label="Feature Store" status="Healthy" />
            <HealthItem label="Prediction Engine" status="Healthy" />
            <HealthItem label="News Intelligence" status="Healthy" />
          </div>
        </GlassCard>

        {/* Database & Caching */}
        <GlassCard className="p-5">
          <h2 className="text-md font-semibold text-white mb-4 flex items-center gap-2">
            <Database size={18} className="text-purple-400"/> Databases & Cache
          </h2>
          <div className="space-y-3">
            <HealthItem label="Redis Intraday Cache" status="Healthy" />
            <HealthItem label="PostgreSQL (App DB)" status="Healthy" />
            <HealthItem label="SQLite (Market DB)" status="Healthy" />
            <HealthItem label="SQLite (Feedback DB)" status="Healthy" />
            <HealthItem label="AWS S3 Backup" status="Pending Sync" />
          </div>
        </GlassCard>

        {/* Provider Usage */}
        <GlassCard className="p-5">
          <h2 className="text-md font-semibold text-white mb-4 flex items-center gap-2">
            <Network size={18} className="text-pink-400"/> Provider API Usage
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg border border-white/10">
              <span className="text-sm text-gray-300">Yahoo Finance</span>
              <span className="font-mono text-blue-400">42 Calls</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg border border-white/10">
              <span className="text-sm text-gray-300">NSE / Jugaad</span>
              <span className="font-mono text-purple-400">8 Calls</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg border border-white/10">
              <span className="text-sm text-gray-300">RSS Feeds</span>
              <span className="font-mono text-orange-400">12 Calls</span>
            </div>
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Redis Cache Hit Rate</span>
                <span className="font-bold text-green-400">93.4%</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-1.5 mt-2">
                <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '93.4%' }}></div>
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      <GlassCard className="p-5 h-48 flex items-center justify-center">
        <div className="text-center">
          <Zap className="mx-auto text-gray-500 mb-2 opacity-50" size={32} />
          <p className="text-gray-400">API Consumption & Hourly Rate Limits Chart</p>
          <p className="text-xs text-gray-500 mt-1">Integration pending</p>
        </div>
      </GlassCard>
    </div>
  );
}
